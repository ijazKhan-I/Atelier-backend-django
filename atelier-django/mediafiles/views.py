from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from django.conf import settings

from .models import DatabaseFile


@require_GET
def serve_database_media(request, path: str):
    """Serve media bytes stored in the database (Neon-backed uploads)."""
    name = (path or "").lstrip("/")
    if not name or ".." in name.split("/"):
        raise Http404("Invalid media path")

    try:
        row = DatabaseFile.objects.get(name=name)
    except DatabaseFile.DoesNotExist as exc:
        raise Http404("Media not found") from exc

    response = HttpResponse(bytes(row.content), content_type=row.content_type or "application/octet-stream")
    response["Content-Length"] = str(row.size or len(row.content))
    response["Cache-Control"] = "public, max-age=86400"
    return response


def using_database_storage() -> bool:
    backend = (settings.STORAGES.get("default") or {}).get("BACKEND", "")
    return backend == "mediafiles.storage.DatabaseStorage"
