# Jenkins CI/CD Pipeline for Bedrock RAG System

This directory contains the Jenkins pipeline configuration for building, testing, and deploying the Bedrock RAG System.

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

## Environment Variables

- `VERSION` - Automatically generated based on date and git commit
- `AWS_REGION` - AWS region for ECR and EC2 resources
- `ECR_REPOSITORY` - ECR repository URL for Docker images

## Deployment Setup

### Prerequisites

1. AWS ECR repository for storing Docker images
2. EC2 instances for development and production environments
3. Docker and Docker Compose installed on EC2 instances
4. IAM roles for EC2 instances to pull from ECR

### Docker Compose Template

Create a `docker-compose.template.yml` file in your repository that will be used as a template for deployment. Environment variables in this file will be replaced with actual values during deployment.

## Usage

This pipeline is designed to be triggered automatically when changes are pushed to the GitLab repository. 
It can also be triggered manually from the Jenkins dashboard.

### Branch-Specific Behavior

- **develop** branch: Builds, tests, and deploys to development EC2 instance
- **main** branch: Builds, tests, pushes Docker images to ECR, and deploys to production EC2 instance with manual approval 