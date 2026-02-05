# Terraform Stateless Application Deployment (Interview Project)

Production-grade Terraform deployment of a stateless application following secure-by-default and zero-trust infrastructure principles.

## Overview

This project provisions a production‑style cloud architecture to host a
stateless containerized application (NGINX hello demo) using Terraform.

The design focuses on: - High availability - Network security and
isolation - Scalable load-balanced application hosting -
Infrastructure-as-Code best practices - Clear architectural
documentation

This repository was built as part of a technical assessment and
demonstrates real‑world cloud architecture decisions aligned with
enterprise security expectations.

------------------------------------------------------------------------

## Architecture Summary

The infrastructure deploys:

-   VPC with public and private subnets across multiple AZs
-   Internet Gateway for external access
-   NAT Gateways for controlled outbound access from private subnets
-   Route tables enforcing network segmentation
-   Security Groups implementing least‑privilege access
-   Load Balancer deployed in public subnets
-   Stateless containerized application running behind the load balancer
-   Private compute resources not exposed directly to the internet
-   IAM / service roles where required

Key principles: - No direct public access to compute layer - All ingress
flows through load balancer - Private subnets for workloads - HA across
availability zones

------------------------------------------------------------------------

## Repository Structure

    terraform/
      networking/
      compute/
      load_balancer/
      security/
      identity/
    diagrams/
      architecture.py
    README.md

------------------------------------------------------------------------

## Deployment Instructions

### Prerequisites

-   Terraform installed
-   Cloud provider credentials configured
-   Python 3 installed (for diagrams)

### Steps

1.  Clone repository

2.  Initialize Terraform terraform init

3.  Validate terraform validate

4.  Plan terraform plan

5.  Apply terraform apply

------------------------------------------------------------------------

## Security Design Decisions

-   Public exposure limited to Load Balancer
-   Workloads isolated in private subnets
-   NAT gateways for controlled outbound connectivity
-   Security groups enforce traffic boundaries
-   Infrastructure designed following Zero‑Trust principles

------------------------------------------------------------------------

## Security Enhancements (Future Roadmap)

Additional controls that can be enabled in production environments include:

- TLS termination using AWS ACM certificates
- AWS WAF for Layer 7 protection (OWASP Top 10)
- AWS Shield for DDoS protection
- Production deployments should enable HTTPS listeners with ACM certificates and enforce HTTP→HTTPS redirection.

This design intentionally separates baseline infrastructure from layered security controls.

------------------------------------------------------------------------

## Scalability

The architecture supports:

-   Horizontal scaling at compute layer
-   Load balancer distribution
-   Stateless application replacement


------------------------------------------------------------------------

## What Makes This Production‑Ready

-   Modular Terraform structure
-   Secure networking baseline
-   HA architecture pattern
-   Clear architecture diagram
-   Reproducible infrastructure

------------------------------------------------------------------------

## Author Notes

This implementation emphasizes: - clarity - security - scalability -
operational realism.

Created by Enrique Gabriel.
