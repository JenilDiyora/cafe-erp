"""Management command to download and attach curated cafe photographs to database records."""
import urllib.request
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.menu.models import Product
from apps.gallery.models import GalleryImage
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Download and link high-resolution curated photos for gallery, menu products, and reviews"

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT)
        (media_dir / 'cafe').mkdir(parents=True, exist_ok=True)
        (media_dir / 'gallery').mkdir(parents=True, exist_ok=True)
        (media_dir / 'menu' / 'products').mkdir(parents=True, exist_ok=True)
        (media_dir / 'menu' / 'categories').mkdir(parents=True, exist_ok=True)
        (media_dir / 'reviews').mkdir(parents=True, exist_ok=True)

        def download_file(url, target_path):
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response, open(target_path, 'wb') as out_file:
                out_file.write(response.read())

        # 1. Gallery Images Mapping
        gallery_map = {
            "Single Origin Pour Over": ("gallery/pour_over.jpg", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80"),
            "Latte Art Rosette": ("gallery/latte_art.jpg", "https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&w=800&q=80"),
            "Freshly Baked Viennoiserie": ("gallery/croissants.jpg", "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80"),
            "Smashed Avocado Tartine": ("gallery/avocado_toast.jpg", "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80"),
            "Sunlit Cozy Reading Corner": ("gallery/interior_corner.jpg", "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80"),
            "Espresso Bar & La Marzocco": ("gallery/espresso_bar.jpg", "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80"),
            "Garden Terrace Seating": ("gallery/terrace.jpg", "https://images.unsplash.com/photo-1559925393-8be0ec4767c8?auto=format&fit=crop&w=800&q=80"),
            "Weekend Acoustic Live Set": ("gallery/live_music.jpg", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80"),
        }

        self.stdout.write("Linking and verifying gallery photos...")
        for title, (rel_path, url) in gallery_map.items():
            dest = media_dir / rel_path
            if not dest.exists():
                try:
                    self.stdout.write(f"  Downloading {title}...")
                    download_file(url, dest)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not download {title}: {e}"))
            GalleryImage.objects.filter(title=title).update(image=rel_path)

        # 2. Menu Products Mapping
        product_map = {
            "Espresso Solo": ("menu/products/espresso.jpg", "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?auto=format&fit=crop&w=600&q=80"),
            "Caramel Hazelnut Latte": ("menu/products/caramel_latte.jpg", "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=600&q=80"),
            "Spanish Cortado": ("menu/products/cortado.jpg", "https://images.unsplash.com/photo-1577968897966-3d4325b36b61?auto=format&fit=crop&w=600&q=80"),
            "Signature Nitro Cold Brew": ("menu/products/cold_brew.jpg", "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=600&q=80"),
            "Cappuccino Classico": ("menu/products/cappuccino.jpg", "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=600&q=80"),
            "Masala Chai Latte": ("menu/products/masala_chai.jpg", "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80"),
            "Japanese Ceremonial Matcha": ("menu/products/matcha.jpg", "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80"),
            "Himalayan Chamomile & Lemongrass": ("menu/products/chamomile.jpg", "https://images.unsplash.com/photo-1597481499750-3e6b22637e12?auto=format&fit=crop&w=600&q=80"),
            "Iced Salted Caramel Macchiato": ("menu/products/iced_macchiato.jpg", "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=600&q=80"),
            "Mango Passionfruit Sparkler": ("menu/products/sparkler.jpg", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80"),
            "Dark Chocolate Mocha Frappe": ("menu/products/mocha_frappe.jpg", "https://images.unsplash.com/photo-1578314675249-a6910f80cc4e?auto=format&fit=crop&w=600&q=80"),
            "Avocado & Sourdough Tartine": ("menu/products/avocado_tartine.jpg", "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=600&q=80"),
            "Artisan Granola & Greek Yogurt Bowl": ("menu/products/granola_bowl.jpg", "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80"),
            "Classic French Butter Croissant": ("menu/products/croissant.jpg", "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80"),
            "Truffle Parmesan Hand-Cut Fries": ("menu/products/truffle_fries.jpg", "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80"),
            "Pesto Paneer Panini": ("menu/products/panini.jpg", "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=600&q=80"),
            "Spicy Jalapeño Cheese Poppers": ("menu/products/poppers.jpg", "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?auto=format&fit=crop&w=600&q=80"),
            "Warm Belgian Chocolate Molten Cake": ("menu/products/molten_cake.jpg", "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80"),
            "Classic New York Baked Cheesecake": ("menu/products/cheesecake.jpg", "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=600&q=80"),
            "Tiramisu Tradizionale": ("menu/products/tiramisu.jpg", "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=600&q=80"),
        }

        self.stdout.write("Linking and verifying menu product photos...")
        for name, (rel_path, url) in product_map.items():
            dest = media_dir / rel_path
            if not dest.exists():
                try:
                    self.stdout.write(f"  Downloading {name}...")
                    download_file(url, dest)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not download {name}: {e}"))
            Product.objects.filter(name=name).update(image=rel_path)

        # 3. Customer Review Avatars
        review_map = {
            "Aarav Mehta": ("reviews/aarav.jpg", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=250&q=80"),
            "Sophia Chen": ("reviews/sophia.jpg", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=250&q=80"),
            "Rohan Sharma": ("reviews/rohan.jpg", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=250&q=80"),
            "Ananya Deshmukh": ("reviews/ananya.jpg", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=250&q=80"),
            "Kavita Rao": ("reviews/kavita.jpg", "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=250&q=80"),
        }

        self.stdout.write("Linking and verifying review avatars...")
        for customer, (rel_path, url) in review_map.items():
            dest = media_dir / rel_path
            if not dest.exists():
                try:
                    self.stdout.write(f"  Downloading avatar for {customer}...")
                    download_file(url, dest)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not download {customer}: {e}"))
            Review.objects.filter(customer_name=customer).update(customer_image=rel_path)

        self.stdout.write(self.style.SUCCESS("Successfully populated and linked all photographs!"))

