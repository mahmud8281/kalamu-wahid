# 🧵 Kalamu Wahid Tailoring Synergy

A full-stack web platform for a premium Hausa tailoring and textile business.
Built with Python Flask, SQLite, and Tailwind CSS.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Installation Guide](#installation-guide)
6. [Running the Project](#running-the-project)
7. [Default Admin Login](#default-admin-login)
8. [How to Use](#how-to-use)
9. [WhatsApp Setup](#whatsapp-setup)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)

---

## 📌 Project Overview

Kalamu Wahid Tailoring Synergy is a business management platform that allows:

- Customers to register, place tailoring orders, shop for textiles, and track their orders
- The CEO/MD and staff to manage all orders, payments, measurements, gallery, and customers
- Automatic WhatsApp notifications for every new order
- PDF generation for invoices and measurement cards

**Tech Stack:**
| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | SQLite (via SQLAlchemy) |
| Frontend | HTML, Tailwind CSS, JavaScript |
| PDF Generation | ReportLab |
| Authentication | Flask-Login |
| Hosting (recommended) | Render.com |

---

## ✅ Features

### Customer Features
- Register and login with email and password
- Save and edit body measurements digitally
- Place tailoring orders with design image upload
- Browse and order textile products (Shadda, Yadi, Caps, etc.)
- Track order status in real time (Pending → In Progress → Ready → Delivered)
- Download PDF invoice for every order
- Edit profile (name, phone, password)
- WhatsApp button to contact the shop directly

### Admin / CEO / MD Features
- Full dashboard with revenue charts and business analytics
- Manage all tailoring orders (update status, payment)
- Manage all product orders
- Upload fashion gallery (bulk upload, multiple images at once)
- Manage textile products (bulk upload by name/price/category)
- Take and edit customer measurements (registered + walk-in customers)
- Print professional measurement card as PDF
- Print invoice PDF for any order
- Send WhatsApp message directly to any customer
- Manage staff accounts (CEO only)
- Full payment tracking (total revenue, collected, outstanding balance)

---

## 📁 Project Structure

```
kalamu_tailoring/
│
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions (db, login_manager)
├── requirements.txt        # Python dependencies
├── Procfile                # For deployment on Render
├── .env                    # Environment variables (do not share)
│
├── models/
│   ├── __init__.py
│   ├── user_model.py       # User accounts (customer, admin, staff)
│   ├── measurement_model.py # Customer body measurements
│   ├── order_model.py      # Tailoring orders
│   ├── gallery_model.py    # Fashion gallery images
│   └── product_model.py    # Shop products, product orders, walk-in customers
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py      # Login, register, logout
│   ├── customer_routes.py  # Home page, dashboard, profile
│   ├── order_routes.py     # Place order, my orders, track order
│   ├── measurement_routes.py # Customer measurements
│   ├── shop_routes.py      # Public shop
│   ├── admin_routes.py     # CEO/MD admin panel
│   ├── admin_shop_routes.py # Product & measurement management
│   └── print_routes.py     # PDF invoice and measurement card
│
├── templates/
│   ├── base.html           # Master layout with navbar and footer
│   ├── home.html           # Public home page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── customer/
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── measurements.html
│   │   ├── place_order.html
│   │   ├── my_orders.html
│   │   ├── order_confirm.html
│   │   └── track_order.html
│   ├── shop/
│   │   ├── shop.html
│   │   ├── product_detail.html
│   │   ├── request_order.html
│   │   └── order_confirm.html
│   └── admin/
│       ├── base_admin.html
│       ├── dashboard.html
│       ├── orders.html
│       ├── customers.html
│       ├── customer_detail.html
│       ├── payments.html
│       ├── gallery.html
│       ├── staff.html
│       └── shop/
│           ├── products.html
│           ├── product_orders.html
│           ├── measurements.html
│           └── take_measurement.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── uploads/                # All uploaded images stored here
└── instance/
    └── kalamu_tailoring.db # SQLite database (auto-created)
```

---

## 📦 Requirements

Before installing, make sure you have:

- **Python 3.10 or higher** — Download from https://python.org
- **pip** — comes with Python automatically
- **Git** (optional, for deployment) — Download from https://git-scm.com

To check your Python version, open Command Prompt and run:
```
python --version
```

---

## 🛠 Installation Guide

### Step 1 — Download the project

Place the `kalamu_tailoring` folder on your Desktop.

### Step 2 — Open Command Prompt

Press `Win + R`, type `cmd`, press Enter.

Navigate to the project folder:
```
cd Desktop\kalamu_tailoring
```

### Step 3 — Create a virtual environment

```
python -m venv venv
```

### Step 4 — Activate the virtual environment

```
venv\Scripts\activate
```

You will see `(venv)` appear at the start of the line. This means it is active.

### Step 5 — Upgrade pip

```
python -m pip install --upgrade pip
```

### Step 6 — Install all required libraries

```
pip install -r requirements.txt
```

This will automatically install:
- **flask** — the web framework
- **flask-sqlalchemy** — database management
- **flask-login** — user authentication and sessions
- **flask-wtf** — form handling and security (CSRF protection)
- **pillow** — image processing for uploads
- **python-dotenv** — loads environment variables from .env file
- **reportlab** — generates professional PDF invoices and measurement cards
- **gunicorn** — production web server for deployment
- **werkzeug** — password hashing and security utilities
- **sqlalchemy** — database ORM (Object Relational Mapper)
- **wtforms** — web form validation

Wait until you see `Successfully installed ...` before continuing.

### Step 7 — Create the uploads folder (if it does not exist)

```
mkdir uploads
```

---

## ▶ Running the Project

Make sure your virtual environment is active (you see `(venv)` in the terminal).

Run the application:
```
python app.py
```

You will see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Open your browser and go to:
```
http://127.0.0.1:5000
```

The website is now running on your computer.

To stop the server, press `Ctrl + C` in the terminal.

---

## 🔐 Default Admin Login

When you run the project for the first time, an admin account is created automatically.

| Field | Value |
|-------|-------|
| URL | http://127.0.0.1:5000/admin/dashboard |
| Email | admin@kalamu.com |
| Password | admin123 |

**IMPORTANT:** Change this password immediately after your first login by going to the staff settings.

---

## 📱 How to Use

### For Customers

| Action | URL |
|--------|-----|
| Home page | http://127.0.0.1:5000 |
| Register | http://127.0.0.1:5000/register |
| Login | http://127.0.0.1:5000/login |
| Dashboard | http://127.0.0.1:5000/dashboard |
| My Profile | http://127.0.0.1:5000/profile |
| Measurements | http://127.0.0.1:5000/measurements |
| Place Order | http://127.0.0.1:5000/place-order |
| My Orders | http://127.0.0.1:5000/my-orders |
| Shop | http://127.0.0.1:5000/shop |

### For Admin / CEO / MD

| Action | URL |
|--------|-----|
| Admin Dashboard | http://127.0.0.1:5000/admin/dashboard |
| All Orders | http://127.0.0.1:5000/admin/orders |
| Payments | http://127.0.0.1:5000/admin/payments |
| Customers | http://127.0.0.1:5000/admin/customers |
| Gallery | http://127.0.0.1:5000/admin/gallery |
| Staff Accounts | http://127.0.0.1:5000/admin/staff |
| Products | http://127.0.0.1:5000/admin/shop |
| Product Orders | http://127.0.0.1:5000/admin/shop/orders |
| Measurements | http://127.0.0.1:5000/admin/shop/measurements |

---

## 📲 WhatsApp Setup

To connect WhatsApp to your business number:

1. Open `routes/order_routes.py`
2. Find this line:
   ```python
   WHATSAPP_NUMBER = '2348000000000'
   ```
3. Replace `2348000000000` with your real number

**Number format rules:**
- Remove the leading `0` from your Nigerian number
- Add `234` at the front
- No spaces, no `+` sign
- Example: `08123456789` becomes `2348123456789`

Do the same replacement in these files:
- `routes/order_routes.py`
- `routes/shop_routes.py`
- `templates/base.html` (floating WhatsApp button)
- `templates/customer/track_order.html`

**Fastest method — VS Code Find & Replace:**
1. Press `Ctrl + Shift + H`
2. Search: `2348000000000`
3. Replace: your real number
4. Click Replace All

---

## 🌐 Deployment Guide

Follow these steps to make the website live online so anyone in the world can visit it.

### Option 1 — Render.com (Recommended, Free)

**Step 1 — Create a GitHub account**

Go to https://github.com and create a free account.

**Step 2 — Upload your project to GitHub**

1. Download and install Git from https://git-scm.com
2. Open Command Prompt in your project folder
3. Run these commands one by one:
```
git init
git add .
git commit -m "Initial commit - Kalamu Wahid Tailoring"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kalamu-wahid.git
git push -u origin main
```

**Step 3 — Create account on Render**

Go to https://render.com and sign up with your GitHub account.

**Step 4 — Create a new Web Service**

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Fill in these settings:

| Setting | Value |
|---------|-------|
| Name | kalamu-wahid |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:application` |
| Plan | Free |

**Step 5 — Add environment variables**

In the Render dashboard, go to **Environment** and add:

| Key | Value |
|-----|-------|
| SECRET_KEY | any-long-random-string-here |
| FLASK_ENV | production |

**Step 6 — Deploy**

Click **Create Web Service**. Render will build and deploy your app.

Your website will be live at:
```
https://kalamu-wahid.onrender.com
```

> Note: Free Render accounts sleep after 15 minutes of inactivity. The first visit after sleeping takes 30-60 seconds to load. Upgrade to a paid plan (7 USD/month) for always-on hosting.

---

### Option 2 — PythonAnywhere (Simple, Free)

1. Go to https://pythonanywhere.com and create a free account
2. Go to **Files** and upload your project folder
3. Open a **Bash console** and run:
```
pip install -r requirements.txt
```
4. Go to **Web** → **Add a new web app**
5. Choose **Flask** and set the path to your `app.py`
6. Click **Reload**

Your site will be at:
```
https://yourusername.pythonanywhere.com
```

---

### Option 3 — VPS (Advanced, Full Control)

If you want full control with a real domain name:

1. Buy a VPS from DigitalOcean, Hetzner, or Linode (5-10 USD/month)
2. Buy a domain name from Namecheap or GoDaddy (5-15 USD/year)
3. Install Ubuntu, Nginx, and Gunicorn on the server
4. Point your domain to the server IP address
5. Set up SSL certificate with Let's Encrypt (free HTTPS)

This option requires Linux knowledge. Recommended only after the business grows.

---

## 🔧 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'flask'`
**Solution:** Make sure the virtual environment is activated:
```
venv\Scripts\activate
```
Then install again:
```
pip install -r requirements.txt
```

---

### Problem: `IndentationError` when running app.py
**Solution:** Open the file mentioned in the error and check that all code is properly indented using spaces (not tabs). Python is sensitive to indentation.

---

### Problem: Database error or missing column
**Solution:** Delete the old database and let Flask recreate it:
```
del instance\kalamu_tailoring.db
python app.py
```
Note: This deletes all existing data. Only do this in development.

---

### Problem: Images not showing after upload
**Solution:** Make sure the `uploads` folder exists:
```
mkdir uploads
```
Also check that `config.py` has the correct path:
```python
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
```

---

### Problem: WhatsApp button not working
**Solution:** Make sure the phone number is in the correct format — no `+` sign, starts with `234`, no spaces. Example: `2348123456789`

---

### Problem: `(venv)` not appearing after activation
**Solution:** Run this command instead:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again:
```
venv\Scripts\activate
```

---

### Problem: Port already in use
**Solution:** Another program is using port 5000. Run Flask on a different port:
```
flask run --port 5001
```
Then visit http://127.0.0.1:5001

---

## 📞 Support

For questions about this platform contact the developer.

**Business:** Kalamu Wahid Tailoring Synergy
**Location:** Kano, Nigeria

---

## 📄 License

This project was built specifically for Kalamu Wahid Tailoring Synergy.
All rights reserved © 2024.
