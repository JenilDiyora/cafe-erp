# Mitra Cafe — Phase 1 Website

A modern, responsive, server-rendered cafe website built using **Python, Django, Jinja2 Templates, and PostgreSQL**.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+, Django 5.2+
- **Frontend / Templates:** Jinja2 Template Engine (Django Jinja2 Backend)
- **Database:** PostgreSQL (via `psycopg` 3)
- **Styling:** Bootstrap 5.3 + Bootstrap Icons + Custom Warm Cafe Theme
- **Admin:** Django Admin CMS
- **Architecture:** Traditional Server-Rendered (No React.js, No SPA, No unnecessary REST APIs for Phase 1)

---

## 📂 Project Structure

```text
cafe-erp/
├── backend/
│   ├── apps/
│   │   ├── core/         # Cafe settings, Opening hours, Home, About, SEO & Errors
│   │   ├── menu/         # Menu categories, Products, Search & Filters
│   │   ├── gallery/      # Gallery categories, Photo collection, Lightbox
│   │   ├── reviews/      # Customer testimonials, Star ratings
│   │   └── contact/      # Contact inquiries, ModelForm, Validation
│   ├── config/
│   │   ├── settings.py   # Jinja2 + PostgreSQL configuration
│   │   ├── urls.py       # Main route registry & media handlers
│   │   ├── jinja2.py     # Jinja2 custom globals, filters, and helpers
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── templates/        # Jinja2 templates
│   │   ├── base.html
│   │   ├── includes/     # Navbar, Footer, Messages, Pagination
│   │   ├── home/         # Homepage template
│   │   ├── menu/         # Menu catalog with search & dietary tags
│   │   ├── about/        # Story, Mission, Vision & Ingredients
│   │   ├── gallery/      # Responsive image grid with Lightbox modal
│   │   ├── reviews/      # Testimonials and star ratings
│   │   ├── contact/      # Contact info, opening hours & inquiry form
│   │   └── errors/       # Custom 404 & 500 error pages
│   ├── static/
│   │   ├── css/          # main.css, responsive.css
│   │   └── js/           # main.js (lightbox, mobile navbar, smooth scroll)
│   ├── media/            # Uploaded images (cafe, menu, gallery, reviews)
│   ├── manage.py
│   └── .env
├── requirements.txt
├── .env.example
├── .gitignore
├── manage.py             # Root proxy for convenient manage.py execution
└── README.md
```

---

## 🚀 Getting Started

### 1. Environment Setup

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Database (.env)

Ensure your `.env` contains your PostgreSQL credentials:

```env
DEBUG=True
SECRET_KEY=django-insecure-cafe-website-phase1-secret-key-2026-production-ready
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=cafe_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 3. Run Migrations & Seed Demo Data

```bash
python manage.py migrate
python manage.py seed_cafe_data
```

The `seed_cafe_data` command will automatically create:
- **Superuser account:** `admin` / `admin123`
- **Cafe Branding & Info:** Mitra Cafe
- **Opening Hours:** Monday – Sunday schedule
- **Menu Categories & Products:** Single origin coffees, artisanal teas, breakfast tartines, pastries, snacks, desserts
- **Gallery Collection:** Interior, coffee bar, terrace & food photos
- **Customer Reviews:** 5-star testimonials

### 4. Start Development Server

```bash
python manage.py runserver
```

Open your browser at:
- **Website Home:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Menu Catalog:** [http://127.0.0.1:8000/menu/](http://127.0.0.1:8000/menu/)
- **About Us:** [http://127.0.0.1:8000/about/](http://127.0.0.1:8000/about/)
- **Photo Gallery:** [http://127.0.0.1:8000/gallery/](http://127.0.0.1:8000/gallery/)
- **Reviews:** [http://127.0.0.1:8000/reviews/](http://127.0.0.1:8000/reviews/)
- **Contact & Inquiries:** [http://127.0.0.1:8000/contact/](http://127.0.0.1:8000/contact/)
- **Django Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - *Username:* `admin`
  - *Password:* `admin123`

---

## 🧪 Running Automated Tests

Run the full automated test suite:

```bash
python manage.py test apps.core apps.menu apps.gallery apps.reviews apps.contact
```

All 13 unit tests test URL routes, database persistence, search filtering, category tabs, and contact form validation.

