resource "aws_launch_template" "this" {
  for_each = var.node_groups

  name          = lower("${var.name}-${each.key}-launch-template")
  ebs_optimized = var.ebs_optimized
  image_id      = var.image_id

  dynamic "block_device_mappings" {
    for_each = var.block_device_mappings
    content {
      device_name = block_device_mappings.value.device_name
      dynamic "ebs" {
        for_each = [lookup(block_device_mappings.value, "ebs", [])]
        content {
          delete_on_termination = lookup(ebs.value, "delete_on_termination", null)
          volume_size           = lookup(ebs.value, "volume_size", null)
          volume_type           = lookup(ebs.value, "volume_type", null)
        }
      }
    }
  }

  lifecycle {
    create_before_destroy = true
  }
  network_interfaces {
    security_groups = [var.eks_cluster_sg]
  }
  user_data = base64encode(templatefile("${path.module}/user-data.sh.tpl", {
  }))
}
