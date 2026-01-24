pipeline {
  agent any

  parameters {
    choice(name: 'ACTION', choices: ['APPLY', 'DESTROY'], description: 'Provision or destroy all infrastructure')
  }

  environment {
    AWS_REGION = "ap-south-1"
    PROJECT    = "credit-mlops"
  }

  options {
    timestamps()
  }

  stages {

    stage('Checkout') {
      when { expression { params.ACTION == 'APPLY' } }
      steps { checkout scm }
    }

    stage('Tests') {
      when { expression { params.ACTION == 'APPLY' } }
      steps { sh 'pytest tests/' }
    }

    stage('Terraform Apply') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        cd infra
        terraform init
        terraform apply -auto-approve
        terraform output -json > tf.json
        '''
      }
    }

    stage('Load Infra Outputs') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        cd infra
        export SAGEMAKER_ROLE_ARN=$(jq -r .sagemaker_role_arn.value tf.json)
        export ENDPOINT_NAME=$(jq -r .endpoint_name.value tf.json)
        echo "SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN" > ../.env_infra
        echo "ENDPOINT_NAME=$ENDPOINT_NAME" >> ../.env_infra
        '''
      }
    }

    stage('Build Training Image') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        docker build -t credit-train training/
        '''
      }
    }

    stage('Train Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f .env_infra ] && source .env_infra
        python pipelines/trigger_training.py
        '''
      }
    }

    stage('Evaluate') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f .env_artifacts ] && source .env_artifacts
        python pipelines/evaluate.py
        '''
      }
    }

    stage('Register Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f .env_artifacts ] && source .env_artifacts
        python pipelines/register_model.py
        '''
      }
    }

    stage('Deploy (Manual Approval)') {
      when { expression { params.ACTION == 'APPLY' } }
      input 'Approve model for production?'
      steps {
        sh '''
        set -e
        [ -f .env_infra ] && source .env_infra
        [ -f .env_model ] && source .env_model
        python pipelines/deploy.py
        '''
      }
    }

    stage('Terraform Destroy') {
      when { expression { params.ACTION == 'DESTROY' } }
      input 'This will DELETE all AWS resources. Are you sure?'
      steps {
        sh '''
        set -e
        cd infra
        terraform init
        terraform destroy -auto-approve
        '''
      }
    }
  }

  post {
    failure {
      echo "Pipeline failed. Production endpoint remains unchanged."
      echo "If this occurred before deployment, no rollback is required."
    }
    success {
      echo "Action ${params.ACTION} completed successfully."
    }
  }
}