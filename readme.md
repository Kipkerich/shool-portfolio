# School Portfolio - Wama Training Institute

A professional, responsive, and dynamic Django web application built for **Wama Training Institute** - a premier healthcare education institution dedicated to advancing medical knowledge and producing highly skilled healthcare professionals.

---

## 🌟 Features

- **Responsive Design** - Optimized for desktop, tablet, and mobile viewing with clean, semantic Bootstrap 5 markup.
- **Dynamic Course Catalog** - Beautiful course display cards with status badges indicating whether program applications are **OPEN** or **CLOSED**.
- **Admin Dashboard Integration** - Fully registered courses, application fields, and student submissions within Django Admin. Toggles for program status are editable on-the-fly.
- **Dynamic Application Forms** - Blocks submissions and shows a clean, user-friendly "Applications Closed" banner when any course is set to closed.
- **Secure Contact Form** - Built-in contact form delivering messages directly to `wamatraininginstitute@gmail.com` using Django's email configuration.
- **Professional Branding** - Cohesive color styling centered around gold/brown (`#956c34` and `#f5a425`) and navy blue (`#07244b`).
- **Interactive Google Maps** - Responsive map view pointing directly to the campus at *Ongata Rongai, Tyme Suite, 5th Floor*.

---

## 🛠️ Tech Stack

- **Backend:** Python / Django 6.x
- **Frontend:** Bootstrap 5, Font Awesome Icons, Owl Carousel (optional)
- **Database:** SQLite (default/development) / MySQL (production-ready)
- **Email:** Django standard `send_mail` via configured SMTP backends

---

## 📁 Project Directory Structure

```text
wama-training-institute/
│
├── readme.md                   # Repository documentation & guide
├── assets/                     # Frontend vendor stylesheets, scripts, and fonts
└── wti_project/                # Django project directory
    ├── db.sqlite3              # Local development database
    ├── manage.py               # Django task runner cli
    ├── core/                   # Main application module
    │   ├── admin.py            # Model registration and customization
    │   ├── models.py           # Database models (Course, FAQ, Blog, Submission)
    │   ├── views.py            # Route controller actions (Home, Contact, Course details)
    │   ├── tests.py            # Comprehensive Unit and Integration tests
    │   └── templates/          # HTML Templates (index, contact, courses, apply, details)
    └── wti_project/            # Main project configuration
        ├── settings.py         # App settings & credentials
        ├── urls.py             # Route configuration
        └── wsgi.py             # WSGI web server config
```

---

## 🚀 Local Development Setup

Follow these steps to run the application locally on your machine:

### 1. Clone the repository and navigate to the Django directory
```bash
cd wti_project
```

### 2. Create and activate a Python virtual environment
```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows (cmd):
venv\Scripts\activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```
*(If a `requirements.txt` is not provided, make sure Django is installed: `pip install Django`)*

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser
Create a local admin user to access and manage the database models:
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser to view the application. Access the administrative portal at `http://127.0.0.1:8000/admin/`.

---

## 🧪 Running Tests

A comprehensive suite of Django unit and integration tests has been implemented to verify form submission, course application closures, visual rendering context, and administrative features.

To execute the test suite:
```bash
cd wti_project
python manage.py test
```

---

## 📦 Guide: Deploying the Django Application to cPanel

Most shared/reseller cPanel hosting services support Python applications using **CloudLinux's LVE Manager** (usually labeled as **Setup Python App** or **Python Selector**). Follow this comprehensive deployment guide to set up your site.

### Step 1: Prepare Your Django Project for Production
Before uploading, make these changes in your production settings file (`wti_project/wti_project/settings.py`):

1. **Disable Debug Mode:**
   ```python
   DEBUG = False
   ```
2. **Set Allowed Hosts:**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```
3. **Configure Static Files:**
   Set `STATIC_ROOT` so Django knows where to collect assets:
   ```python
   STATIC_ROOT = os.path.join(BASE_DIR, 'public_html/static')
   # Or a folder inside the project directories
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

### Step 2: Create a Python Application in cPanel
1. Log in to your cPanel dashboard.
2. Search for and click **Setup Python App** in the *Software* category.
3. Click the **Create Application** button.
4. Set the following parameters:
   - **Python Version:** Choose `3.10` or newer.
   - **Application root:** Enter the path where you will upload your project files (e.g., `wama-app` or `public_html/wama-app`).
   - **Application URL:** Select your domain (e.g., `yourdomain.com`).
   - **Application startup file:** Enter `passenger_wsgi.py`.
   - **Application Entry point:** Enter `application`.
5. Click **Create**. This will initialize the virtual environment and create a basic `passenger_wsgi.py` in your application root folder.

### Step 3: Upload Project Files
Use cPanel's **File Manager** or an **FTP client** (like FileZilla) to upload your project directory to the specified *Application root* folder.

