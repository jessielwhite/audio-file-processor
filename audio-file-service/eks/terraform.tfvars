# SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

additional_security_group_ids         = ["EXAMPLE_SECURITY_GROUP_ID"]
aws_profile                           = "default"
cluster_name                          = "EXAMPLE_CLUSTER"
cpu_instance_type                     = "t3.xlarge"
desired_count_cpu_nodes               = "1"
desired_count_gpu_nodes               = "1"
existing_vpc_details                  = {
    vpc_id                              = "EXAMPLE_VPC_ID"
    subnet_ids                          = [
        "subnet-09ae23f8a9d10ac9e", #us-east-1a
        "subnet-0c8e4b019191776dc", #us-east-1b
        "subnet-0e58da1e1b41ea298", #us-east-1c
        "subnet-06e74f2292ae34600", #us-east-1d
        "subnet-03192b1ad8d61dfc2"  #us-east-1f
    ]
}

# For Instances refer https://docs.aws.amazon.com/dlami/latest/devguide/gpu.html
gpu_instance_type                     = "g6.2xlarge"
install_gpu_operator                  = "true"
max_cpu_nodes                         = "10"
max_gpu_nodes                         = "10"
min_cpu_nodes                         = "1"
min_gpu_nodes                         = "1"
region             = "us-east-1"
