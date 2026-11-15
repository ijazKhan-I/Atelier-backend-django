from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import Category, Product, ProductVariation
from cms.models import AboutPage, ContactPage, HomePage, ShopPage


class Command(BaseCommand):
    help = "Seed default CMS pages, sample categories/products, and a demo admin user."

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@atelier.local", "admin123")
            self.stdout.write(self.style.SUCCESS("Created superuser admin / admin123"))
        else:
            self.stdout.write("Superuser admin already exists")

        if not User.objects.filter(username="demo").exists():
            User.objects.create_user("demo", "demo@atelier.local", "demo1234")
            self.stdout.write(self.style.SUCCESS("Created user demo / demo1234"))

        HomePage.objects.get_or_create(pk=1)
        ShopPage.objects.get_or_create(pk=1)
        AboutPage.objects.get_or_create(pk=1)
        ContactPage.objects.get_or_create(pk=1)
        self.stdout.write(self.style.SUCCESS("Ensured CMS single-type pages"))

        categories_spec = [
            ("Outerwear", "outerwear"),
            ("Knitwear", "knitwear"),
            ("Trousers", "trousers"),
            ("Accessories", "accessories"),
        ]
        categories = {}
        for name, slug in categories_spec:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            categories[slug] = cat

        samples = [
            ("Structured Wool Coat", "outerwear", 42000, "A tailored coat with quiet structure."),
            ("Merino Crew Neck", "knitwear", 18000, "Soft merino for everyday layers."),
            ("Wide Pleat Trouser", "trousers", 22000, "Relaxed silhouette with clean pleats."),
            ("Leather Belt", "accessories", 9000, "Vegetable-tanned leather, brass buckle."),
            ("Cashmere Scarf", "accessories", 15000, "Lightweight cashmere in tonal weave."),
            ("Double-Face Blazer", "outerwear", 38000, "Unconstructed blazer with soft shoulder."),
        ]

        created = 0
        for name, cat_slug, price, description in samples:
            if Product.objects.filter(name=name).exists():
                continue
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=categories[cat_slug],
                is_published=True,
                published_at=timezone.now(),
            )
            ProductVariation.objects.create(
                product=product,
                name="Black",
                code="#111111",
                stock=12,
                price=price,
                size="M",
            )
            ProductVariation.objects.create(
                product=product,
                name="Ivory",
                code="#F5F0E8",
                stock=8,
                price=price,
                size="L",
            )
            created += 1

        home = HomePage.objects.first()
        if home and home.trending_products.count() == 0:
            for product in Product.objects.filter(is_published=True)[:4]:
                home.trending_products.add(product)

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} products (skipped existing)"))
        self.stdout.write(self.style.SUCCESS("Done. API: http://localhost:8000/api/"))
