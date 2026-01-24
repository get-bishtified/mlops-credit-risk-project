pipeline {
  agent any

  parameters {
    choice(
      name: 'ACTION',
      choices: ['APPLY', 'DESTROY'],
      description: 'Provision or destroy all infrastructure'
    )
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
      steps { sh 'python3 -m pytest tests/' }
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

        echo "===== Terraform Outputs ====="
        cat tf.json
        echo "============================="

        export SAGEMAKER_ROLE_ARN=$(jq -r '.sagemaker_role_arn.value // empty' tf.json)
        export ENDPOINT_NAME=$(jq -r '.endpoint_name.value' tf.json)
        export MODEL_GROUP=$(jq -r '.model_package_group_name.value' tf.json)
        export RAW_BUCKET=$(jq -r '.raw_bucket.value' tf.json)
        export MODEL_BUCKET=$(jq -r '.model_bucket.value' tf.json)
        export TRAIN_REPO=$(jq -r '.train_repo_url.value' tf.json)

        # Check if required variables are set
        if [ -z "$SAGEMAKER_ROLE_ARN" ]; then echo "ERROR: SAGEMAKER_ROLE_ARN is not set in Terraform outputs"; exit 1; fi
        if [ -z "$RAW_BUCKET" ]; then echo "ERROR: RAW_BUCKET is not set in Terraform outputs"; exit 1; fi
        if [ -z "$MODEL_BUCKET" ]; then echo "ERROR: MODEL_BUCKET is not set in Terraform outputs"; exit 1; fi
        if [ -z "$TRAIN_REPO" ]; then echo "ERROR: TRAIN_REPO is not set in Terraform outputs"; exit 1; fi

        echo "SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN"
        echo "ENDPOINT_NAME=$ENDPOINT_NAME"
        echo "MODEL_GROUP=$MODEL_GROUP"
        echo "RAW_BUCKET=$RAW_BUCKET"
        echo "MODEL_BUCKET=$MODEL_BUCKET"
        echo "TRAIN_REPO=$TRAIN_REPO"

        echo "SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN" >  "$WORKSPACE/.env_infra"
        echo "ENDPOINT_NAME=$ENDPOINT_NAME"        >> "$WORKSPACE/.env_infra"
        echo "MODEL_GROUP=$MODEL_GROUP"            >> "$WORKSPACE/.env_infra"
        echo "RAW_BUCKET=$RAW_BUCKET"              >> "$WORKSPACE/.env_infra"
        echo "MODEL_BUCKET=$MODEL_BUCKET"          >> "$WORKSPACE/.env_infra"
        echo "TRAIN_IMAGE=$TRAIN_REPO:latest"      >> "$WORKSPACE/.env_infra"
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
        . "$WORKSPACE/.env_infra"

        echo "ROLE=$SAGEMAKER_ROLE_ARN"
        echo "TRAIN_IMAGE=$TRAIN_IMAGE"
        echo "RAW_BUCKET=$RAW_BUCKET"
        echo "MODEL_BUCKET=$MODEL_BUCKET"

        python3 pipelines/trigger_training.py
        '''
      }
    }

    stage('Evaluate') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        . "$WORKSPACE/.env_artifacts"
        python3 pipelines/evaluate.py
        '''
      }
    }

    stage('Register Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        . "$WORKSPACE/.env_artifacts"
        python3 pipelines/register_model.py
        '''
      }
    }

    stage('Deploy (Manual Approval)') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        script {
          input(
            id: 'approve_deploy',
            message: 'Approve model for production?'
          )
        }

        sh '''
        set -e
        . "$WORKSPACE/.env_infra"
        . "$WORKSPACE/.env_model"
        python3 pipelines/deploy.py
        '''
      }
    }

    stage('Health Check (Post-Deploy)') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        . "$WORKSPACE/.env_infra"
        python3 pipelines/check_drift.py
        '''
      }
    }

    stage('Terraform Destroy') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        script {
          input(
            id: 'approve_destroy',
            message: 'This will DELETE all AWS resources. Are you sure?'
          )
        }

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
    }
    success {
      echo "Action ${params.ACTION} completed successfully."
    }
  }
}
