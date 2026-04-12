# HARUKI POS 春木
### Japanese-Style Point of Sale System built with Django

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-red)

> A clean, minimal POS system inspired by Japanese retail aesthetics — designed for small businesses, convenience stores, and cafes.

---

## Screenshots

| POS Screen | Checkout | Receipt | Reports |
|---|---|---|---|
| Cashier screen with product grid | Payment methods + change calculator | Itemized receipt with member points | Daily sales dashboard |

---

## Features

### Cashier Screen
- Product grid with uploaded images
- Category filter tabs (Japanese / English)
- Product search in real time
- Session-based cart with quantity controls
- Japanese consumption tax calculation (10% standard / 8% reduced)

### Member System (ポイントカード)
- Search customer by phone number
- Register new members on the spot
- Loyalty points — ¥100 = 1 point
- Points displayed on receipt

### Checkout
- 4 payment methods — Cash / Card / IC Card / QR Code
- Cash change calculator with quick amount buttons
- Automatic stock reduction after sale

### Receipt
- Itemized receipt with Japanese and English product names
- Member name and points earned
- Print support via browser

### Reports (レポート)
- Dashboard with 7-day sales bar chart
- Top 5 selling products this month
- Daily report (日報) with payment breakdown
- Order history with date and status filters
- Member list with total spent and points

### Admin Panel
- Product management with image upload
- Category management
- Order management with status badges
- Staff account management
- HARUKI branded admin header

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 6.0 |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Database | SQLite |
| Static files | Whitenoise |
| Styling | Custom CSS with Japanese design tokens |

---

## Project Structure

```
pos_project/
├── manage.py
├── .env                        # environment variables
├── requirements.txt
├── start_haruki.bat            # Windows startup script
├── backup_haruki.bat           # Daily backup script
├── media/
│   └── product_images/         # uploaded product images
├── pos_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── store/
    ├── models.py               # Category, Product, Customer, Order, OrderItem
    ├── views.py                # all views
    ├── urls.py                 # all routes
    ├── admin.py                # admin configuration
    ├── fixtures/
    │   └── initial_data.json   # sample categories and products
    ├── static/store/
    │   ├── css/
    │   │   ├── haruki.css      # global design tokens
    │   │   ├── login.css
    │   │   ├── pos.css
    │   │   ├── checkout.css
    │   │   ├── receipt.css
    │   │   ├── customer.css
    │   │   └── reports.css
    │   ├── js/
    │   │   ├── pos.js          # cart logic
    │   │   ├── checkout.js     # change calculator
    │   │   ├── customer.js     # member search and register
    │   │   └── reports.js      # bar chart
    │   └── images/
    │       └── no_image.jpg    # placeholder image
    └── templates/store/
        ├── base.html
        ├── login.html
        ├── pos.html
        ├── checkout.html
        ├── receipt.html
        ├── reports.html
        ├── daily_report.html
        ├── order_history.html
        ├── customer_list.html
        ├── 404.html
        └── 500.html
```

---

## Installation

### Requirements
- Python 3.10+
- pip

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/haruki-pos.git
cd haruki-pos/pos_project
```

**2. Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Mac / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```
SECRET_KEY=your-very-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Load sample data**
```bash
python manage.py loaddata store/fixtures/initial_data.json
```

**7. Create admin account**
```bash
python manage.py createsuperuser
```

**8. Collect static files**
```bash
python manage.py collectstatic --noinput
```

**9. Run the server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000`

---

## Usage

### First time setup
1. Go to `http://localhost:8000/admin/`
2. Add product categories under **Store → Categories**
3. Add products under **Store → Products** — upload images and set prices
4. Create staff accounts under **Authentication → Users**
5. Staff log in at `http://localhost:8000/login/`

### Daily operation
1. Double-click `start_haruki.bat` — browser opens automatically
2. Log in with staff credentials
3. Search member by phone number (optional)
4. Tap products to add to cart
5. Click **会計する / CHECKOUT**
6. Select payment method
7. Complete payment → receipt generated automatically
8. Run `backup_haruki.bat` at end of day

### Manager reports
- Visit `http://localhost:8000/reports/` for dashboard
- Daily report at `http://localhost:8000/reports/daily/`
- Order history at `http://localhost:8000/reports/orders/`
- Member list at `http://localhost:8000/reports/customers/`

---

## URL Routes

| URL | Page | Access |
|---|---|---|
| `/` | POS cashier screen | Staff |
| `/login/` | Staff login | Public |
| `/logout/` | Logout | Staff |
| `/checkout/` | Payment screen | Staff |
| `/receipt/<id>/` | Receipt | Staff |
| `/reports/` | Reports dashboard | Staff |
| `/reports/daily/` | Daily report | Staff |
| `/reports/orders/` | Order history | Staff |
| `/reports/customers/` | Member list | Staff |
| `/admin/` | Admin panel | Manager |

---

## Tax System

Following Japanese consumption tax law:

| Type | Rate | Products |
|---|---|---|
| Standard | 10% | General goods, snacks eaten on premises |
| Reduced | 8% | Food and drinks for takeaway |
| Exempt | 0% | As required |

Tax is calculated as **tax-inclusive** (内税) — the displayed price already includes tax.

---

## Member Points System

- Every **¥100 spent = 1 point**
- Points are tracked per customer account
- Points earned shown on receipt
- Cashier searches by phone number
- New members registered on the spot

---

## Design System

Haruki uses a Japanese-inspired minimal design:

| Token | Value | Usage |
|---|---|---|
| `--haruki-black` | `#1a1a1a` | Headers, text, primary buttons |
| `--haruki-red` | `#c0392b` | Accent, prices, active states |
| `--haruki-bg` | `#f7f6f4` | Page background (warm off-white) |
| `--haruki-border` | `#e0ddd8` | All borders |
| `--haruki-muted` | `#999` | Secondary text |

---

## Windows Startup

Double-click `start_haruki.bat` to:
- Activate virtual environment
- Run database migrations
- Start server on port 8000
- Open browser automatically

Double-click `backup_haruki.bat` to:
- Copy `db.sqlite3` to `D:\Haruki_Backups\`
- Name backup with today's date e.g. `haruki_20260411.db`

---

## Local Network Access

To access from tablets or other PCs on the same WiFi:

```bash
python manage.py runserver 0.0.0.0:8000
```

Find your PC IP address:
```bash
ipconfig
```

Add your IP to `.env`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.5
```

Other devices visit: `http://192.168.1.5:8000`

---

## Contributing

1. Fork the repository
2. Create your feature branch `git checkout -b feature/barcode-scanner`
3. Commit your changes `git commit -m 'Add barcode scanner support'`
4. Push to the branch `git push origin feature/barcode-scanner`
5. Open a Pull Request

---

## Roadmap

- [ ] Barcode scanner support
- [ ] Low stock email alerts
- [ ] Monthly Excel export
- [ ] Discount and coupon system
- [ ] Multiple store locations
- [ ] Customer-facing display
- [ ] Kitchen printer integration

---

## License

MIT License — free to use for personal and commercial projects.

---

## Author

Built with Django and Japanese design principles.

> ありがとうございます。またお越しください。
> Thank you. Please come again.

**HARUKI POS 春木** — *Simple. Clean. Japanese.*
