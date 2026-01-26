pipeline {
  agent any

  parameters {
    choice(
      name: 'ACTION',
      choices: ['APPLY', 'DESTROY'],
      description: 'Provision (APPLY) or destroy (DESTROY) the entire MLOps stack'
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

    /* ---------------- APPLY FLOW ---------------- */

    stage('Checkout') {
      when { expression { params.ACTION == 'APPLY' } }
      steps { checkout scm }
    }

    stage('Tests') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
          set -e
          python3 -m pip install --user pytest
          python3 -m pytest tests/
        '''
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

          echo "SAGEMAKER_ROLE_ARN=$(jq -r .sagemaker_role_arn.value tf.json)" > ../.env_infra
          echo "ENDPOINT_NAME=$(jq -r .endpoint_name.value tf.json)" >> ../.env_infra
          echo "MODEL_GROUP=$(jq -r .model_group.value tf.json)" >> ../.env_infra
          echo "RAW_BUCKET=$(jq -r .raw_bucket.value tf.json)" >> ../.env_infra
          echo "MODEL_BUCKET=$(jq -r .model_bucket.value tf.json)" >> ../.env_infra
          echo "TRAIN_IMAGE=$(jq -r .train_image.value tf.json)" >> ../.env_infra
        '''
      }
    }

    stage('Train Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
          set -e
          source .env_infra
          python3 pipelines/trigger_training.py
        '''
      }
    }

    stage('Evaluate') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
          set -e
          source .env_artifacts
          python3 pipelines/evaluate.py
        '''
      }
    }

    stage('Register Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
          set -e
          source .env_artifacts
          python3 pipelines/register_model.py
        '''
      }
    }

    stage('Deploy (Manual Approval)') {
      when { expression { params.ACTION == 'APPLY' } }

      input {
        message "Approve model for production deployment?"
        ok "Deploy"
      }

      steps {
        sh '''
          set -e
          source .env_infra
          source .env_model
          python3 pipelines/deploy.py
        '''
      }
    }

    /* ---------------- DESTROY FLOW ---------------- */

    stage('Pre-Destroy Cleanup (SageMaker & S3)') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        sh '''
          set -e

          echo "Stopping training jobs..."
          for j in $(aws sagemaker list-training-jobs --region ${AWS_REGION} \
            --query "TrainingJobSummaries[?starts_with(TrainingJobName, '${PROJECT}')].TrainingJobName" \
            --output text); do
            aws sagemaker stop-training-job --training-job-name "$j" --region ${AWS_REGION} || true
          done

          echo "Deleting model packages..."
          for p in $(aws sagemaker list-model-packages --region ${AWS_REGION} \
            --model-package-group-name ${PROJECT}-credit-risk \
            --query "ModelPackageSummaryList[].ModelPackageArn" \
            --output text 2>/dev/null); do
            aws sagemaker delete-model-package --model-package-arn "$p" --region ${AWS_REGION} || true
          done

          echo "Emptying S3 buckets..."
          for b in $(aws s3 ls | awk '{print $3}' | grep "^${PROJECT}-"); do
            aws s3 rm "s3://$b" --recursive || true
          done
        '''
      }
    }

    stage('Terraform Destroy') {
      when { expression { params.ACTION == 'DESTROY' } }

      input {
        message "This will DELETE all AWS resources. Continue?"
        ok "Destroy"
      }

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
      echo "Pipeline failed. No partial production rollout occurred."
    }
    success {
      echo "Action ${params.ACTION} completed successfully."
    }
  }
}
