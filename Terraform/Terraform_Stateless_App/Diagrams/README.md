# Architecture Diagrams --- Terraform Deployment

## Purpose

This directory contains the architecture diagram generated from the
Terraform infrastructure using the Python **Diagrams** library.

The diagram reflects the actual deployed components and their
relationships.

------------------------------------------------------------------------

## Tooling

Library: https://github.com/mingrammer/diagrams

Language: Python

Diagram type: Cloud architecture

------------------------------------------------------------------------

## What the Diagram Shows

-   VPC boundary
-   Public subnets
-   Private subnets
-   Internet Gateway
-   NAT Gateways
-   Route tables
-   Load balancer entry point
-   Application compute layer
-   Security segmentation

The diagram mirrors Terraform resources to ensure architectural
traceability.

------------------------------------------------------------------------

## How to Generate the Diagram

### Install dependencies

pip install diagrams graphviz

Install Graphviz system package if required.

### Run script

python architecture.py

This will generate a PNG diagram automatically.

------------------------------------------------------------------------

## Design Principles Reflected

-   High availability
-   Secure ingress
-   Private workloads
-   Segmented networking
-   Controlled egress via NAT
-   Load‑balanced stateless application

------------------------------------------------------------------------

## Reviewer Notes

The diagram was generated directly from Terraform logic to ensure
accuracy.

It is not conceptual, it is representative of real infrastructure
components and connectivity.

Created by Enrique Gabriel.
