from django.db import models


class DatabaseFile(models.Model):
    """Binary file stored in the database (Neon / Postgres / SQLite)."""

    name = models.CharField(max_length=512, unique=True, db_index=True)
    content = models.BinaryField()
    content_type = models.CharField(max_length=128, default="application/octet-stream")
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
