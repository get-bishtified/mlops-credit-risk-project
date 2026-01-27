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
      when { expression { params.ACTION == 'APPLY' } }
      steps { deleteDir() }
    }

    stage('Checkout') {
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
        cd "$WORKSPACE/infra"
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
        cd "$WORKSPACE/infra"

        rm -f "$WORKSPACE/.env_infra"

        export SAGEMAKER_ROLE_ARN=$(jq -r .sagemaker_role_arn.value tf.json)
        export ENDPOINT_NAME=$(jq -r .endpoint_name.value tf.json)
        export RAW_BUCKET=$(jq -r .raw_bucket.value tf.json)
        export MODEL_BUCKET=$(jq -r .model_bucket.value tf.json)
        export MODEL_GROUP=$(jq -r .model_group.value tf.json)

        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

        export TRAIN_IMAGE="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/credit-mlops-train:latest"
        export INFERENCE_IMAGE="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/credit-mlops-infer:latest"

        {
          echo "SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN"
          echo "ENDPOINT_NAME=$ENDPOINT_NAME"
          echo "RAW_BUCKET=$RAW_BUCKET"
          echo "MODEL_BUCKET=$MODEL_BUCKET"
          echo "MODEL_GROUP=$MODEL_GROUP"
          echo "TRAIN_IMAGE=$TRAIN_IMAGE"
          echo "INFERENCE_IMAGE=$INFERENCE_IMAGE"
        } > "$WORKSPACE/.env_infra"
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
          aws s3 cp "$WORKSPACE/data/sample.csv" "s3://$RAW_BUCKET/train/data.csv"
        fi
        '''
      }
    }

    stage('Build & Push Training Image') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        set -a
        . "$WORKSPACE/.env_infra"
        set +a

        aws ecr get-login-password --region "$AWS_REGION" \
          | docker login --username AWS --password-stdin "$(echo $TRAIN_IMAGE | cut -d/ -f1)"

        docker build -t credit-train "$WORKSPACE/training"
        docker tag credit-train "$TRAIN_IMAGE"
        docker push "$TRAIN_IMAGE"
        '''
      }
    }

    stage('Build & Push Inference Image') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
          set -e
          set -a
          . "$WORKSPACE/.env_infra"
          set +a

          aws ecr get-login-password --region "$AWS_REGION" \
            | docker login --username AWS --password-stdin "$(echo $INFERENCE_IMAGE | cut -d/ -f1)"

          docker build -t credit-mlops-infer "$WORKSPACE/inference"
          docker tag credit-mlops-infer "$INFERENCE_IMAGE"
          docker push "$INFERENCE_IMAGE"
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
        python3 "$WORKSPACE/pipelines/trigger_training.py"
        '''
      }
    }

    stage('Evaluate') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        [ -f "$WORKSPACE/.env_artifacts" ] && . "$WORKSPACE/.env_artifacts"
        python3 "$WORKSPACE/pipelines/evaluate.py"
        '''
      }
    }

    stage('Register Model') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        set -a
        . "$WORKSPACE/.env_infra"
        [ -f "$WORKSPACE/.env_artifacts" ] && . "$WORKSPACE/.env_artifacts"
        set +a
        python3 "$WORKSPACE/pipelines/register_model.py"
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
        [ -f "$WORKSPACE/.env_model" ] && . "$WORKSPACE/.env_model"
        set +a
        python3 "$WORKSPACE/pipelines/deploy.py"
        '''
      }
    }

    stage('Post-Deploy Health Check') {
      when { expression { params.ACTION == 'APPLY' } }
      steps {
        sh '''
        set -e
        set -a
        . "$WORKSPACE/.env_infra"
        set +a
        python3 "$WORKSPACE/pipelines/check_drift.py"
        '''
      }
    }

    stage('Pre-Destroy Cleanup (SageMaker)') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        sh '''
        set -e
        for ep in $(aws sagemaker list-endpoints --query 'Endpoints[].EndpointName' --output text); do
          aws sagemaker delete-endpoint --endpoint-name "$ep" || true
        done

        for job in $(aws sagemaker list-training-jobs --status-equals InProgress --query 'TrainingJobSummaries[].TrainingJobName' --output text); do
          aws sagemaker stop-training-job --training-job-name "$job" || true
        done

        sleep 60
        '''
      }
    }

    stage('Pre-Destroy Cleanup (S3)') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        sh '''
        set -e
        for b in $(aws s3 ls | awk '{print $3}' | grep "^${PROJECT}-"); do
          aws s3 rm "s3://$b" --recursive || true
        done
        '''
      }
    }

    stage('Pre-Destroy Cleanup (ECR)') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        sh '''
        set -e
        for repo in $(aws ecr describe-repositories \
          --query "repositories[?starts_with(repositoryName, '${PROJECT}-')].repositoryName" \
          --output text); do

          image_ids=$(aws ecr list-images \
            --repository-name "$repo" \
            --query 'imageIds[*]' \
            --output json)

          if [ "$image_ids" != "[]" ]; then
            aws ecr batch-delete-image \
              --repository-name "$repo" \
              --image-ids "$image_ids" || true
          fi
        done
        '''
      }
    }

    stage('Terraform Destroy') {
      when { expression { params.ACTION == 'DESTROY' } }
      steps {
        input message: 'This will DELETE all AWS resources. Are you sure?'
        sh '''
        set -e
        cd "$WORKSPACE/infra"
        terraform init
        terraform destroy -auto-approve
        '''
      }
    }
  }

  post {
    failure { echo "Pipeline failed." }
    success { echo "Action ${params.ACTION} completed successfully." }
  }
}
