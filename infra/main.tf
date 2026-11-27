provider "aws" {
  region = var.region
}

# --- 1. Le stockage : un bucket S3 privé ---
resource "aws_s3_bucket" "data" {
  bucket        = var.bucket_name
  force_destroy = true # permet a terraform destroy de supprimer le bucket meme s'il contient des fichiers
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- 2. Les droits du serveur : lire et écrire dans CE bucket, rien d'autre ---
resource "aws_iam_role" "ec2" {
  name = "adoptionia-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "s3" {
  role = aws_iam_role.ec2.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:*"]
      Resource = [aws_s3_bucket.data.arn, "${aws_s3_bucket.data.arn}/*"]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "adoptionia-ec2-profile"
  role = aws_iam_role.ec2.name
}

# --- 3. Le pare-feu : qui peut entrer sur le serveur ---
resource "aws_security_group" "app" {
  name = "adoptionia-app-sg"

  ingress { # SSH : seulement depuis votre IP
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"]
  }

  ingress { # interface Streamlit : ouverte à tous
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress { # le serveur peut sortir (API HN, LLM, S3)
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- 4. Le serveur ---
resource "aws_key_pair" "me" {
  key_name   = "adoptionia-key"
  public_key = file("~/.ssh/adoptionia.pub")
}

data "aws_ami" "al2023" { # la dernière image officielle Amazon Linux 2023
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.small" # 2 Go, éligible à l'offre gratuite AWS (+ 2 Go de swap plus bas)
  key_name               = aws_key_pair.me.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size = 30 # 30 Go de disque (images Docker + données)
  }

  # Script exécuté une seule fois, au premier démarrage : installe Docker, Git et CRON
  user_data = <<-EOF
    #!/bin/bash
    # 2 Go de mémoire d'appoint (swap) : marge de sécurité pour Docker sur une machine gratuite
    dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
    dnf install -y docker git cronie
    systemctl enable --now docker crond
    usermod -aG docker ec2-user
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
  EOF

  tags = {
    Name = "adoptionia"
  }
}

output "public_ip" {
  value = aws_instance.app.public_ip
}

output "app_url" {
  value = "http://${aws_instance.app.public_ip}:8501"
}