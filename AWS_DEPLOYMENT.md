# Wama Training Institute: AWS Cloud Architecture and Deployment Guideline

This document provides a comprehensive, production-grade guideline for designing the architecture and deploying the **Wama Training Institute (WTI)** Django application to **Amazon Web Services (AWS)**. It is structured to ensure high availability, scalability, robust security, and cost-efficiency.

---

## 🏛️ 1. Target AWS Cloud Architecture

Our target architecture utilizes modern, secure cloud design principles. It employs a **Multi-Availability Zone (Multi-AZ)** VPC setup, separating our application tiers into public and private subnets, leveraging container orchestration via **AWS ECS Fargate**, and utilizing managed storage and database services.

### Architecture Diagram (Logical Flow)
```text
                  ┌────────────────────────────────────────┐
                  │               Route 53                 │
                  └───────────────────┬────────────────────┘
                                      │ (HTTPS)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │         CloudFront CDN                 │ <─── Static/Media assets in S3
                  └───────────────────┬────────────────────┘
                                      │ (HTTPS)
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VPC (Multi-AZ)                                       │
│                                                                                        │
│   ┌───────────────────────────────┐        ┌───────────────────────────────┐           │
│   │     Public Subnet (AZ-A)      │        │     Public Subnet (AZ-B)      │           │
│   │                               │        │                               │           │
│   │  ┌─────────────────────────┐  │        │  ┌─────────────────────────┐  │           │
│   │  │ Application Load Bal.   │◄─┼────────┼─►│ Application Load Bal.   │  │           │
│   │  │         (ALB)           │  │        │  │         (ALB)           │  │           │
│   │  └────────────┬────────────┘  │        │  └────────────┬────────────┘  │           │
│   │               │               │        │               │               │           │
│   │               │               │        │               │               │           │
│   │               ▼               │        │               ▼               │           │
│   │          NAT Gateway          │        │          NAT Gateway          │           │
│   └───────────────┬───────────────┘        └───────────────┬───────────────┘           │
│                   │                                        │                           │
│                   ▼                                        ▼                           │
│   ┌───────────────────────────────┐        ┌───────────────────────────────┐           │
│   │     Private Subnet (AZ-A)     │        │     Private Subnet (AZ-B)     │           │
│   │                               │        │                               │           │
│   │  ┌─────────────────────────┐  │        │  ┌─────────────────────────┐  │           │
│   │  │    ECS Fargate Task     │  │        │  │    ECS Fargate Task     │  │           │
│   │  │  (Django Web / Gunicorn)│  │        │  │  (Django Web / Gunicorn)│  │           │
│   │  └────────────┬────────────┘  │        │  └────────────┬────────────┘  │           │
│   │               │               │        │               │               │           │
│   └───────────────┼───────────────┘        └───────────────┼───────────────┘           │
│                   │                                        │                           │
│                   ▼                                        ▼                           │
│   ┌───────────────────────────────┐        ┌───────────────────────────────┐           │
│   │    Database Subnet (AZ-A)     │        │    Database Subnet (AZ-B)     │           │
│   │                               │        │                               │           │
│   │  ┌─────────────────────────┐  │        │  ┌─────────────────────────┐  │           │
│   │  │    RDS MySQL Master     │◄─┼────────┼─►│   RDS MySQL Standby     │  │           │
│   │  └─────────────────────────┘  │        │  └─────────────────────────┘  │           │
│   └───────────────────────────────┘        └───────────────────────────────┘           │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 🛠️ Key AWS Services & Roles
1. **Amazon Route 53**: Highly available Domain Name System (DNS) service to route users to the CloudFront distribution or Application Load Balancer.
2. **AWS Certificate Manager (ACM)**: Manages SSL/TLS certificates for secure HTTPS communication.
3. **Amazon CloudFront**: Content Delivery Network (CDN) to cache static and media files globally, reducing latency and offloading traffic from the Django container instances.
4. **Amazon S3 (Simple Storage Service)**: Secure, durable object storage for Django static files (`/static/`) and user-uploaded files (`/media/`, such as blog images, course banners, and application documents).
5. **Amazon VPC (Virtual Private Cloud)**: Segmented virtual network with:
   - **Public Subnets**: House the Application Load Balancer (ALB) and NAT Gateways.
   - **Private Subnets**: House the ECS Fargate Tasks (Django web servers). This ensures the application instances cannot be reached directly from the internet, drastically reducing the attack surface.
   - **Database Subnets**: Isolated subnets holding the RDS instances, allowing connections only from the private application subnets.
6. **Application Load Balancer (ALB)**: Distributes incoming HTTPS traffic across multiple ECS container instances running across different Availability Zones. Offers built-in health-checks and handles SSL termination.
7. **AWS ECS (Elastic Container Service) with Fargate**: A serverless compute engine for containers. It runs Dockerized Django applications automatically scaling up or down based on traffic load (CPU/Memory utilization).
8. **Amazon RDS for MySQL**: Managed relational database running in a Multi-AZ configuration for automatic failover, automated snapshots, and minor engine updates.
9. **Amazon ElastiCache (Redis)**: Optional, high-performance in-memory caching and session store.
10. **AWS Secrets Manager / Systems Manager Parameter Store**: Securely stores environment variables and secrets (e.g., `SECRET_KEY`, database credentials, Paystack APIs, Formspree keys).
11. **AWS IAM (Identity and Access Management)**: Enforces fine-grained access control using the principle of least privilege.

---

## 📦 2. Application Dockerization

To deploy to AWS ECS Fargate, we must containerize our Django application.

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

# Collect static files (optional here, but best practice for S3 storage configuration)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Use gunicorn to serve the app
CMD gunicorn wti_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
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

## 🛡️ 3. Settings Configuration for Production AWS Deployment

Update Django settings in `wti_project/settings.py` to support AWS services.

### S3 Backend Storage Configuration
Using `django-storages` is standard practice for saving static and media files directly to S3.

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
Ensure production flags are updated:

```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# SSL and Security Configuration (Only when running behind ALB HTTPS)
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

