from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import CafeSetting, OpeningHour
from apps.menu.models import Category, Product
from apps.gallery.models import GalleryCategory, GalleryImage
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Seed initial cafe data for Phase 1 demonstration"

    def handle(self, *args, **options):
        self.stdout.write("Seeding cafe data...")

        # 1. Superuser
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@cafe.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' with password 'admin123'"))
        else:
            self.stdout.write("Superuser 'admin' already exists")

        # 2. Cafe Settings
        cafe_setting, created = CafeSetting.objects.get_or_create(
            id=1,
            defaults={
                'cafe_name': "Mitra Cafe",
                'tagline': "Crafted Coffee, Delicious Bites & Warm Moments",
                'short_description': "Your beloved neighborhood cafe offering handcrafted specialty coffees, freshly baked delicacies, and a warm, vibrant atmosphere.",
                'about_description': "Founded with a passion for soulful coffee and heartfelt hospitality, Mitra Cafe brings friends and families together over rich brews and authentic flavors. Every cup is brewed with precision, every dish crafted with organic ingredients, and every guest welcomed like family.",
                'phone': "+91 7405401350",
                'email': "jenildiyora760@gmail.com",
                'address': "Mitra Cafe, Chhaprabhatha, Surat, Gujarat 394520",
                'google_maps_url': "https://maps.app.goo.gl/YjiYuT8wt5XhwfJC7",
                'instagram_url': "https://instagram.com/mitracafe",
                'facebook_url': "https://facebook.com/mitracafe",
                'whatsapp_number': "+917405401350",
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Cafe Settings"))

        # 3. Opening Hours
        days_hours = [
            ("Monday", "08:00 AM", "10:00 PM", False, 1),
            ("Tuesday", "08:00 AM", "10:00 PM", False, 2),
            ("Wednesday", "08:00 AM", "10:00 PM", False, 3),
            ("Thursday", "08:00 AM", "10:00 PM", False, 4),
            ("Friday", "08:00 AM", "11:00 PM", False, 5),
            ("Saturday", "08:00 AM", "11:00 PM", False, 6),
            ("Sunday", "08:30 AM", "10:00 PM", False, 7),
        ]
        for day, open_t, close_t, closed, order in days_hours:
            OpeningHour.objects.get_or_create(
                day=day,
                defaults={
                    'opening_time': open_t,
                    'closing_time': close_t,
                    'is_closed': closed,
                    'display_order': order,
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded Opening Hours"))

        # 4. Menu Categories
        categories_data = [
            ("Coffee", "Artisanal espresso and slow drip brews made with sustainably sourced beans", 1),
            ("Tea", "Handcrafted whole leaf teas, botanical infusions, and traditional chais", 2),
            ("Cold Beverages", "Chilled cold brews, blended smoothies, and refreshing coolers", 3),
            ("Breakfast", "Wholesome, energizing morning plates served fresh daily", 4),
            ("Snacks", "Gourmet savory bites, artisanal sandwiches, and loaded toasts", 5),
            ("Desserts", "Decadent cakes, buttery pastries, and sweet delights", 6),
        ]
        cat_objs = {}
        for cat_name, desc, order in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': desc,
                    'display_order': order,
                    'is_active': True,
                }
            )
            cat_objs[cat_name] = cat
        self.stdout.write(self.style.SUCCESS("Seeded Menu Categories"))

        # 5. Menu Products
        products_data = [
            # Coffee
            ("Espresso Solo", "Coffee", 140, "A concentrated, bold shot of single-origin Arabica with rich golden crema.", "Bold & intense single shot", True, False, True, True, False, "", 1),
            ("Caramel Hazelnut Latte", "Coffee", 240, "Velvety steamed milk with double espresso, infused with housemade caramel and toasted hazelnut.", "Signature comforting flavored latte", True, True, True, True, False, "Dairy, Nuts", 2),
            ("Spanish Cortado", "Coffee", 190, "Equal parts robust espresso and silky warm milk to cut the acidity.", "Balanced Spanish style coffee", False, False, True, True, False, "Dairy", 3),
            ("Signature Nitro Cold Brew", "Coffee", 260, "Cold steeped for 24 hours and nitrogen infused for an ultra-creamy, cascading velvety texture.", "Velvety smooth nitrogen cold brew", True, True, True, True, False, "", 4),
            ("Cappuccino Classico", "Coffee", 210, "Rich espresso crowned with equal layers of steamed milk and fluffy milk foam, dusted with dark cocoa.", "Classic Italian espresso & foam", False, True, True, True, False, "Dairy", 5),

            # Tea
            ("Masala Chai Latte", "Tea", 160, "Slow-brewed Assam CTC black tea with crushed cardamom, cinnamon, clove, and ginger.", "Fragrant spiced traditional chai", True, True, True, True, True, "Dairy", 1),
            ("Japanese Ceremonial Matcha", "Tea", 250, "Whisked Uji stone-ground ceremonial matcha blended with warm oat milk.", "Antioxidant-rich ceremonial matcha", True, False, True, True, False, "", 2),
            ("Himalayan Chamomile & Lemongrass", "Tea", 180, "Caffeine-free organic herbal infusion with soothing chamomile blossoms and zesty lemongrass.", "Calming bedtime botanical blend", False, False, True, True, False, "", 3),

            # Cold Beverages
            ("Iced Salted Caramel Macchiato", "Cold Beverages", 250, "Chilled whole milk poured over ice, marked with double espresso and topped with sea-salt caramel drizzle.", "Chilled sweet & salty layered favorite", True, True, True, True, False, "Dairy", 1),
            ("Mango Passionfruit Sparkler", "Cold Beverages", 210, "Crushed Alphonso mango pulp, tangy passionfruit essence, and sparkling mineral water with fresh mint.", "Fruity refreshing bubbly refresher", False, False, True, True, False, "", 2),
            ("Dark Chocolate Mocha Frappe", "Cold Beverages", 270, "Blended Belgian cocoa, double espresso, crushed ice, and whipped cream topping.", "Indulgent blended frozen coffee shake", True, False, True, True, False, "Dairy", 3),

            # Breakfast
            ("Avocado & Sourdough Tartine", "Breakfast", 320, "Creamy smashed Haas avocado on toasted sourdough, topped with cherry tomatoes, feta, and toasted pumpkin seeds.", "Fresh wholesome morning favorite", True, True, True, True, False, "Gluten, Dairy", 1),
            ("Artisan Granola & Greek Yogurt Bowl", "Breakfast", 260, "Organic honey-baked granola, Greek yogurt, wild berry compote, chia seeds, and sliced almonds.", "High protein wholesome yogurt bowl", False, False, True, True, False, "Dairy, Nuts", 2),
            ("Classic French Butter Croissant", "Breakfast", 160, "Flaky, golden-layered viennoiserie baked fresh every morning with pure Normandy butter.", "Buttery flaky bakery classic", False, True, True, True, False, "Gluten, Dairy", 3),

            # Snacks
            ("Truffle Parmesan Hand-Cut Fries", "Snacks", 240, "Crispy golden potato fries tossed in black truffle oil, rosemary sea salt, and grated aged Parmesan.", "Decadent crispy snack with garlic aioli", True, True, True, True, False, "Dairy", 1),
            ("Pesto Paneer Panini", "Snacks", 290, "Grilled sourdough panini loaded with marinated cottage cheese, basil pesto, sundried tomatoes, and fresh mozzarella.", "Hot pressed gourmet panini sandwich", False, False, True, True, False, "Gluten, Dairy, Nuts", 2),
            ("Spicy Jalapeño Cheese Poppers", "Snacks", 220, "Crumb-fried molten cheddar and cream cheese bites with pickled jalapeños and chipotle dip.", "Crispy golden molten cheese bites", False, False, True, True, True, "Dairy, Gluten", 3),

            # Desserts
            ("Warm Belgian Chocolate Molten Cake", "Desserts", 280, "Rich 70% dark chocolate cake with a molten flowing center, served with vanilla bean ice cream.", "Decadent gooey chocolate dessert", True, True, True, True, False, "Dairy, Gluten, Eggs", 1),
            ("Classic New York Baked Cheesecake", "Desserts", 270, "Creamy baked Philadelphia cheesecake over a buttery graham cracker crust with blueberry coulis.", "Smooth rich classic cheesecake", False, True, True, True, False, "Dairy, Gluten", 2),
            ("Tiramisu Tradizionale", "Desserts", 290, "Espresso-soaked Savoiardi ladyfingers layered with velvety mascarpone cream and dusted with bitter cocoa.", "Authentic Italian coffee dessert", True, False, True, True, False, "Dairy, Gluten", 3),
        ]

        for name, cat_name, price, desc, s_desc, feat, best, avail, veg, spicy, allergen, order in products_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat_objs[cat_name],
                    'price': price,
                    'description': desc,
                    'short_description': s_desc,
                    'is_featured': feat,
                    'is_bestseller': best,
                    'is_available': avail,
                    'vegetarian': veg,
                    'spicy': spicy,
                    'allergen_information': allergen,
                    'display_order': order,
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded Menu Products"))

        # 6. Gallery Categories & Images
        gal_cats = [
            ("Coffee", 1),
            ("Food", 2),
            ("Interior", 3),
            ("Exterior", 4),
            ("Events", 5),
        ]
        g_objs = {}
        for g_name, g_order in gal_cats:
            gcat, _ = GalleryCategory.objects.get_or_create(
                name=g_name,
                defaults={'display_order': g_order, 'is_active': True}
            )
            g_objs[g_name] = gcat

        gallery_items = [
            ("Single Origin Pour Over", "Coffee", "Slow drip manual brew ritual with Ethiopian Yirgacheffe", 1),
            ("Latte Art Rosette", "Coffee", "Barista pouring delicate latte art into ceramic mug", 2),
            ("Freshly Baked Viennoiserie", "Food", "Morning spread of butter croissants and pain au chocolat", 3),
            ("Smashed Avocado Tartine", "Food", "Gourmet sourdough toast with heirloom cherry tomatoes", 4),
            ("Sunlit Cozy Reading Corner", "Interior", "Warm rustic timber tables, ambient pendant lights, and bookshelves", 5),
            ("Espresso Bar & La Marzocco", "Interior", "Custom polished copper espresso machine at the main counter", 6),
            ("Garden Terrace Seating", "Exterior", "Leafy outdoor patio bathed in golden afternoon light", 7),
            ("Weekend Acoustic Live Set", "Events", "Intimate evening live music performance at the cafe lounge", 8),
        ]
        for title, cat_name, caption, order in gallery_items:
            GalleryImage.objects.get_or_create(
                title=title,
                defaults={
                    'category': g_objs[cat_name],
                    'caption': caption,
                    'display_order': order,
                    'is_active': True,
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded Gallery Items"))

        # 7. Customer Reviews
        reviews_data = [
            ("Aarav Mehta", 5, "Mitra Cafe has genuinely the best specialty coffee in the city! The Nitro Cold Brew was extraordinarily smooth and the avocado sourdough tartine was perfection. The staff is so warm and welcoming.", True, 1),
            ("Sophia Chen", 5, "Such a cozy aesthetic and wonderful ambiance for both working and catching up with friends. Their Caramel Hazelnut Latte and Belgian chocolate molten cake are an absolute must-try!", True, 2),
            ("Rohan Sharma", 5, "Outstanding attention to coffee craft! The baristas know their origins, notes, and brewing temperatures. The acoustic live music on weekends makes the vibe unforgettable.", True, 3),
            ("Ananya Deshmukh", 4, "Loved the matcha latte and truffle fries. The seating is comfortable, fast Wi-Fi, and the outdoor terrace is simply beautiful. Highly recommended!", False, 4),
            ("Kavita Rao", 5, "The Spanish cortado was robust and perfectly balanced. Easily my favorite cafe to unwind on a Sunday morning.", False, 5),
        ]
        for name, rating, text, feat, order in reviews_data:
            Review.objects.get_or_create(
                customer_name=name,
                defaults={
                    'rating': rating,
                    'review_text': text,
                    'is_featured': feat,
                    'is_active': True,
                    'display_order': order,
                }
            )
        self.stdout.write(self.style.SUCCESS("Seeded Customer Reviews"))
        self.stdout.write(self.style.SUCCESS("Cafe database successfully initialized!"))

