from catalog.models import Product, ProductVariation


class StockError(Exception):
    pass


def _find_variation(product: Product, color: str, size: str) -> ProductVariation | None:
    qs = product.variations.all()
    color = (color or "").strip().lower()
    size = (size or "").strip().lower()

    for variation in qs:
        if variation.name.strip().lower() == color and variation.size.strip().lower() == size:
            return variation

    # Fallback: match color only if size empty on either side
    for variation in qs:
        if variation.name.strip().lower() == color:
            if not size or not variation.size.strip() or variation.size.strip().lower() == size:
                return variation
    return None


def validate_order_stock(items: list[dict]):
    for item in items:
        document_id = str(item.get("productDocumentId") or "").strip()
        quantity = int(item.get("quantity") or 0)
        color = item.get("color") or ""
        size = item.get("size") or ""
        name = item.get("productName") or "Item"

        if quantity < 1:
            raise StockError(f"Invalid quantity for {name}.")

        try:
            product = Product.objects.get(document_id=document_id, is_published=True)
        except Product.DoesNotExist as exc:
            raise StockError(f"{name} is no longer available.") from exc

        variation = _find_variation(product, color, size)
        if not variation:
            raise StockError(f"Selected option for {name} is unavailable.")
        if variation.stock < quantity:
            raise StockError(f"Not enough stock for {name} ({color}/{size}).")


def decrease_stock(items: list[dict]):
    for item in items:
        product = Product.objects.get(document_id=item["productDocumentId"])
        variation = _find_variation(product, item.get("color") or "", item.get("size") or "")
        if not variation:
            raise StockError("Variation not found while decreasing stock.")
        quantity = int(item.get("quantity") or 0)
        if variation.stock < quantity:
            raise StockError("Stock changed while placing order.")
        variation.stock -= quantity
        variation.save(update_fields=["stock"])


def restore_stock(items: list[dict]):
    for item in items:
        try:
            product = Product.objects.get(document_id=item["productDocumentId"])
        except Product.DoesNotExist:
            continue
        variation = _find_variation(product, item.get("color") or "", item.get("size") or "")
        if not variation:
            continue
        variation.stock += int(item.get("quantity") or 0)
        variation.save(update_fields=["stock"])
