# Required Credentials for Bedrock RAG System Deployment

This document outlines all the credentials and environment variables needed for the successful deployment of the Bedrock RAG System using Jenkins CI/CD pipeline.

## Jenkins Credentials

Configure these credentials in Jenkins Credentials Manager:

| Credential ID | Type |
|---------------|------|
| `aws-ecr-repository` | Secret text |
| `aws-credentials` | AWS Credentials |
| `ec2-dev-host` | Secret text |
| `ec2-prod-host` | Secret text |
| `ec2-ssh-key` | SSH Username with private key |
| `KNOWLEDGE_BASE_ID` | Secret text |
| `MONGODB_URI` | Secret text |
| `MONGODB_DB_NAME` | Secret text |
| `MONGODB_COLLECTION` | Secret text |
| `gitlab-webhook-secret` | Secret text |

## Environment Variables for Deployment

These environment variables are passed from Jenkins to the deployed Docker containers:

| Variable | Description | Source |
|----------|-------------|--------|
| `VERSION` | Automatic version based on date and Git commit | Generated in Pipeline |
| `AWS_REGION` | AWS region for services | Defined in Jenkinsfile |
| `ECR_REPOSITORY` | ECR repository URL | From Jenkins credentials |
| `AWS_ACCESS_KEY_ID` | AWS access key | From Jenkins credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | From Jenkins credentials |

## EC2 Instance Requirements

The EC2 instances need:

1. Docker and Docker Compose installed
2. A user (e.g., ec2-user) with permissions to:
   - Write to `/home/ec2-user/bedrock-rag/`
   - Run Docker commands
   - Pull from ECR repositories

## AWS IAM Requirements

Ensure that:

1. The AWS credentials have permissions for:
   - ECR repository push/pull
   - Any other AWS services used by your application (e.g., Bedrock)

2. The EC2 instances have an IAM role with permissions to:
   - Pull from ECR repositories
   - Access AWS Bedrock service
   - Any other required AWS services

## GitLab Integration (Optional)

If using GitLab CI/CD integration with Jenkins:

1. Configure GitLab webhooks to trigger Jenkins pipeline
2. Set up a GitLab API token as a Jenkins credential
3. Configure the GitLab connection in Jenkins system settings

## Setting Up

1. Store all credentials in Jenkins Credentials Manager
2. Ensure proper IAM roles are attached to EC2 instances
3. Verify Docker and Docker Compose are installed on EC2 instances
4. Check that your docker-compose.yml references the environment variables correctly
5. Test the pipeline with a minimal commit to ensure all credentials are functioning 