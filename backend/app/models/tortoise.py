# backend/app/models/tortoise.py


from datetime import datetime

from tortoise import fields, models


class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.url


class User(models.Model):
    """A distillist user, identified by their Spotify account."""

    id: int = fields.IntField(primary_key=True)
    spotify_id: str = fields.CharField(max_length=64, unique=True)
    display_name: str | None = fields.CharField(max_length=255, null=True)
    # Both tokens are stored encrypted (see app/security.py), never in plain text.
    access_token: str = fields.TextField()
    refresh_token: str | None = fields.TextField(null=True)
    token_expires_at: datetime = fields.DatetimeField()
    scopes: str = fields.TextField(default="")
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.spotify_id


class Session(models.Model):
    """A server-side login session. The browser only holds its (signed) id."""

    id: str = fields.CharField(max_length=64, primary_key=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="sessions", on_delete=fields.CASCADE
    )
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    expires_at: datetime = fields.DatetimeField()

    def __str__(self) -> str:
        return self.id