### Step 4: Configure the `passenger_wsgi.py`
cPanel runs Python apps using Phusion Passenger. You must redirect Passenger to Django's WSGI instance. Overwrite the autogenerated `passenger_wsgi.py` inside your application root with the following snippet:

```python
import os
import sys

# Define the paths. Replace 'wama-app' with your actual cPanel application root directory name.
sys.path.insert(0, '/home/YOUR_CPANEL_USERNAME/wama-app/wti_project')

# Set settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'wti_project.settings'

# Import Django application handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

*(Ensure to replace `YOUR_CPANEL_USERNAME` with your real cPanel hosting username, and verify path directories match).*

### Step 5: Setup MySQL Database on cPanel & Update Django DB Configurations

To transition your database from SQLite to a robust production **MySQL** database on cPanel, follow these steps exactly:

#### 1. Create a MySQL Database in cPanel
1. Navigate to your cPanel dashboard and find the **Databases** category.
2. Click on **MySQL® Database Wizard**.
3. **Step 1 (Create a Database):** Enter a name for your database (e.g., `wama_db`) and click **Next Step**.
4. **Step 2 (Create Database Users):** Enter a username (e.g., `wama_user`) and a secure password. Make sure to note this password down securely. Click **Create User**.
5. **Step 3 (Add User to Database):** Tick the checkbox for **ALL PRIVILEGES** to give your database user complete access, then scroll down and click **Next Step** / **Make Changes**.
6. Note down the full database name and user name. In cPanel, these are usually prefixed with your cPanel hosting username (e.g., `mycpaneluser_wama_db` and `mycpaneluser_wama_user`).

#### 2. Install MySQL Database Adapters in cPanel Virtual Environment
1. To connect Python/Django to MySQL, you need a MySQL adapter such as `mysqlclient` or `pymysql`. We recommend `pymysql` as it is easy to install without compiling external binary libraries on shared servers.
2. Access cPanel's **Terminal** and activate your application's virtual environment (as shown in **Step 2**).
3. Install `pymysql` using pip:
   ```bash
   pip install pymysql
   ```
4. Tell Django to use `pymysql` as the MySQL connector by adding the following code at the very top of `wti_project/wti_project/__init__.py`:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

#### 3. Update Django `DATABASES` Settings
In your Django project's `wti_project/wti_project/settings.py`, replace the SQLite database configuration block:

```python
# REMOVE OR COMMENT OUT:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ADD MYSQL DATABASE CONFIGURATION:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mycpaneluser_wama_db',       # Full database name from MySQL Database Wizard
        'USER': 'mycpaneluser_wama_user',     # Full database username
        'PASSWORD': 'YourSecureDBPassword!',  # The secure password you chose
        'HOST': 'localhost',                  # 'localhost' is default for most shared cPanel hosts
        'PORT': '3306',                       # Default MySQL port
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### Step 6: Install Dependencies in Virtual Environment
1. Back in cPanel's **Setup Python App**, copy the virtual environment activation command displayed at the top of the page.
2. Open cPanel's **Terminal** tool and run that copied command to enter the virtual environment.
3. Navigate to your project directory and install the requirements:
   ```bash
   cd ~/wama-app/wti_project
   pip install django sqlparse asgiref pymysql
   ```

### Step 7: Configure SMTP Email in Production
In production, Django must authenticate with an active SMTP mail server to send messages from the Contact Form. Create an email account in cPanel (e.g., `info@yourdomain.com`) and update your settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.yourdomain.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'info@yourdomain.com'
EMAIL_HOST_PASSWORD = 'YourEmailPassword123!'
DEFAULT_FROM_EMAIL = 'Wama Training Institute <info@yourdomain.com>'
```

### Step 8: Gather Static Files and Migrate Database
While active in the virtual environment inside cPanel's terminal:

1. **Run Database Migrations (This will generate MySQL database tables):**
   ```bash
   python manage.py migrate
   ```
2. **Collect All Static Assets:**
   ```bash
   python manage.py collectstatic --noinput
   ```
3. **Create your Administrative User:**
   ```bash
   python manage.py createsuperuser
   ```

### Step 9: Finalize and Test
1. In the **Setup Python App** panel, click **Restart** to apply all modifications.
2. Navigate to your website URL. Your Django application is now fully running on cPanel using MySQL!
3. Go to `/admin` to verify that database tables (`Course`, `ApplicationField`, etc.) are fully visible.
4. Try submitting the Contact Page form to verify successful SMTP delivery.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- Template styled with inspiration from [TemplateMo Grad School](https://templatemo.com/tm-557-grad-school).
- Icons provided by [Font Awesome](https://fontawesome.com).
- Forms backed with native Django processing and robust testing logic.
