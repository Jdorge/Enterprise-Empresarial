# ═════════════════════════════════════════════════════════════════
# NEXUS n8n Enterprise Infrastructure (AWS EKS + RDS + ElastiCache)
# DevOps PhD Production-Grade — 99.99% SLA
# ═════════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket         = "nexus-terraform-state"
    key            = "n8n-enterprise/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "nexus-n8n-enterprise"
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  }
}

# ─────────────────────────────────────────────────────────────────
# 1. VPC & NETWORKING
# ─────────────────────────────────────────────────────────────────

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "nexus-vpc"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false  # High availability
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Kubernetes specific tags
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# ─────────────────────────────────────────────────────────────────
# 2. EKS CLUSTER
# ─────────────────────────────────────────────────────────────────

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.28"

  cluster_endpoint_public_access       = true
  cluster_endpoint_private_access      = true
  cluster_endpoint_public_access_cidrs  = ["0.0.0.0/0"]  # Adjust in production
  cluster_endpoint_private_access_cidrs = ["10.0.0.0/16"]

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = concat(module.vpc.private_subnets, module.vpc.public_subnets)
  control_plane_subnet_ids = module.vpc.private_subnets

  # Cluster encryption
  cluster_encryption_config = {
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }

  # EKS Managed Node Group for n8n
  eks_managed_node_groups = {
    n8n_primary = {
      name            = "n8n-primary"
      use_name_prefix = true
      capacity_type   = "ON_DEMAND"

      instance_types = ["m5.2xlarge"]  # 8vCPU, 32GB RAM — pode escalar conforme demanda
      min_size       = 3
      max_size       = 10
      desired_size   = 5

      disk_size = 100

      labels = {
        workload = "n8n-primary"
      }

      taints = []

      tags = {
        NodeGroup = "n8n-primary"
      }
    }

    system = {
      name            = "system"
      use_name_prefix = true
      capacity_type   = "SPOT"

      instance_types = ["t3.large"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2

      disk_size = 50

      labels = {
        workload = "system"
      }

      taints = [{
        key    = "system"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  # Cluster addons
  cluster_addons = {
    coredns            = { version = "v1.10.1-eksbuild.2" }
    kube-proxy         = { version = "v1.28.1-eksbuild.1" }
    vpc-cni            = { version = "v1.14.1-eksbuild.1" }
    aws-ebs-csi-driver = { version = "v1.24.0-eksbuild.1" }
  }

  # IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  # Monitoring
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = {
    ClusterName = var.cluster_name
  }
}

resource "aws_kms_key" "eks" {
  description             = "EKS Secret Encryption Key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# ─────────────────────────────────────────────────────────────────
# 3. RDS POSTGRESQL (n8n Database)
# ─────────────────────────────────────────────────────────────────

resource "aws_db_subnet_group" "n8n" {
  name       = "n8n-db-subnet"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "n8n-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name        = "nexus-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_worker.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "nexus-rds-sg"
  }
}

resource "aws_db_instance" "n8n" {
  allocated_storage       = 100
  max_allocated_storage   = 500  # Enable autoscaling
  storage_type            = "gp3"
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.rds.arn
  engine                  = "postgres"
  engine_version          = "16.1"
  instance_class          = "db.r6i.2xlarge"  # High memory for concurrent workflows
  db_name                 = "n8n_db"
  username                = "n8n_admin"
  password                = random_password.db_password.result
  parameter_group_name    = "default.postgres16"
  db_subnet_group_name    = aws_db_subnet_group.n8n.name
  vpc_security_group_ids  = [aws_security_group.rds.id]

  # High Availability
  multi_az               = true
  backup_retention_period = 30
  backup_window          = "02:00-03:00"
  maintenance_window     = "sun:03:00-sun:04:00"
  deletion_protection    = true

  # Performance Insights
  enabled_cloudwatch_logs_exports = ["postgresql"]
  performance_insights_enabled     = true
  performance_insights_retention_period = 7

  skip_final_snapshot       = false
  final_snapshot_identifier = "nexus-rds-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "nexus-n8n-db"
  }
}

resource "aws_kms_key" "rds" {
  description             = "RDS Encryption Key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!&#$^<>-"
}

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "nexus/n8n/db-credentials"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = aws_db_instance.n8n.username
    password = random_password.db_password.result
    host     = aws_db_instance.n8n.endpoint
    port     = 5432
    database = aws_db_instance.n8n.db_name
  })
}

# ─────────────────────────────────────────────────────────────────
# 4. ELASTICACHE REDIS (Cache & Rate Limiting)
# ─────────────────────────────────────────────────────────────────

