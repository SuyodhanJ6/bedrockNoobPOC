# Jenkins CI/CD Pipeline for Bedrock RAG System

This directory contains the Jenkins pipeline configuration for building, testing, and deploying the Bedrock RAG System.

## Pipeline Configuration Files

- **Jenkinsfile** - Located in the root directory, this is the final version of the Jenkins pipeline definition
- **docker-compose.yml** - Located in the root directory, this is the final Docker Compose configuration used for deployment
- **CREDENTIALS.md** - Details about the credentials required for the pipeline

## Pipeline Overview

The Jenkins pipeline performs the following stages:

1. **Checkout** - Retrieves the source code from GitLab repository
2. **Install Dependencies** - Installs required Python packages
3. **Lint** - Runs code quality checks using flake8 and black
4. **Test** - Executes all tests using the make test command
5. **Build Docker Images** - Builds Docker images for all services
6. **Push Docker Images to ECR** - Pushes Docker images to AWS ECR (main branch only)
7. **Deploy to Dev EC2** - Deploys to development EC2 instance (develop branch only)
8. **Deploy to Production EC2** - Deploys to production EC2 instance with manual approval (main branch only)

## Required Jenkins Plugins

- Docker Pipeline
- AWS Steps
- Credentials Binding
- Pipeline Utility Steps
- Timestamper
- SSH Agent
- GitLab Integration

## Required Jenkins Credentials

The following credentials need to be configured in Jenkins:

- `aws-credentials` - AWS credentials for ECR and EC2 access
- `aws-ecr-repository` - AWS ECR repository URL
- `ec2-dev-host` - Development EC2 instance hostname/IP
- `ec2-prod-host` - Production EC2 instance hostname/IP
- `ec2-ssh-key` - SSH key for EC2 instances
- `KNOWLEDGE_BASE_ID` - Bedrock Knowledge Base ID
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB_NAME` - MongoDB database name
- `MONGODB_COLLECTION` - MongoDB collection name
- `gitlab-webhook-secret` - Secret token for GitLab webhook

See [CREDENTIALS.md](CREDENTIALS.md) for more details on credential values and setup.

## Environment Variables

Environment variables are passed directly from Jenkins to the Docker Compose deployment on EC2:

- `VERSION` - Automatically generated based on date and git commit
- `AWS_REGION` - AWS region for ECR and EC2 resources
- `ECR_REPOSITORY` - ECR repository URL for Docker images
- `AWS_ACCESS_KEY_ID` - AWS access key (from credentials)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (from credentials)

## Deployment Setup

### Prerequisites

1. AWS ECR repository for storing Docker images
2. EC2 instances for development and production environments
3. Docker and Docker Compose installed on EC2 instances
4. IAM roles for EC2 instances to pull from ECR

### Docker Compose Configuration

Ensure your `docker-compose.yml` file uses environment variables for image names and versions:

```yaml
version: '3'
services:
  agent:
    image: ${ECR_REPOSITORY}/bedrock-agent:${VERSION}
    # other configurations...
```

## Usage

This pipeline is designed to be triggered automatically when changes are pushed to the GitLab repository. 
It can also be triggered manually from the Jenkins dashboard.

### Branch-Specific Behavior

- **develop** branch: Builds, tests, and deploys to development EC2 instance
- **main** branch: Builds, tests, pushes Docker images to ECR, and deploys to production EC2 instance with manual approval 