## 🚀 4. Step-by-Step AWS Deployment Walkthrough

Below are the operational steps to set up and deploy the architecture.

### Step 4.1: Network Setup (VPC, Subnets, and Gateways)
1. Navigate to the **VPC Console** on AWS.
2. Click **Create VPC** and select **VPC and more** (this configures a Multi-AZ environment automatically).
3. Set the configuration details:
   - **Name tag**: `wti-vpc`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Number of Availability Zones (AZs)**: `2` (e.g., `us-east-1a` and `us-east-1b` for high availability)
   - **Number of Public Subnets**: `2`
   - **Number of Private Subnets**: `2`
   - **NAT Gateways**: `1 per AZ` (recommended for production) or `1 in 1 AZ` (to save cost)
   - **VPC Endpoints**: S3 Gateway (improves speed and cost for accessing S3 buckets directly from private subnets).
4. Click **Create VPC**.

### Step 4.2: Security Groups Setup
Create four security groups within the `wti-vpc`:
1. **ALB Security Group (`wti-alb-sg`)**:
   - **Inbound Rules**: HTTP (80) and HTTPS (443) from `0.0.0.0/0`.
   - **Outbound Rules**: All Traffic to anywhere.
2. **ECS Tasks Security Group (`wti-ecs-sg`)**:
   - **Inbound Rules**: TCP Port 8000 (or custom Django port) only from `wti-alb-sg`.
   - **Outbound Rules**: All Traffic to anywhere (needed to call Paystack APIs, Formspree, pull Docker images, etc.).
3. **RDS Database Security Group (`wti-rds-sg`)**:
   - **Inbound Rules**: TCP Port 3306 (MySQL) or 5432 (PostgreSQL) only from `wti-ecs-sg`.
   - **Outbound Rules**: None.

### Step 4.3: Database Setup (Amazon RDS)
1. Go to the **RDS Console** and click **Create database**.
2. Select **Standard create** -> **MySQL** (or PostgreSQL if preferred).
3. Under **Templates**, choose **Production** (Multi-AZ for high availability) or **Dev/Test** (Single instance to save cost).
4. Set credentials and identifier:
   - **DB instance identifier**: `wti-production-db`
   - **Master username**: Choose a secure master username (e.g., `wticontrol_dbuser`).
   - **Master password**: Generate a secure password and store it in AWS Secrets Manager.
5. Under **Connectivity**:
   - Select your newly created VPC (`wti-vpc`).
   - Ensure the database is placed in **Private Subnets** (Public access: No).
   - Select the security group `wti-rds-sg`.
6. Click **Create Database**. Once provisioned, note down the endpoint URL.

