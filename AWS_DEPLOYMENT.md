# Wama Training Institute: AWS Cloud Architecture and Deployment Guideline (AWS Free Tier Optimized)

This document provides a comprehensive, production-grade guideline for designing the architecture and deploying the **Wama Training Institute (WTI)** Django application to **Amazon Web Services (AWS)**.

To help minimize operational expenses, this specific guide is optimized for the **AWS Free Tier**, ensuring you can host this Django application with **$0/month in AWS hosting fees** under the standard 12-month AWS Free Tier eligibility.

---

## 🏛️ 1. Free-Tier AWS Cloud Architecture

Standard enterprise Multi-AZ architectures use multiple NAT Gateways and multi-AZ RDS database deployments, which incur significant non-free hourly charges (typically $30–$100+/month).

Our optimized architecture uses **100% Free Tier Eligible components**:
*   **Compute:** Single **t2.micro / t3.micro** EC2 instance (750 hours/month free).
*   **Database:** Single-AZ **db.t3.micro** RDS MySQL database (750 hours/month free).
*   **Storage & CDN:** Amazon S3 (5 GB free) and Amazon CloudFront (1 TB/month transfer free).
*   **Zero NAT Gateways:** Both the EC2 web server and RDS database are deployed in public/isolated subnets with strict Security Groups. The RDS database is set to **Publicly Accessible: No**, meaning it can only be accessed by the EC2 instance, securing your database without expensive NAT Gateways.

### Architecture Diagram (Logical Flow)
```text
                  ┌────────────────────────────────────────┐
                  │               Route 53                 │ (DNS routing)
                  └───────────────────┬────────────────────┘
                                      │ (HTTPS)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         CloudFront CDN                 │ <─── Static/Media assets in S3
                  └───────────────────┬────────────────────┘
                                      │ (HTTPS on port 443)
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VPC (Single AZ)                                      │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                              Public Subnet                                     │   │
│   │                                                                                │   │
│   │  ┌───────────────────────┐              ┌───────────────────────────────────┐  │   │
│   │  │   EC2 Instance        │◄────────────►│       RDS MySQL DB Instance       │  │   │
│   │  │ (t2.micro/t3.micro)   │ (Port 3306)  │       (db.t3.micro, Single-AZ)    │  │   │
│   │  │  - Docker / Gunicorn  │              │       - Publicly Accessible: NO   │  │   │
│   │  │  - Nginx Reverse Proxy│              │       - Strict wti-rds-sg         │  │   │
│   │  └───────────────────────┘              └───────────────────────────────────┘  │   │
│   │                                                                                │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 🛠️ Key AWS Services & Roles (Free Tier Optimized)
1. **Amazon Route 53**: Handles Domain Name System (DNS) records (Note: Route 53 is not fully free, costing $0.50/month per hosted zone, but represents the lowest possible DNS cost).
2. **AWS Certificate Manager (ACM)**: Manages SSL/TLS certificates for HTTPS (100% free).
3. **Amazon CloudFront**: Caches static and media assets globally (Up to 1 TB of outbound data transfer per month is free).
4. **Amazon S3 (Simple Storage Service)**: Stores static web files (`/static/`) and user-uploaded media files (`/media/`) (5 GB of Standard storage, 20,000 GET requests, and 2,000 PUT requests are free per month).
5. **Amazon VPC (Virtual Private Cloud)**: Provides a virtual isolated network (100% free).
6. **Amazon EC2 Instance (`t2.micro` or `t3.micro` depending on region)**: Runs the Dockerized Django app (750 hours/month free).
7. **Amazon RDS for MySQL (`db.t3.micro`, Single-AZ)**: Handles database records (750 hours/month free, 20 GB of General Purpose SSD storage, and 20 GB of automated database backups are free).
8. **AWS Systems Manager Parameter Store**: Securely stores environment variables and keys (Free standard tier).

---

## 📦 2. Application Dockerization

To simplify deployment and keep the environment clean, we containerize our Django application.

### `Dockerfile`
Create a `Dockerfile` in the root of your project directory (`/wti_project/`):

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Use gunicorn to serve the app
CMD ["gunicorn", "wti_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### `.dockerignore`
Ensure development and sensitive files are not copied into the Docker image:

```text
.git
__pycache__
*.pyc
db.sqlite3
venv/
.env
runserver.log
```

---

## 🛡️ 3. Settings Configuration for AWS S3 & CloudFront

Update Django settings in `wti_project/settings.py` to support S3 storage and CloudFront.

### S3 Backend Storage Configuration

1. Install required packages:
   ```bash
   pip install django-storages boto3
   ```

2. Add `'storages'` to `INSTALLED_APPS` in `settings.py`.
3. Add the following configurations in `settings.py`:

```python
import os

# AWS S3 Settings
USE_AWS = os.getenv('USE_AWS', 'False') == 'True'

if USE_AWS:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-west-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # Static files settings
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

    # Media files settings
    DEFAULT_FILE_STORAGE = 'wti_project.storage_backends.MediaStorage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    STATIC_URL = 'static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_URL = 'media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

4. Create a `storage_backends.py` file to handle separate media and static locations:

```python
# wti_project/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
```

### Production Security Settings in `settings.py`

