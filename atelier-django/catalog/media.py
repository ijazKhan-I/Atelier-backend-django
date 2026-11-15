"""Serialize Django ImageField values into Strapi-like media objects."""
from django.conf import settings


def absolute_media_url(file_field) -> str | None:
    if not file_field:
        return None
    try:
        url = file_field.url
    except ValueError:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{settings.PUBLIC_BASE_URL}{url}"


def serialize_image(file_field, *, obj_id: int | None = None, document_id: str | None = None):
    url = absolute_media_url(file_field)
    if not url:
        return None

    name = getattr(file_field, "name", "") or "image"
    basename = name.rsplit("/", 1)[-1]

    return {
        "id": obj_id or 0,
        "documentId": document_id or str(obj_id or 0),
        "name": basename,
        "alternativeText": None,
        "caption": None,
        "focalPoint": None,
        "width": 0,
        "height": 0,
        "formats": {},
        "hash": "",
        "ext": f".{basename.rsplit('.', 1)[-1]}" if "." in basename else "",
        "mime": "",
        "size": 0,
        "url": url,
        "previewUrl": None,
        "provider": "local",
        "provider_metadata": None,
        "createdAt": None,
        "updatedAt": None,
        "publishedAt": None,
    }
