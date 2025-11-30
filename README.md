# Agriculture & Forestry Management Application

A cloud-based Flask application for managing agricultural crops and forestry plantations.

## Features

- **User Authentication**: Secure login and signup functionality
- **CRUD Operations**: Create, Read, Update, Delete crops and forests
- **Custom OOP Library**: `agri_lib` for crop management and analysis
- **AWS Integration**: 5 AWS services for cloud functionality

## AWS Services Used

1. **Amazon S3** - Object storage for crop/forest images
2. **Amazon DynamoDB** - NoSQL database for activity logging
3. **AWS Lambda** - Serverless computing for crop analysis
4. **Amazon EC2** - Hosting the Flask application
5. **Amazon CloudWatch** - Monitoring and metrics

## Custom Library (`agri_lib`)

The application includes a custom OOP library with:

- `CropManager` - Manages collection of crops and forests
- `CropAnalyzer` - Provides insights and recommendations
- `Crop` - Class for agricultural crops
- `Forest` - Class for forestry plantations
- Utility functions for yield estimation and seasonal recommendations

## Project Structure

```
flask_app/
├── app.py                       # Main Flask application
├── requirements.txt             # Python dependencies
├── setup_aws_infrastructure.py  # AWS setup script
├── agri_lib/                    # Custom OOP library
│   ├── __init__.py
│   ├── crop_manager.py
│   └── utils.py
├── templates/                   # HTML templates (Bootstrap 5)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── add_crop.html
│   ├── edit_crop.html
│   └── analyze.html
└── .github/workflows/
    └── deploy.yml               # CI/CD pipeline
```

## Setup Instructions

### 1. AWS Infrastructure Setup

Run the infrastructure setup script:

```bash
cd flask_app
python setup_aws_infrastructure.py
```

This will create:
- S3 bucket for image storage
- DynamoDB table for activity logs
- Lambda function for analysis
- CloudWatch dashboard
- Security group
- EC2 instance

### 2. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets):

- `EC2_HOST`: Public IP address of your EC2 instance
- `EC2_SSH_KEY`: Contents of cloud-key-pair.pem file

### 3. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 4. CI/CD Deployment

The GitHub Actions workflow will automatically:
1. Connect to EC2 via SSH
2. Pull latest code from repository
3. Install dependencies
4. Stop any existing Flask app
5. Start fresh Flask app with nohup

## Running Locally

```bash
cd flask_app
pip install -r requirements.txt
python app.py
```

Access at: http://localhost:5000

## Region and Configuration

- AWS Region: eu-north-1 (Stockholm)
- EC2 AMI: Amazon Linux 2023
- Instance Type: t3.small