resource "aws_elasticache_subnet_group" "redis" {
  name       = "nexus-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name        = "nexus-redis-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_worker.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "nexus-redis-sg"
  }
}

resource "aws_elasticache_replication_group" "redis" {
  engine               = "redis"
  engine_version       = "7.1"
  replication_group_description = "NEXUS n8n Redis Cluster"
  node_type            = "cache.r6g.xlarge"
  num_cache_clusters   = 3  # Multi-AZ cluster
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]
  automatic_failover_enabled = true
  multi_az_enabled     = true
  at_rest_encryption_enabled = true
  auth_token           = random_password.redis_auth_token.result
  transit_encryption_enabled = true

  parameter_group_name = "default.redis7"

  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"

  notification_topic_arn = aws_sns_topic.nexus_alerts.arn

  tags = {
    Name = "nexus-redis-cluster"
  }
}

resource "random_password" "redis_auth_token" {
  length  = 32
  special = false
  numeric = true
}

resource "aws_secretsmanager_secret" "redis_credentials" {
  name                    = "nexus/n8n/redis-credentials"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "redis_credentials" {
  secret_id = aws_secretsmanager_secret.redis_credentials.id
  secret_string = jsonencode({
    auth_token = random_password.redis_auth_token.result
    endpoint   = aws_elasticache_replication_group.redis.configuration_endpoint_address
    port       = 6379
  })
}

# ─────────────────────────────────────────────────────────────────
# 5. S3 BACKUP BUCKETS
# ─────────────────────────────────────────────────────────────────

resource "aws_s3_bucket" "backups" {
  bucket = "nexus-backups-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "nexus-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "delete-old-backups"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_kms_key" "s3" {
  description             = "S3 Backup Encryption Key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# ─────────────────────────────────────────────────────────────────
# 6. SNS TOPICS FOR ALERTS
# ─────────────────────────────────────────────────────────────────

resource "aws_sns_topic" "nexus_alerts" {
  name = "nexus-n8n-alerts"
}

resource "aws_sns_topic_subscription" "nexus_alerts_email" {
  topic_arn = aws_sns_topic.nexus_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_sns_topic_subscription" "nexus_alerts_slack" {
  topic_arn = aws_sns_topic.nexus_alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}

# ─────────────────────────────────────────────────────────────────
# 7. SECURITY GROUP FOR EKS WORKERS
# ─────────────────────────────────────────────────────────────────

resource "aws_security_group" "eks_worker" {
  name        = "nexus-eks-worker"
  description = "Security group for EKS worker nodes"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "nexus-eks-worker"
  }
}

# ─────────────────────────────────────────────────────────────────
# 8. ECR REGISTRY
# ─────────────────────────────────────────────────────────────────

resource "aws_ecr_repository" "n8n" {
  name                 = "nexus-n8n-enterprise"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }

  tags = {
    Name = "nexus-n8n-ecr"
  }
}

resource "aws_ecr_lifecycle_policy" "n8n" {
  repository = aws_ecr_repository.n8n.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_kms_key" "ecr" {
  description             = "ECR Encryption Key"
  deletion_window_in_days = 10
  enable_key_rotation     = true
}

# ─────────────────────────────────────────────────────────────────
# 9. IAM ROLES & POLICIES
# ─────────────────────────────────────────────────────────────────

resource "aws_iam_role" "n8n_pod_execution" {
  name = "nexus-n8n-pod-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Federated = module.eks.oidc_provider_arn
      }
      Condition = {
        StringEquals = {
          "${replace(module.eks.oidc_provider_arn, "/^(.*provider/)/", "")}:sub" = "system:serviceaccount:production:n8n"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "n8n_s3_access" {
  name = "nexus-n8n-s3-access"
  role = aws_iam_role.n8n_pod_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.backups.arn,
          "${aws_s3_bucket.backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.s3.arn
      }
    ]
  })
}

data "aws_caller_identity" "current" {}

# ─────────────────────────────────────────────────────────────────
# 10. OUTPUTS
# ─────────────────────────────────────────────────────────────────

output "cluster_name" {
  value       = module.eks.cluster_name
  description = "EKS Cluster Name"
}

output "cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS Cluster Endpoint"
}

output "cluster_oidc_issuer_url" {
  value       = module.eks.oidc_provider
  description = "OIDC Provider URL"
}

output "rds_endpoint" {
  value       = aws_db_instance.n8n.endpoint
  description = "RDS PostgreSQL Endpoint"
}

output "redis_endpoint" {
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
  description = "Redis Cluster Endpoint"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.n8n.repository_url
  description = "ECR Repository URL"
}

output "backup_bucket" {
  value       = aws_s3_bucket.backups.id
  description = "S3 Backup Bucket"
}