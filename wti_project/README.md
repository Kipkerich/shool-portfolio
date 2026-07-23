# Wama Training Institute (WTI) — Dynamic Django Application

A dynamic, multi-page web platform engineered for **Wama Training Institute (WTI)**, a TVETA-accredited healthcare education institution located in Ongata Rongai, Kenya.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Local Setup](#-installation--local-setup)
- [Version Control & Branching Strategy](#-version-control--branching-strategy)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

This repository transforms WTI's static web presence into a scalable, maintainable **Django multi-page application**. Built with strict adhereance to the **DRY (Don't Repeat Yourself)** principle, shared layout elements like headers and footers are centralized in a master template, while inner pages render dynamic components including interactive carousels, admissions gateways, and updates.

---

## ✨ Key Features

- **Master Template Architecture:** Global UI management via `base.html` inheritance for navigation and footers.
- **Interactive Landing Page Sliders:** Integrated horizontal Owl Carousel sliders for:
  - *Why Choose Us:* Institutional pillars and accreditation highlights.
  - *Available Courses:* Interactive course cards linking to full course details.
- **Admissions Gateway:** Direct CTA flows targeting student conversion, inquiries, and application downloads.
- **News & Insights Grid:** Structured section for institutional news, announcements, and articles.
- **Clean Django Routing:** Clear URL mappings powered by `wti_project` configuration.

---

## 🛠 Tech Stack

- **Backend:** Python 3.10+ / Django 5.x
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 4/5, FontAwesome
- **Slider & Utility Libraries:** jQuery, Owl Carousel, Isotope, Lightbox

---

## 📂 Project Directory Structure

```text
shool-portfolio/
│
├── wti_project/            # Django Root Settings Directory
│   ├── settings.py         # Global App Configurations & Paths
│   ├── urls.py             # Root URL Dispatcher
│   ├── wsgi.py             # WSGI Web Server Gateway Interface
│   └── asgi.py             # Asynchronous Support Config
│
├── core/                   # Core Application Directory
│   ├── templates/core/     # Modular Django HTML Templates
│   │   ├── base.html       # Master Layout (Header, Footer, Head, Scripts)
│   │   ├── index.html      # Dynamic Landing Page
│   │   ├── about.html      # About WTI Template
│   │   ├── courses.html    # Course Catalog & Fee Structures
│   │   └── contact.html    # Inquiry & Location Map
│   ├── static/             # Static Assets (CSS, JS, Fonts, Images)
│   ├── views.py            # Route Controllers
│   └── urls.py             # App-level URL Mappings
│
├── .gitignore              # Ignored Files Matrix (Environment, SQLite, Bytecode)
├── manage.py               # Django Management CLI Utility
└── README.md               # Repository Setup Documentation

🚀 Installation & Local Setup
Follow these step-by-step instructions to set up and run the project locally on your environment.

1. Prerequisites
Ensure you have the following installed on your machine:

Python: 3.10+ (Download Python)

Git: Installed and configured (Download Git)

2. Clone the Repository
Open your terminal and clone the shool-portfolio repository:

Bash
git clone [https://github.com/Kipkerich/shool-portfolio.git](https://github.com/Kipkerich/shool-portfolio.git)
cd shool-portfolio
3. Set Up Virtual Environment
On macOS/Linux:
Bash
python3 -m venv venv
source venv/bin/activate
On Windows (PowerShell / CMD):
PowerShell
python -m venv venv
.\venv\Scripts\activate
4. Install Dependencies
Install Django and required Python modules:

Bash
pip install --upgrade pip
pip install django
(If a requirements.txt is present, run: pip install -r requirements.txt)

5. Apply Database Migrations
Set up local SQLite database tables:

Bash
python manage.py migrate
6. Create Superuser (Optional - For Django Admin access)
Bash
python manage.py createsuperuser
7. Run Development Server
Start the local development server:

Bash
python manage.py runserver
Open your web browser and navigate to:

Plaintext
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
🌿 Version Control & Branching Strategy
Development follows feature-branch workflows. Main changes are pushed to designated working branches before merging into main.

Active Branch
dynamic-version — Holds the dynamic Django multi-page refactor.

main — Production release branch.

👤 Author & Design Credits
Institution: Wama Training Institute (WTI) — Ongata Rongai, Kenya

Platform Architect: Pixel Architect
