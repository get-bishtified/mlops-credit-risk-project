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

    stage('Clean Workspace') {
      steps {
        deleteDir()
      }
    }

    stage('Checkout') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        checkout scm
      }
    }

    stage('Tests') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh 'python3 -m pytest tests/'
      }
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
        export RAW_BUCKET=$(jq -r .raw_bucket.value tf.json)
        export MODEL_BUCKET=$(jq -r .model_bucket.value tf.json)
        export MODEL_GROUP=$(jq -r .model_group.value tf.json)
        export TRAIN_IMAGE=$(jq -r .train_image.value tf.json)
        export TRAINING_SUBNETS=$(jq -r '.training_subnets.value | join(",")' tf.json)
        export TRAINING_SG=$(jq -r '.training_security_groups.value[0]' tf.json)

        {
          echo "SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN"
          echo "ENDPOINT_NAME=$ENDPOINT_NAME"
          echo "RAW_BUCKET=$RAW_BUCKET"
          echo "MODEL_BUCKET=$MODEL_BUCKET"
          echo "MODEL_GROUP=$MODEL_GROUP"
          echo "TRAIN_IMAGE=$TRAIN_IMAGE"
          echo "TRAINING_SUBNETS=$TRAINING_SUBNETS"
          echo "TRAINING_SG=$TRAINING_SG"
        } > ../.env_infra
        '''
      }
    }

    stage('Ensure Training Data') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        set -a
        . "$WORKSPACE/.env_infra"
        set +a

        if ! aws s3 ls "s3://$RAW_BUCKET/train/data.csv" >/dev/null 2>&1; then
          echo "Uploading sample training data..."
          aws s3 cp data/sample.csv "s3://$RAW_BUCKET/train/data.csv"
        else
          echo "Training data already present."
        fi
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
        set -a
        . "$WORKSPACE/.env_infra"
        set +a
        python3 pipelines/trigger_training.py
        '''
      }
    }

    stage('Evaluate') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f .env_artifacts ] && . .env_artifacts
        python3 pipelines/evaluate.py
        '''
      }
    }

    stage('Register Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f .env_artifacts ] && . .env_artifacts
        python3 pipelines/register_model.py
        '''
      }
    }

    stage('Deploy (Manual Approval)') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        input message: 'Approve model for production?'
        sh '''
        set -e
        set -a
        . "$WORKSPACE/.env_infra"
        [ -f .env_model ] && . .env_model
        set +a
        python3 pipelines/deploy.py
        '''
      }
    }

    stage('Terraform Destroy') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        input message: 'This will DELETE all AWS resources. Are you sure?'
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
