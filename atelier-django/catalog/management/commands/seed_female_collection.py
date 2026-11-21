"""Replace catalog with a curated women's clothing collection + HD Unsplash images."""
from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

from catalog.models import Category, Product, ProductImage, ProductVariation
from cms.models import AboutPage, ContactPage, HomePage, ShopPage


# HD Unsplash fashion photos (free license).
IMG = {
    "silk_blouse": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=1000&q=80",
    "linen_dress": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=1000&q=80",
    "wool_coat": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?auto=format&fit=crop&w=1000&q=80",
    "cashmere_knit": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=1000&q=80",
    "wide_trousers": "https://images.unsplash.com/photo-1594633313593-bab3825d0caf?auto=format&fit=crop&w=1000&q=80",
    "satin_skirt": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=1000&q=80",
    "tailored_blazer": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?auto=format&fit=crop&w=1000&q=80",
    "evening_dress": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=1000&q=80",
    "trench_coat": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1000&q=80",
    "soft_cardigan": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=1000&q=80",
    "denim_jacket": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=1000&q=80",
    "midi_dress": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1000&q=80",
    "leather_tote": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=1000&q=80",
    "silk_scarf": "https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&w=1000&q=80",
    "cat_dresses": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=1000&q=80",
    "cat_outerwear": "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1000&q=80",
    "cat_knitwear": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=1000&q=80",
    "cat_trousers": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=1000&q=80",
    "cat_accessories": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=1000&q=80",
    "hero": "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1400&q=80",
    "curation_1": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80",
    "curation_2": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1000&q=80",
    "philosophy": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=1000&q=80",
    "about_hero": "https://images.unsplash.com/photo-1558171813-4c088753af8f?auto=format&fit=crop&w=1400&q=80",
}

CATEGORIES = [
    ("Dresses", "dresses", "cat_dresses"),
    ("Outerwear", "outerwear", "cat_outerwear"),
    ("Knitwear", "knitwear", "cat_knitwear"),
    ("Trousers", "trousers", "cat_trousers"),
    ("Tops", "tops", "silk_blouse"),
    ("Accessories", "accessories", "cat_accessories"),
]

PRODUCTS = [
    (
        "Silk Bias-Cut Blouse",
        "tops",
        168,
        "Fluid mulberry silk with a soft bias drape. Designed for polished days and quiet evenings.",
        "silk_blouse",
        [("Ivory", "#F5F0E8"), ("Black", "#1A1A1A"), ("Blush", "#E8C4C0")],
    ),
    (
        "Floral Linen Midi Dress",
        "dresses",
        248,
        "Breathable European linen with a gathered waist and midi length for effortless summer polish.",
        "linen_dress",
        [("Floral Cream", "#F2E8D5"), ("Sage", "#A8B89A")],
    ),
    (
        "Structured Wool Coat",
        "outerwear",
        420,
        "Double-faced wool with a clean shoulder and hidden closures. A winter silhouette with quiet authority.",
        "wool_coat",
        [("Camel", "#C4A484"), ("Charcoal", "#36454F")],
    ),
    (
        "Cashmere Crew Knit",
        "knitwear",
        198,
        "Featherweight cashmere with a refined crew neck. Soft enough for bare skin, sharp enough for layering.",
        "cashmere_knit",
        [("Oatmeal", "#D6C6B0"), ("Black", "#111111"), ("Rose", "#C08081")],
    ),
    (
        "Wide Pleat Trouser",
        "trousers",
        186,
        "High-rise wool blend with deep front pleats and a fluid wide leg. Tailored ease for every day.",
        "wide_trousers",
        [("Ivory", "#F5F0E8"), ("Black", "#111111"), ("Navy", "#1B2838")],
    ),
    (
        "Satin Slip Skirt",
        "dresses",
        158,
        "Bias-cut satin that moves like liquid light. Pair with a knit for day or silk for night.",
        "satin_skirt",
        [("Champagne", "#F7E7CE"), ("Black", "#111111")],
    ),
    (
        "Soft Shoulder Blazer",
        "outerwear",
        312,
        "Unconstructed blazer with a soft shoulder and single-button close. Modern ease, classic line.",
        "tailored_blazer",
        [("Ivory", "#F5F0E8"), ("Black", "#111111")],
    ),
    (
        "Evening Column Dress",
        "dresses",
        380,
        "A sculpted column in fluid crepe. Minimal jewellery, maximum presence.",
        "evening_dress",
        [("Ruby", "#9B1B30"), ("Black", "#0D0D0D")],
    ),
    (
        "Classic Trench Coat",
        "outerwear",
        356,
        "Cotton-blend trench with a belted waist and storm flap. Timeless weatherproof elegance.",
        "trench_coat",
        [("Stone", "#D2C6B2"), ("Black", "#1A1A1A")],
    ),
    (
        "Cloud Soft Cardigan",
        "knitwear",
        142,
        "Open-front cardigan in airy merino. Layer over dresses or wear alone as a light jacket.",
        "soft_cardigan",
        [("Cream", "#F5F1E8"), ("Dusty Pink", "#D4A5A5")],
    ),
    (
        "Cropped Denim Jacket",
        "outerwear",
        176,
        "Washed indigo denim with a cropped boxy fit. The everyday layer that finishes every look.",
        "denim_jacket",
        [("Indigo", "#3F5B8C"), ("Black Wash", "#2B2B2B")],
    ),
    (
        "Wrap Midi Dress",
        "dresses",
        228,
        "Soft jersey wrap with a flattering V-neck and midi skirt. Travel-ready and endlessly wearable.",
        "midi_dress",
        [("Black", "#111111"), ("Olive", "#6B7F5A"), ("Wine", "#722F37")],
    ),
    (
        "Structured Leather Tote",
        "accessories",
        264,
        "Vegetable-tanned leather tote with clean hardware and a spacious interior for city days.",
        "leather_tote",
        [("Tan", "#C68642"), ("Black", "#111111")],
    ),
    (
        "Printed Silk Scarf",
        "accessories",
        98,
        "Hand-rolled silk scarf with an abstract print. Wear at the neck, in hair, or on a bag handle.",
        "silk_scarf",
        [("Multi", "#C9A9A6")],
    ),
]