### Step 4.4: Storage Setup (Amazon S3 & CloudFront)
1. Go to the **S3 Console** and click **Create bucket**.
2. Set Bucket Name (e.g., `wama-training-institute-assets`).
3. Set properties:
   - Uncheck **Block all public access** (since static web elements and media files need to be publicly accessible, or use CloudFront Origin Access Identities for private S3 access).
   - Keep bucket versioning **Enabled** (for backups/restoration).
4. Go to **Amazon CloudFront** and click **Create distribution**.
5. Set the Origin Domain to your S3 bucket endpoint.
6. Configure caching policies and forward headers if required.
7. Under **Viewer Protocol Policy**, choose **Redirect HTTP to HTTPS**.
8. Click **Create Distribution**.

### Step 4.5: Certificate Management (ACM) & Domain Setup
1. Open the **AWS Certificate Manager (ACM)** console.
2. Click **Request a certificate** -> **Request a public certificate**.
3. Add your domains (e.g., `wamatraining.edu`, `www.wamatraining.edu`).
4. Select **DNS validation** (recommended).
5. AWS will generate CNAME records. Add these records in your **Route 53** host zone or external domain registrar to complete SSL verification.

### Step 4.6: Docker Image Repository (Amazon ECR)
1. Open the **Amazon ECR (Elastic Container Registry)** console.
2. Click **Create repository**.
3. Name it `wti-django-app` and keep the visibility settings as **Private**.
4. Click on your repository and click **View push commands**. Run those commands in your CI/CD pipeline or local console to authenticate Docker, build the container, tag it, and push it to ECR:
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
   docker build -t wti-django-app .
   docker tag wti-django-app:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/wti-django-app:latest
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/wti-django-app:latest
   ```

### Step 4.7: Load Balancer (ALB) Configuration
1. Open the **EC2 Console** and click on **Load Balancers** -> **Create Load Balancer** -> **Application Load Balancer**.
2. Name it `wti-alb`.
3. Under Network mapping, select `wti-vpc` and choose your **Public Subnets** (at least two AZs).
4. Assign the security group `wti-alb-sg`.
5. Under Listeners and routing:
   - Create listener on HTTP (Port 80), configured to redirect to HTTPS (443).
   - Create listener on HTTPS (Port 443), forwarding to a new **Target Group** (e.g., `wti-target-group`).
   - In listener settings, select the SSL Certificate created in ACM.
6. Target Group (`wti-target-group`) Configuration:
   - Target Type: **IP addresses** (required for ECS Fargate).
   - Port: 8000.
   - Health check path: `/` or a dedicated health check endpoint like `/health/` or `/about/`.

### Step 4.8: AWS ECS Fargate Cluster & Task Definition
1. Open the **Elastic Container Service (ECS)** console.
2. Click **Create Cluster**, choose **Fargate (Serverless)**, and name it `wti-cluster`.
3. Navigate to **Task Definitions** -> **Create new Task Definition** with JSON or Console:
   - **Infrastructure requirements**: AWS Fargate, operating system/architecture Linux/X86_64.
   - **Task size**: CPU (`0.5 vCPU` or `1 vCPU`), Memory (`1 GB` or `2 GB`).
   - **Task execution role**: Ensure the role has access to pull from ECR and read from SSM Parameter Store / Secrets Manager.
   - **Container definition**:
     - **Name**: `django-web`
     - **Image URL**: Point to your Amazon ECR URI (e.g., `<aws_account_id>.dkr.ecr.<region>.amazonaws.com/wti-django-app:latest`).
     - **Port mappings**: Container Port 8000 (TCP).
     - **Environment variables**: Use AWS Secret manager integrations to inject variables securely:
       - `SECRET_KEY`
       - `DEBUG` = `False`
       - `ALLOWED_HOSTS` = `YOUR_ALB_DOMAIN,YOUR_CUSTOM_DOMAIN`
       - `DATABASE_URL` = `mysql://wticontrol_dbuser:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:3306/wti_db`
       - `PAYSTACK_PUBLIC_KEY`, `PAYSTACK_SECRET_KEY`
       - `EMAIL_BACKEND` = `'django.core.mail.backends.smtp.EmailBackend'` (and secure credentials)
       - `USE_AWS` = `True`
       - `AWS_STORAGE_BUCKET_NAME` = `wama-training-institute-assets`
4. Click **Create**.

