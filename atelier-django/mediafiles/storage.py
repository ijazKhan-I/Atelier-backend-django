"""Store Django media files in the database so uploads survive on Vercel + Neon.

Neon only stores ImageField *paths* by default; the bytes still need a durable
backend. Serverless disks are read-only / ephemeral, so we persist file content
in PostgreSQL alongside the rest of the app data.
"""
from __future__ import annotations

import mimetypes

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri


@deconstructible
class DatabaseStorage(Storage):
    def _db_file(self):
        from .models import DatabaseFile

        return DatabaseFile

    def _normalize(self, name: str) -> str:
        return (name or "").lstrip("/")

    def _guess_content_type(self, name: str) -> str:
        guessed, _ = mimetypes.guess_type(name)
        return guessed or "application/octet-stream"

    def _open(self, name, mode="rb"):
        name = self._normalize(name)
        row = self._db_file().objects.get(name=name)
        return ContentFile(bytes(row.content), name=name)

    def _save(self, name, content):
        name = self._normalize(name)
        if hasattr(content, "chunks"):
            data = b"".join(chunk for chunk in content.chunks())
        else:
            data = content.read()
            if isinstance(data, str):
                data = data.encode("utf-8")

        content_type = getattr(content, "content_type", None) or self._guess_content_type(name)
        Model = self._db_file()
        Model.objects.update_or_create(
            name=name,
            defaults={
                "content": data,
                "content_type": content_type,
                "size": len(data),
            },
        )
        return name

    def exists(self, name):
        name = self._normalize(name)
        return self._db_file().objects.filter(name=name).exists()

    def delete(self, name):
        name = self._normalize(name)
        self._db_file().objects.filter(name=name).delete()

    def size(self, name):
        name = self._normalize(name)
        return self._db_file().objects.values_list("size", flat=True).get(name=name)

    def url(self, name):
        name = self._normalize(name)
        base = settings.MEDIA_URL or "/uploads/"
        if not base.endswith("/"):
            base = f"{base}/"
        return f"{base}{filepath_to_uri(name)}"

    def get_accessed_time(self, name):
        raise NotImplementedError("DatabaseStorage does not track accessed time.")

    def get_created_time(self, name):
        name = self._normalize(name)
        return self._db_file().objects.values_list("created_at", flat=True).get(name=name)

    def get_modified_time(self, name):
        name = self._normalize(name)
        return self._db_file().objects.values_list("updated_at", flat=True).get(name=name)

    def path(self, name):
        # No local filesystem path — required so Django does not treat this as FS storage.
        raise NotImplementedError("DatabaseStorage files are not on the local filesystem.")
