# modules/eks/main.tf

resource "aws_eks_cluster" "this" {
  name     = "crm-eks-${var.environment}"
  role_arn = var.cluster_role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

# GPU node group
resource "aws_eks_node_group" "gpu" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "gpu-pool"
  node_role_arn   = var.gpu_node_role_arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = 1
    max_size     = 5
    min_size     = 1
  }

  labels = {
    "inference" = "true"
    "gpu"       = "true"
  }

  instance_types = ["g4dn.xlarge"]
}
