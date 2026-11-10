from faststream.rabbit import RabbitQueue

notification = RabbitQueue("notifications.create", durable=True)
