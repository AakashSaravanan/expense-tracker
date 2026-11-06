# Cloud-Based Personal Expense Tracker

A cloud-based personal expense management application built using **Python Flask, MySQL, Docker, and AWS**. The application helps users manage their income and expenses through a web-based interface, while leveraging AWS cloud infrastructure for application hosting, database management, and container deployment.

## Overview

The Cloud-Based Personal Expense Tracker is a full-stack web application designed to simplify personal financial management. It provides a centralized platform for managing financial transactions, organizing expenses, and monitoring financial activities.

The application is developed using Flask and Bootstrap, containerized with Docker, and deployed using AWS services. It uses Amazon RDS for managed MySQL database hosting, Amazon ECR for Docker image storage, and Amazon EC2 for running the containerized application.

## Key Features

- **User Authentication:** User registration and login functionality for accessing the application.
- **Expense Management:** Add, view, edit, and delete financial transactions.
- **Income and Expense Tracking:** Maintain financial records by managing income and expense transactions.
- **Dashboard:** Access the expense tracker through a centralized dashboard.
- **Receipt Management:** Attach and view transaction receipts.
- **Responsive Interface:** User-friendly interface developed using HTML, CSS, JavaScript, and Bootstrap.
- **Cloud-Based Infrastructure:** Utilizes AWS services to host the application and manage its database.
- **Containerization:** Docker packages the application and its dependencies into a portable container.
- **Secure Configuration Management:** AWS Systems Manager Parameter Store manages sensitive application configuration values.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Database | MySQL |
| ORM | SQLAlchemy |
| Containerization | Docker |
| Application Server | Gunicorn |
| Cloud Platform | Amazon Web Services (AWS) |
| Compute | Amazon EC2 |
| Database Hosting | Amazon RDS |
| Container Registry | Amazon ECR |
| Configuration Management | AWS Systems Manager Parameter Store |

## System Architecture

The application follows a containerized cloud deployment architecture using AWS services.

### Architecture Components

1. **Amazon EC2:** Hosts the Flask application inside a Docker container using an Ubuntu-based instance.
2. **Docker:** Packages the Flask application and its dependencies into a container.
3. **Amazon ECR:** Stores the Docker images used for application deployment.
4. **Amazon RDS:** Provides a managed MySQL database for application data.
5. **AWS Systems Manager Parameter Store:** Stores database credentials and Flask configuration securely.
6. **Gunicorn:** Serves the Flask application inside the Docker container.

### Application Workflow

1. Users access the Flask application through a web browser.
2. The application runs inside a Docker container hosted on Amazon EC2.
3. The Flask backend communicates with the MySQL database hosted on Amazon RDS.
4. Amazon ECR stores the container images used by the EC2 instance.
5. Application configuration and sensitive credentials are retrieved through AWS Systems Manager Parameter Store.

## AWS Infrastructure

The project uses the following AWS services:

| AWS Service | Purpose |
|---|---|
| Amazon EC2 | Hosting the containerized Flask application |
| Amazon RDS | Managed MySQL database |
| Amazon ECR | Private Docker image repository |
| AWS Systems Manager Parameter Store | Secure application configuration |
| AWS IAM | Access control and permissions |
| Amazon VPC | Network isolation and communication |
| Security Groups | Control inbound and outbound network traffic |
| Amazon S3 | Storage bucket provisioned for the project |

### Cloud Configuration

- **AWS Region:** Asia Pacific (Mumbai) – `ap-south-1`
- **EC2 Operating System:** Ubuntu
- **Database Engine:** MySQL 8.4
- **Database Name:** `expense_tracker`
- **Database Port:** `3306`
- **Application Port:** `5000`
- **Container Registry:** Amazon ECR
- **Application Server:** Gunicorn

### Network Security

- EC2 security group configured for application access.
- RDS security group allows MySQL traffic from the EC2 security group.
- RDS instance configured for private access.
- Database credentials and application secrets stored in Parameter Store rather than hardcoded in the application.

## Docker Configuration

The Flask application is containerized using Docker to provide a consistent runtime environment.

The application runs inside a Docker container with the following configuration:

- Application entry point: `app:app`
- Application server: Gunicorn
- Worker processes: 2
- Threads per worker: 4
- Container port: `5000`
- Restart policy: `unless-stopped`

### Build Docker Image

