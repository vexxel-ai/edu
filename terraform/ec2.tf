resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu_arm.id
  instance_type = var.instance_type
  key_name      = var.ssh_key_name

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = file("${path.module}/user-data.sh")

  tags = {
    Name = "${var.project_name}-${var.environment}"
  }

  # Connection details for provisioners
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/${var.ssh_key_name}.pem")
    host        = self.public_ip
  }

  # Wait for instance to be ready
  provisioner "remote-exec" {
    inline = [
      "echo 'Waiting for cloud-init to complete...'",
      "cloud-init status --wait",
      "echo 'Instance ready'"
    ]
  }
}

# Elastic IP for consistent public IP
resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-eip"
  }
}