### Step 4.9: Creating the ECS Service
1. Inside your `wti-cluster`, go to **Services** -> **Create**.
2. Configure settings:
   - Launch type: **Fargate**.
   - Deployment configuration: Service.
   - Task definition family: Select `wti-django-app` task created above.
   - Service name: `wti-django-service`.
   - Desired tasks: `2` (ensures high availability across AZs).
3. Under **Networking**:
   - VPC: `wti-vpc`.
   - Subnets: Choose the **Private Subnets**.
   - Security Group: Choose `wti-ecs-sg`.
   - Public IP: Ensure **Disabled** (traffic must flow via ALB, not directly).
4. Under **Load Balancing**:
   - Load balancer type: Application Load Balancer.
   - Select your existing `wti-alb`.
   - Choose target group `wti-target-group`.
5. Under **Service Auto Scaling** (Optional):
   - Set policies to scale based on Average CPU Utilization exceeding 70%.
6. Click **Create Service**.

---

## 🛠️ 5. Database Migrations and Admin Setup on AWS ECS

Running migrations and creating a superuser on a containerized, serverless Fargate cluster requires run-task controls.

### Running Initial Migrations
Once the database container is connected, run a one-off task using the AWS CLI or ECS Console:

```bash
# Run one-off task to migrate database tables
aws ecs run-task \
    --cluster wti-cluster \
    --task-definition wti-django-app \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<PRIVATE_SUBNET_1>,<PRIVATE_SUBNET_2>],securityGroups=[<ECS_SG>],assignPublicIp=DISABLED}" \
    --overrides '{"containerOverrides": [{"name": "django-web", "command": ["python", "manage.py", "migrate"]}]}'
```

### Creating the Django Superuser on Cloud Database
Run a one-off task with interactive overrides or custom python shell execution:

```bash
aws ecs run-task \
    --cluster wti-cluster \
    --task-definition wti-django-app \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<PRIVATE_SUBNET_1>,<PRIVATE_SUBNET_2>],securityGroups=[<ECS_SG>],assignPublicIp=DISABLED}" \
    --overrides '{"containerOverrides": [{"name": "django-web", "command": ["python", "manage.py", "shell", "-c", "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('\''cloudadmin'\'', '\''admin@wamatraining.edu'\'', '\''SecurePassword1234'\'')"]}]}'
```

---

## 🔄 6. Continuous Integration & Deployment (CI/CD) with GitHub Actions

Automating your builds ensures that changes to the Django app are immediately tested and pushed safely to ECS.

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Amazon ECS

on:
  push:
    branches:
      - main

env:
  AWS_REGION: eu-west-1
  ECR_REPOSITORY: wti-django-app
  ECS_SERVICE: wti-django-service
  ECS_CLUSTER: wti-cluster
  ECS_TASK_DEFINITION: .aws/task-definition.json
  CONTAINER_NAME: django-web

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    environment: production

    steps:
    - name: Checkout Code
      uses: actions/checkout@v3

    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, Tag, and Push Image to ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Fill in the new image ID in the Amazon ECS task definition
      id: task-def
      uses: aws-actions/amazon-ecs-render-task-definition@v1
      with:
        task-definition: ${{ env.ECS_TASK_DEFINITION }}
        container-name: ${{ env.CONTAINER_NAME }}
        image: ${{ steps.build-image.outputs.image }}

    - name: Deploy Amazon ECS task definition
      uses: aws-actions/amazon-ecs-deploy-task-definition@v1
      with:
        task-definition: ${{ steps.task-def.outputs.task-definition }}
        service: ${{ env.ECS_SERVICE }}
        cluster: ${{ env.ECS_CLUSTER }}
        wait-for-service-stability: true
```

---

## 📈 7. Post-Deployment Optimization & Monitoring

To keep WWT applications performant and healthy under load:
1. **Amazon CloudWatch**: Set up metric alarms monitoring CPU & Memory utilization of your ECS service tasks, HTTP response counts, and 5XX server errors on ALB.
2. **Database Backups**: Schedule automated nightly snapshots in RDS with at least 7 days of retention.
3. **Route 53 Failover Routing**: Optionally connect Route 53 to health checks to redirect users to a custom maintenance page or secondary region if the primary site experiences down-time.
4. **Log Forwarding**: Configure AWS firelens or configure default CloudWatch logging backend on Task Definitions to capture standard `gunicorn` or python logging streams.