```bash
docker build -t expense-tracker .
```

### Run Docker Container

```bash
docker run -d \
  --name expense-tracker \
  -p 5000:5000 \
  --restart unless-stopped \
  expense-tracker
```

### Verify Running Container

```bash
docker ps
```

## Database Configuration

The application uses MySQL with SQLAlchemy for database interaction.

For cloud deployment, the database is hosted using Amazon RDS.

**Database Configuration:**

- Engine: MySQL 8.4
- Database: `expense_tracker`
- Port: `3306`
- Hosting: Amazon RDS
- Access: Private network connectivity from EC2

Database credentials and connection settings are managed using AWS Systems Manager Parameter Store.

## Environment Variables

The application requires the following configuration values:

| Variable | Description |
|---|---|
| `DB_USER` | MySQL database username |
| `DB_PASSWORD` | MySQL database password |
| `DB_HOST` | Database endpoint |
| `DB_NAME` | Database name |
| `DB_PORT` | Database port |
| `FLASK_SECRET_KEY` | Flask session security key |

For local development, these values can be configured in a `.env` file.

For AWS deployment, the corresponding parameters are maintained under:

```text
/expense-tracker/
```

**Security Note:** Never commit `.env` files, database passwords, secret keys, or AWS credentials to GitHub.

## Local Installation and Setup

### Prerequisites

Install the following tools:

- Python 3.12 or later
- MySQL
- Git
- Docker (optional for containerized execution)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
```

Navigate to the project directory:

```bash
cd Expense-Tracker
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\Activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required database connection values and Flask secret key.

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```text
http://localhost:5000
```

## AWS Deployment Workflow

The cloud deployment process uses Docker and AWS services.

### Step 1: Build the Docker Image

Build the application image locally:

```bash
docker build -t expense-tracker .
```

### Step 2: Authenticate with Amazon ECR

Authenticate Docker with your private ECR repository using AWS CLI.

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 3: Tag the Docker Image

```bash
docker tag expense-tracker:latest <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/expense-tracker:latest
```

### Step 4: Push the Image to Amazon ECR

```bash
docker push <AWS_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/expense-tracker:latest
```

### Step 5: Run the Application on EC2

The EC2 instance retrieves the Docker image from Amazon ECR and runs the Flask application inside a container.

The application uses Gunicorn to serve incoming requests.

### Step 6: Connect to Amazon RDS

The Flask application connects to the private MySQL RDS instance using the database configuration retrieved from AWS Systems Manager Parameter Store.

## Project Structure

```text
Expense-Tracker/
│
├── app.py                  # Main Flask application
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image configuration
├── .dockerignore           # Files excluded from Docker builds
├── .gitignore              # Git ignored files
│
├── templates/
│   ├── base.html            # Shared base template and navigation
│   ├── home.html            # Application landing page
│   ├── dashboard.html       # Expense management dashboard
│   └── ...                  # Other application templates
│
├── static/
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── ...                  # Other static assets
│
├── uploads/                 # Local receipt upload directory, if used
│
└── README.md                # Project documentation
```

*Note: The structure above is a representative overview. Additional files and templates may exist in the actual repository.*

## Security Considerations

- Database credentials are maintained outside the application source code.
- AWS Systems Manager Parameter Store is used for sensitive configuration.
- Amazon RDS is configured for private network access.
- AWS security groups restrict database access to the application infrastructure.
- Docker provides an isolated application runtime environment.
- Flask uses a secret key for session security.

## Project Objectives

- Develop a practical cloud-based financial management application.
- Understand full-stack web application development using Flask.
- Implement database connectivity using MySQL and SQLAlchemy.
- Learn application containerization using Docker.
- Deploy containerized applications using Amazon EC2 and Amazon ECR.
- Configure managed relational databases using Amazon RDS.
- Implement secure cloud configuration management using AWS Systems Manager.
- Understand AWS networking, IAM, and security group configurations.

## Future Enhancements

- Integrate Amazon S3 for centralized receipt storage.
- Implement automated application deployment and CI/CD.
- Add advanced financial analytics and interactive visualizations.
- Introduce monthly expense summaries and budget management.
- Improve monitoring, logging, and application security.

## Author

Developed as a cloud computing and DevOps learning project, combining Python Flask application development, Docker containerization, MySQL database management, and AWS cloud infrastructure.
