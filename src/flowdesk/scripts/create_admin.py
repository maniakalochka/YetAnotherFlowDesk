import argparse
import asyncio
import enum
import getpass
import os
import sys
from collections.abc import Sequence

from pydantic import ValidationError

from flowdesk.core.security import password_hasher
from flowdesk.modules.users.exceptions import UserAlreadyExistsError
from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.schemas import UserRegisterSchema

ADMIN_PASSWORD_ENV = "FLOWDESK_ADMIN_PASSWORD"  # noqa: S105


class AdminProvisionStatus(enum.StrEnum):
    CREATED = "created"
    ALREADY_ADMIN = "already_admin"
    PROMOTED = "promoted"


class ExistingUserNotAdminError(Exception):
    pass


class PasswordConfirmationError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create the initial FlowDesk administrator. "
            f"The password is read from a hidden prompt or {ADMIN_PASSWORD_ENV}."
        )
    )
    parser.add_argument("--email", required=True, help="Administrator email address")
    parser.add_argument("--first-name", required=True, help="Administrator first name")
    parser.add_argument("--last-name", required=True, help="Administrator last name")
    parser.add_argument(
        "--promote-existing",
        action="store_true",
        help="Promote an existing non-admin user with the same email",
    )
    return parser


def read_password() -> str:
    password_from_environment = os.getenv(ADMIN_PASSWORD_ENV)
    if password_from_environment is not None:
        return password_from_environment

    password = getpass.getpass("Admin password: ")
    password_confirmation = getpass.getpass("Repeat admin password: ")
    if password != password_confirmation:
        raise PasswordConfirmationError("Passwords do not match")
    return password


async def ensure_admin(
    repository: UserRepository,
    data: UserRegisterSchema,
    *,
    promote_existing: bool = False,
) -> tuple[User, AdminProvisionStatus]:
    existing_user = await repository.get_by_email(data.email)
    if existing_user is not None:
        if existing_user.role is UserRole.ADMIN:
            return existing_user, AdminProvisionStatus.ALREADY_ADMIN
        if not promote_existing:
            raise ExistingUserNotAdminError(
                "A non-admin user with this email already exists. "
                "Use --promote-existing to promote this account."
            )

        existing_user.hashed_password = password_hasher.hash(data.password)
        existing_user.fname = data.fname
        existing_user.lname = data.lname
        existing_user.role = UserRole.ADMIN
        existing_user.is_active = True
        existing_user.is_verified = True
        promoted_user = await repository.save(existing_user)
        return promoted_user, AdminProvisionStatus.PROMOTED

    admin = User(
        email=data.email,
        hashed_password=password_hasher.hash(data.password),
        fname=data.fname,
        lname=data.lname,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    created_admin = await repository.create(admin)
    return created_admin, AdminProvisionStatus.CREATED


async def provision_admin(
    data: UserRegisterSchema,
    *,
    promote_existing: bool,
) -> tuple[User, AdminProvisionStatus]:
    from flowdesk.infrastructure.database.session import AsyncSessionLocal, engine

    try:
        async with AsyncSessionLocal() as session:
            repository = UserRepository(session)
            return await ensure_admin(
                repository,
                data,
                promote_existing=promote_existing,
            )
    finally:
        await engine.dispose()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        data = UserRegisterSchema(
            email=args.email,
            password=read_password(),
            fname=args.first_name,
            lname=args.last_name,
        )
        admin, result = asyncio.run(
            provision_admin(
                data,
                promote_existing=args.promote_existing,
            )
        )
    except (
        ExistingUserNotAdminError,
        PasswordConfirmationError,
        UserAlreadyExistsError,
        ValidationError,
    ) as error:
        print(f"Cannot create administrator: {error}", file=sys.stderr)
        return 1

    messages = {
        AdminProvisionStatus.CREATED: "Administrator created",
        AdminProvisionStatus.ALREADY_ADMIN: "Administrator already exists",
        AdminProvisionStatus.PROMOTED: "Existing user promoted to administrator",
    }
    print(f"{messages[result]}: {admin.email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