```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# SSL and Security Configuration (Only when running behind CloudFront HTTPS)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## 🚀 4. Step-by-Step Free-Tier Deployment Walkthrough

Below are the steps to deploy the application without incurring costs.

### Step 4.1: Network Setup (VPC)
1. Navigate to the **VPC Console** on AWS.
2. Click **Create VPC** -> select **VPC and more**.
   - **Name tag**: `wti-free-vpc`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Number of Availability Zones (AZs)**: `1` (Selecting 1 AZ keeps resource usage inside the free tier).
   - **Number of Public Subnets**: `1`
   - **Number of Private Subnets**: `0`
   - **NAT Gateways**: **None** (Selecting None avoids a charges of $30+/month).
3. Click **Create VPC**.

### Step 4.2: Security Groups Setup
Create two security groups within `wti-free-vpc`:
1. **EC2 Instance Security Group (`wti-ec2-sg`)**:
   - **Inbound Rules**:
     - HTTP (80) from `0.0.0.0/0`.
     - HTTPS (443) from `0.0.0.0/0`.
     - SSH (22) from **My IP** (secures server access).
   - **Outbound Rules**: All Traffic to anywhere.
2. **RDS Database Security Group (`wti-rds-sg`)**:
   - **Inbound Rules**: TCP Port 3306 (MySQL) only from `wti-ec2-sg`.
   - **Outbound Rules**: None.

### Step 4.3: Database Setup (Amazon RDS - Free Tier)
1. Go to the **RDS Console** and click **Create database**.
2. Select **Standard create** -> **MySQL**.
3. Under **Templates**, select **Free Tier** (Crucial: This automatically provisions a Single-AZ `db.t3.micro` with General Purpose SSD storage, completely covered by the free tier).
4. Set credentials:
   - **DB instance identifier**: `wti-free-db`
   - **Master username**: `wticontrol_dbuser`
   - **Master password**: [Provide a strong, secure password]
5. Under **Connectivity**:
   - Select your newly created VPC (`wti-free-vpc`).
   - **Publicly Accessible**: **No** (This ensures no one on the internet can connect directly to your database).
   - Select security group `wti-rds-sg`.
6. Click **Create Database**. Note the endpoint URL once active.

### Step 4.4: Storage Setup (Amazon S3 & CloudFront)
1. Go to the **S3 Console** and click **Create bucket**.
2. Name it (e.g., `wama-training-institute-assets-free`).
3. Set properties:
   - Uncheck **Block all public access** (for static/media files).
4. Go to **Amazon CloudFront** and click **Create distribution**.
5. Set the Origin Domain to your S3 bucket endpoint.
6. Under **Viewer Protocol Policy**, choose **Redirect HTTP to HTTPS**.
7. Click **Create Distribution**.

### Step 4.5: Domain & SSL Setup (AWS Certificate Manager)
1. Open the **AWS Certificate Manager (ACM)** console.
2. Click **Request a public certificate** for your domains (e.g., `wamatraining.edu`, `www.wamatraining.edu`).
3. Complete DNS validation using your domain name registrar or Route 53.
4. Point your domain DNS records to the CloudFront distribution domain name.

### Step 4.6: Compute Server Setup (EC2 Instance - Free Tier)
1. Go to the **EC2 Console** and click **Launch Instance**.
2. Set configuration details:
   - **Name**: `wti-web-server`
   - **AMI**: **Ubuntu Server 24.04 LTS (Free Tier Eligible)**.
   - **Instance Type**: **t2.micro** (or **t3.micro** depending on region availability; ensure it says **Free Tier Eligible**).
   - **Key Pair**: Create or select an existing key pair for SSH access.
   - **Network Settings**:
     - VPC: `wti-free-vpc`.
     - Subnet: Public subnet.
     - Auto-assign public IP: **Enable**.
     - Security Group: Choose `wti-ec2-sg`.
3. Click **Launch Instance**.

---

## 🛠️ 5. Provisioning the EC2 Web Server

Connect to your EC2 instance via SSH and configure the environment:

```bash
# Connect using your key pair
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install -y docker.io docker-compose

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group so you don't need sudo for docker commands
sudo usermod -aG docker ubuntu
# (Log out and log back in to apply docker group permissions)
exit
ssh -i "your-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## 📁 6. Simple Deployment Workflow on EC2

To host the application without the need for an expensive private container registry, we can run the application directly using a simple `docker-compose.yml` file.

### Step 6.1: Create `.env` on EC2
Create a file named `.env` in your app folder on EC2 (`/home/ubuntu/app/`) to securely hold variables:

```text
SECRET_KEY=YOUR_DJANGO_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=YOUR_EC2_PUBLIC_IP,YOUR_DOMAIN_NAME
DATABASE_URL=mysql://wticontrol_dbuser:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:3306/wti_db
USE_AWS=True
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME=wama-training-institute-assets-free
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Step 6.2: Create `docker-compose.yml` on EC2
Create `docker-compose.yml` in `/home/ubuntu/app/`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
    restart: always
```

### Step 6.3: Create Nginx Configuration
Create `nginx.conf` in `/home/ubuntu/app/`:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_NAME_OR_IP;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 6.4: Clone & Launch App
Clone the repository onto the EC2 instance, copy your configurations (`.env`, `docker-compose.yml`, `nginx.conf`) into the project directory, and launch the services:

```bash
cd /home/ubuntu/app/
docker-compose up -d --build
```

### Step 6.5: Database Migrations and Admin Account
Run migrations and create the administrative superuser within the running docker container:

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create django superuser
docker-compose exec web python manage.py createsuperuser
```

---

## 📈 7. Post-Deployment Optimization & Free-Tier Monitoring

To ensure you stay 100% within the free tier limit:
1. **Set AWS Billing Alarms**: Go to **Billing and Cost Management** console and create a billing alarm to notify you via email if your monthly AWS charges exceed $0.50.
2. **Monitor EC2 Disk Usage**: Do not exceed 30 GB of total EBS disk storage space across all active EC2 instances.
3. **Database Automated Backups**: Free Tier includes 20 GB of RDS backups. Ensure backup retention period is set to 7 days or less to prevent storage overruns.