SIZES = ["XS", "S", "M", "L", "XL"]
ACCESSORY_SIZES = ["One Size"]


class Command(BaseCommand):
    help = "Seed women's clothing collection with HD images into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-old",
            action="store_true",
            help="Do not delete existing products before seeding.",
        )

    def _compress(self, raw: bytes, max_side: int = 1200, quality: int = 82) -> bytes:
        img = Image.open(BytesIO(raw))
        img = img.convert("RGB")
        img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        out = BytesIO()
        img.save(out, format="JPEG", quality=quality, optimize=True)
        return out.getvalue()

    def fetch_all(self) -> dict[str, bytes]:
        cache: dict[str, bytes] = {}
        for key, url in IMG.items():
            try:
                req = Request(url, headers={"User-Agent": "AtelierSeed/1.0"})
                with urlopen(req, timeout=45) as resp:
                    raw = resp.read()
                data = self._compress(raw)
                cache[key] = data
                self.stdout.write(f"  fetched {key} ({len(data) // 1024} KB)")
            except (URLError, HTTPError, TimeoutError, OSError) as exc:
                self.stderr.write(self.style.WARNING(f"  skip {key}: {exc}"))
        return cache

    def as_file(self, cache: dict[str, bytes], key: str) -> ContentFile | None:
        data = cache.get(key)
        if not data:
            return None
        return ContentFile(data, name=f"{slugify(key)}.jpg")

    def handle(self, *args, **options):
        self.stdout.write("1/3 Downloading HD women's fashion images…")
        cache = self.fetch_all()
        if not cache:
            self.stderr.write(self.style.ERROR("No images downloaded — aborting."))
            return

        self.stdout.write("2/3 Writing catalog to Neon…")
        if not options["keep_old"]:
            deleted = Product.objects.count()
            self.stdout.write(f"  deleting {deleted} old products…")
            ProductImage.objects.all().delete()
            ProductVariation.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  cleared {deleted} old products"))

        HomePage.objects.get_or_create(pk=1)
        ShopPage.objects.get_or_create(pk=1)
        AboutPage.objects.get_or_create(pk=1)
        ContactPage.objects.get_or_create(pk=1)

        categories: dict[str, Category] = {}
        for name, slug, img_key in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            cat.name = name
            file = self.as_file(cache, img_key)
            if file:
                cat.image.save(file.name, file, save=False)
            cat.save()
            categories[slug] = cat
            self.stdout.write(f"  category: {name}")

        created = 0
        for name, cat_slug, price, description, img_key, colors in PRODUCTS:
            product, _ = Product.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "category": categories[cat_slug],
                    "is_published": True,
                    "published_at": timezone.now(),
                    "shipping_info": {
                        "label": "Complimentary shipping",
                        "detail": "Ships in 2–4 business days. Free returns within 14 days.",
                    },
                    "return_policy": {
                        "label": "14-day returns",
                        "detail": "Unworn items with tags may be returned within 14 days.",
                    },
                    "artisan_notes": {
                        "label": "Atelier note",
                        "detail": "Cut and finished in small seasonal runs for lasting quality.",
                    },
                },
            )

            file = self.as_file(cache, img_key)
            if file:
                product.images.all().delete()
                img = ProductImage(product=product, sort_order=0)
                img.image.save(file.name, file, save=True)

            product.variations.all().delete()
            sizes = ACCESSORY_SIZES if cat_slug == "accessories" else SIZES
            for color_name, hex_code in colors:
                for size in sizes:
                    stock = 6 if size in ("S", "M", "One Size") else 4
                    ProductVariation.objects.create(
                        product=product,
                        name=color_name,
                        code=hex_code,
                        stock=stock,
                        price=price,
                        size=size,
                    )
            created += 1
            self.stdout.write(self.style.SUCCESS(f"  product: {name}"))

        self.stdout.write("3/3 Updating home & about CMS images…")
        home = HomePage.objects.first()
        if home:
            home.hero_badge = "Women · Spring / Summer"
            home.hero_heading = "Soft Power Dressing"
            home.curation_primary_heading = "Linen & Light"
            home.curation_primary_description = (
                "Breathable silhouettes cut for warm days and golden hours."
            )
            home.curation_secondary_heading = "Evening Ease"
            home.curation_secondary_description = (
                "Column dresses and liquid satin for nights that linger."
            )
            home.trending_heading = "Trending Now"
            home.trending_description = "The season's most-wanted women's pieces."
            for field, key in (
                ("hero_background", "hero"),
                ("curation_primary_image", "curation_1"),
                ("curation_secondary_image", "curation_2"),
                ("philosophy_image", "philosophy"),
            ):
                f = self.as_file(cache, key)
                if f:
                    getattr(home, field).save(f.name, f, save=False)
            home.save()
            home.trending_products.clear()
            for product in Product.objects.filter(is_published=True).order_by("name")[:6]:
                home.trending_products.add(product)

        about = AboutPage.objects.first()
        if about:
            f = self.as_file(cache, "about_hero")
            if f:
                about.hero_background.save(f.name, f, save=False)
                about.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} women's products, {Category.objects.count()} categories, "
                f"{ProductImage.objects.count()} images in Neon."
            )
        )
