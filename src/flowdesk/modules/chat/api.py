import json
import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from flowdesk.dependencies.chat import TicketChatServiceDep
from flowdesk.dependencies.ticket import TicketServiceDep, WsTicketDep
from flowdesk.dependencies.user import CurrentUserDep, WsCurrentUserDep
from flowdesk.modules.chat.manager import manager
from flowdesk.modules.chat.schemas import (
    TicketChatMessageCreateSchema,
    TicketChatMessageSchema,
)
from flowdesk.modules.tickets.api import ensure_ticket_access

chat_router = APIRouter(tags=["chat"])


@chat_router.websocket("/tickets/{ticket_id}/ws")
async def ticket_chat(
    ws: WebSocket,
    ticket_id: uuid.UUID,
    current_user: WsCurrentUserDep,
    ticket: WsTicketDep,
    chat_service: TicketChatServiceDep,
) -> None:
    await manager.connect(ticket_id, ws)

    try:
        while True:
            try:
                data = TicketChatMessageCreateSchema.model_validate(await ws.receive_json())
            except ValidationError as error:
                await ws.send_json(
                    {
                        "event": "error",
                        "detail": "Invalid message",
                        "errors": error.errors(
                            include_url=False,
                            include_context=False,
                        ),
                    }
                )
                continue
            except json.JSONDecodeError:
                await ws.send_json(
                    {
                        "event": "error",
                        "detail": "Invalid JSON",
                    }
                )
                continue

            message = await chat_service.create_message(
                data,
                ticket_id=ticket.id,
                author_id=current_user.id,
            )
            response = TicketChatMessageSchema.model_validate(message)

            await manager.broadcast(
                ticket_id,
                {
                    "event": "new_message",
                    **response.model_dump(mode="json"),
                },
            )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ticket_id, ws)


@chat_router.get(
    "/tickets/{ticket_id}/messages",
    response_model=list[TicketChatMessageSchema],
)
async def get_message_history(
    ticket_id: uuid.UUID,
    current_user: CurrentUserDep,
    ticket_service: TicketServiceDep,
    chat_service: TicketChatServiceDep,
) -> list[TicketChatMessageSchema]:
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    ensure_ticket_access(ticket, current_user)
    messages = await chat_service.get_message_history(ticket_id)
    return [TicketChatMessageSchema.model_validate(message) for message in messages]
