# Waymark Voiceover Processing

## Introduction

This project provides IaC and code snippets to illustrate how a voiceover processing feature might be engineered and deployed, including setup for an EKS cluster that allows NVIDIA GPU access for FFMPEG worker pods. The files in the /eks directory leverage examples from the [NVIDIA Terraform Kubernetes Modules repo](https://github.com/NVIDIA/nvidia-terraform-modules.git). Actual AWS environment variables, such as access keys and ECR urls, are stubbed with placeholders.

The included Makefile provides examples for spinning up an NVIDIA GPU-ready EKS cluster, applying Kubernetes deployments, and building and pushing Docker images to an ECR registry.

### api

The API provides a simple API interface for handling voiceover uploads and their processing. The GET and POST `/voiceover` endpoints allow for uploading voiceover files, monitoring their progress, and accessing processed/converted audio files and variable quality proxies. Presumably, the API would later include endpoints related to bouncing final videos, which would involve rendering a final video along with the voiceover audio.

### av-worker

The AV Worker contains the Celery job definition where all of the processing happens. The heavy lifting is done with FFMPEG, which has GPU access thanks to the CUDA support of NVIDIA GPU-ready EKS nodes.

### flower

The Flower container spins up an instance of Celery Flower for monitoring and manipulating audio processing jobs.

### grafana

The Grafana container spins up a Grafana instance for insights.

### sentry

The Sentry container spins up a Sentry instance for exception reporting.

### app

The App container spins up a simple TypeScript client for uploading/downloading voiceovers and viewing their progress.