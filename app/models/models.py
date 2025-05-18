from tortoise import fields, models

from app.core.enums import FriendshipStatus, GameStatus


class User(models.Model):
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=255, default="")
    username = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    completed_unit = fields.IntField(default=0)

    class Meta:
        table = "users"


class Word(models.Model):
    id = fields.BigIntField(pk=True)
    data = fields.JSONField(
        schmea={
            "type": "object",
            "properties": {
                "en": {"type": "array", 'items': {'type': 'string'}},
                "uz": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["en", "uz"],
        }
    )

    class Meta:
        table = "words"


class Friendship(models.Model):
    id = fields.IntField(pk=True)
    requester = fields.ForeignKeyField("models.User", related_name="sent_requests")
    receiver = fields.ForeignKeyField("models.User", related_name="received_requests")
    status = fields.CharEnumField(FriendshipStatus, default=FriendshipStatus.pending)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("requester", "receiver")
