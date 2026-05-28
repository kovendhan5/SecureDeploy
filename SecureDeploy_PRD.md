# SecureDeploy — Azure DevSecOps Pipeline
## Product Requirements Document (PRD)

> **Version:** 1.0 | **Author:** Kovendhan P. | **Date:** May 2025
> **Status:** Ready for Development | **Repo:** `github.com/kovendhan5/securedeploy`

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Objectives](#3-goals--objectives)
4. [Scope](#4-scope)
5. [Technology Stack](#5-technology-stack)
6. [System Architecture](#6-system-architecture)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [7-Day Development Plan](#9-7-day-development-plan)
10. [Repository Structure](#10-repository-structure)
11. [Copilot Prompt Guide](#11-copilot-prompt-guide)
12. [Success Criteria](#12-success-criteria)
13. [Risks & Mitigations](#13-risks--mitigations)
14. [Glossary](#14-glossary)

---

## 1. Executive Summary

SecureDeploy is a **fully automated, security-first CI/CD pipeline** built on Microsoft Azure. It automatically builds, scans, and deploys a containerized Python FastAPI application to Azure Kubernetes Service (AKS) — with zero manual steps and zero secrets exposed in code.

The project demonstrates **DevSecOps best practices** across GitHub Actions, Terraform, Azure services, container security, and infrastructure-as-code — all in a single end-to-end working system.

### What This Project Proves to Recruiters

| Skill Area | What SecureDeploy Demonstrates |
|---|---|
| CI/CD | End-to-end pipeline automation with GitHub Actions |
| Security | Shift-left security with 3 scanning tools |
| Cloud (Azure) | 5+ Azure services provisioned and integrated |
| IaC | 100% Terraform-managed infrastructure |
| Kubernetes | Production AKS deployment with rollback |
| Observability | Prometheus + Grafana live monitoring |

---

## 2. Problem Statement

### 2.1 Business Context

Modern software teams release code multiple times per day. Without automation, each deployment is manual, error-prone, and a security risk. Organizations need engineers who can build and maintain **secure automated delivery pipelines from day one**.

### 2.2 Pain Points Solved

| Pain Point | Current Reality | SecureDeploy Fix |
|---|---|---|
| Manual deployments | Engineers SSH into servers manually | Git push triggers full automated pipeline |
| Security as afterthought | Vulnerabilities found post-deploy | Security gates block every bad commit |
| Secrets in source code | Passwords hardcoded in repositories | Azure Key Vault manages all secrets at runtime |
| No infrastructure traceability | Resources created manually, no history | Terraform defines everything as versioned code |
| Lack of visibility | No insight into pipeline or app health | Grafana dashboard shows real-time metrics |

---

## 3. Goals & Objectives

### 3.1 Primary Goals

| ID | Goal | Success Metric |
|---|---|---|
| G1 | Fully automated CI/CD pipeline | Zero manual steps from commit to deploy |
| G2 | Security integrated at every stage | 3 tools running on every PR |
| G3 | 100% infrastructure via Terraform IaC | No Azure resources created manually |
| G4 | Live production AKS deployment | App accessible via public endpoint |
| G5 | Real-time observability | Grafana dashboard showing live metrics |

### 3.2 Portfolio Goals

- Clean, well-documented GitHub repository suitable for recruiter review
- README with architecture diagram, setup steps, and demo GIF
- LinkedIn post showcasing project with measurable results
- Resume bullet points with concrete numbers (tools, services, metrics)

---

## 4. Scope

### 4.1 In Scope ✅

- GitHub Actions CI/CD workflow (build → test → scan → deploy)
- **Trivy** — container image vulnerability scanning
- **SonarCloud** — SAST static code analysis
- **GitLeaks** — secret detection in source code
- Azure Container Registry (ACR) for Docker image storage
- Azure Kubernetes Service (AKS) as deployment target
- Azure Key Vault for secrets management
- Terraform scripts for all Azure infrastructure
- Prometheus + Grafana monitoring stack on AKS
- Sample Python FastAPI application as deployment subject
- Kubernetes manifests (Deployment, Service, Ingress, HPA)
- Full GitHub documentation (README, architecture diagram)

### 4.2 Out of Scope ❌

- Multi-environment setup (staging, UAT) — single production only
- Custom domain and SSL certificate
- Mobile or frontend application development
- Multi-cloud or hybrid cloud deployment
- Automated performance or load testing
- Cost optimization / FinOps analysis

---

## 5. Technology Stack

| Layer | Tool / Service | Version / SKU | Purpose |
|---|---|---|---|
| CI/CD Orchestration | GitHub Actions | Latest | Pipeline trigger, stage sequencing |
| Secret Detection | GitLeaks | v8+ | Scan commits for exposed credentials |
| Static Analysis (SAST) | SonarCloud | Free tier | Code quality + security vulnerability scan |
| Container Scanning | Trivy | Latest | Scan Docker images for CVEs |
| Container Registry | Azure Container Registry | Basic SKU | Private Docker image storage |
| Infrastructure-as-Code | Terraform | >= 1.5 | Provision all Azure resources |
| Secrets Management | Azure Key Vault | Standard | Secure secrets at runtime |
| Container Orchestration | Azure Kubernetes Service | Latest | Run app in production |
| Monitoring | Prometheus | Helm chart | Scrape and store metrics |
| Dashboards | Grafana | Helm chart | Visualize metrics and alerts |
| Application Runtime | Python FastAPI | 0.110+ | Sample microservice for deployment |
| Containerization | Docker | Latest | Package app and dependencies |

---

## 6. System Architecture

### 6.1 Pipeline Flow (Shift-Left Security Model)

```
Developer Push / PR
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS PIPELINE                    │
│                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐   │
│  │  Stage 1    │   │  Stage 2    │   │    Stage 3        │   │
│  │ Secret Scan │──▶│    Build    │──▶│   SAST Scan       │   │
│  │ (GitLeaks)  │   │ (Docker)    │   │  (SonarCloud)     │   │
│  └─────────────┘   └─────────────┘   └──────────────────┘   │
│         │                                       │             │
│    ❌ BLOCK                                ❌ BLOCK           │
│                                                │             │
│                             ┌──────────────────┘             │
│                             ▼                                 │
│                    ┌─────────────────┐                        │
│                    │    Stage 4      │                        │
│                    │ Container Scan  │                        │
│                    │   (Trivy)       │                        │
│                    └─────────────────┘                        │
│                             │                                 │
│                        ❌ BLOCK                               │
│                             │                                 │
│                    ┌─────────────────┐                        │
│                    │    Stage 5      │                        │
│                    │  Push to ACR    │                        │
│                    └─────────────────┘                        │
│                             │                                 │
│                    ┌─────────────────┐                        │
│                    │    Stage 6      │                        │
│                    │ Terraform Apply │                        │
│                    └─────────────────┘                        │
│                             │                                 │
│                    ┌─────────────────┐                        │
│                    │    Stage 7      │                        │
│                    │  Deploy to AKS  │                        │
│                    └─────────────────┘                        │
│                             │                                 │
│                    ┌─────────────────┐                        │
│                    │    Stage 8      │                        │
│                    │  Health Check   │                        │
│                    │  Smoke Test     │                        │
│                    └─────────────────┘                        │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
  AKS Production Cluster
        │
        ▼
  Prometheus + Grafana
  (Live Monitoring)
```

### 6.2 Pipeline Stage Details

| Stage | Tool | Fail Condition | Block Deployment? |
|---|---|---|---|
| 1. Secret Scan | GitLeaks | Any credential or API key found | ✅ Yes |
| 2. Build | Docker | Build error or test failure | ✅ Yes |
| 3. SAST Scan | SonarCloud | Quality Gate fails | ✅ Yes |
| 4. Image Scan | Trivy | HIGH or CRITICAL CVEs found | ✅ Yes |
| 5. Push to ACR | Azure CLI | Auth failure or registry error | ✅ Yes |
| 6. Infra Apply | Terraform | Plan error or state conflict | ✅ Yes |
| 7. Deploy | kubectl | Pod fails health/readiness probe | ✅ Yes |
| 8. Smoke Test | curl | Non-200 from `/health` endpoint | ✅ Yes |

### 6.3 Azure Infrastructure Map

```
Resource Group: rg-securedeploy-prod
│
├── Virtual Network: vnet-securedeploy
│   └── Subnet: snet-aks
│
├── Azure Kubernetes Service: aks-securedeploy
│   ├── Node Pool: 2x Standard_B2s (auto-scaling 2–4)
│   └── Managed Identity → ACR pull access
│
├── Azure Container Registry: acrsecuredeploy
│   └── SKU: Basic
│
├── Azure Key Vault: kv-securedeploy
│   ├── Secret: SONAR_TOKEN
│   ├── Secret: ACR_PASSWORD
│   └── Access: AKS Managed Identity (RBAC)
│
└── Storage Account: stsecuredeploytfstate
    └── Blob Container: tfstate (Terraform remote state)
```

---

## 7. Functional Requirements

### 7.1 Pipeline Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Pipeline must trigger automatically on every push to `main` | Must Have |
| FR-02 | Pipeline must trigger on every pull request to `main` | Must Have |
| FR-03 | Each stage must report pass/fail in GitHub PR checks | Must Have |
| FR-04 | A failed security gate must block deployment entirely | Must Have |
| FR-05 | Failed deployments must automatically rollback to last stable version | Must Have |
| FR-06 | Pipeline must complete within 15 minutes end-to-end | Should Have |
| FR-07 | Pipeline execution logs must be retained for 30 days | Should Have |
| FR-08 | Manual approval gate before production deploy (optional) | Nice to Have |

### 7.2 Security Requirements

| ID | Requirement | Priority |
|---|---|---|
| SR-01 | Zero secrets, passwords, or API keys in any file in the repository | Must Have |
| SR-02 | All secrets must be retrieved from Azure Key Vault at runtime | Must Have |
| SR-03 | Docker images with CRITICAL CVEs must be blocked from deployment | Must Have |
| SR-04 | SonarCloud Quality Gate failure must block the pipeline | Must Have |
| SR-05 | AKS pods must run as non-root user (securityContext) | Must Have |
| SR-06 | Kubernetes secrets must reference Key Vault via CSI driver | Should Have |
| SR-07 | Container images must be scanned fresh on every pipeline run | Should Have |

### 7.3 Infrastructure Requirements

| ID | Requirement | Priority |
|---|---|---|
| IR-01 | All Azure resources provisioned exclusively via Terraform | Must Have |
| IR-02 | Terraform state stored remotely in Azure Blob Storage | Must Have |
| IR-03 | Full infrastructure destroyable with `terraform destroy` | Must Have |
| IR-04 | Resource naming: `{project}-{env}-{resource}` convention | Should Have |
| IR-05 | All resources tagged with project name, environment, owner | Should Have |

### 7.4 Observability Requirements

| ID | Requirement | Priority |
|---|---|---|
| OB-01 | Prometheus scrapes metrics from deployed application | Must Have |
| OB-02 | Grafana shows request rate, error rate, and latency (RED metrics) | Must Have |
| OB-03 | Grafana shows AKS node CPU and memory utilization | Should Have |
| OB-04 | Alert fires if application error rate exceeds 5% | Should Have |
| OB-05 | Deployment events appear as annotations in Grafana | Nice to Have |

---

## 8. Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Performance | Pipeline execution time | < 15 minutes |
| Reliability | Deployment success rate on clean code | > 95% |
| Security | Secrets exposed in repo or logs | Zero |
| Availability | Application uptime after successful deploy | > 99% |
| Maintainability | Terraform module structure | Modular, reusable, documented |
| Portability | Time to provision new environment from scratch | < 30 minutes |
| Cost | Monthly Azure spend | < USD 50 |
| Documentation | README completeness | Setup + architecture + usage |

---

## 9. 7-Day Development Plan

### Day 1 — Project Setup & Azure Infrastructure

**Goal:** GitHub repo ready, all Azure resources provisioned via Terraform.

**Tasks:**
- [ ] Create GitHub repository `securedeploy` with README stub
- [ ] Install: Azure CLI, Terraform, kubectl, Helm
- [ ] Login to Azure: `az login`
- [ ] Write Terraform root module (`main.tf`, `variables.tf`, `outputs.tf`)
- [ ] Write Terraform modules for: AKS, ACR, Key Vault, VNet, Storage Account
- [ ] Create Terraform remote state backend (Azure Blob)
- [ ] Run `terraform init` → `terraform plan` → `terraform apply`
- [ ] Verify AKS is running: `az aks get-credentials` + `kubectl get nodes`

**Deliverables:** Working AKS cluster + ACR + Key Vault on Azure, all via Terraform.

---

### Day 2 — Sample Application & Docker

**Goal:** FastAPI app built, containerized, tested locally, pushed to ACR manually.

**Tasks:**
- [ ] Create `app/main.py` with FastAPI — endpoints: `/`, `/health`, `/metrics`
- [ ] Write unit tests in `app/tests/`
- [ ] Create `app/Dockerfile` (use `python:3.11-slim` base image)
- [ ] Test locally: `docker build` + `docker run` + `curl localhost:8000/health`
- [ ] Login to ACR: `az acr login --name acrsecuredeploy`
- [ ] Tag and push image manually to ACR
- [ ] Store secrets in Key Vault: `az keyvault secret set`

**Deliverables:** Docker image in ACR, app responds to `/health` with `{"status": "ok"}`.

---

### Day 3 — GitHub Actions CI Pipeline

**Goal:** Automated build, test, and Trivy container scan on every push.

**Tasks:**
- [ ] Create `.github/workflows/ci.yml`
- [ ] Stage 1: Checkout code + run unit tests (`pytest`)
- [ ] Stage 2: Docker build
- [ ] Stage 3: Trivy image scan (fail on HIGH/CRITICAL)
- [ ] Stage 4: Push to ACR (only if scan passes)
- [ ] Add Azure credentials as GitHub Secrets: `AZURE_CREDENTIALS`, `ACR_LOGIN_SERVER`
- [ ] Test pipeline: make a commit and watch it run in GitHub Actions tab

**Deliverables:** Green pipeline badge on GitHub README.

---

### Day 4 — Security Integration (SonarCloud + GitLeaks)

**Goal:** SAST and secret detection gates active on every PR.

**Tasks:**
- [ ] Sign up for SonarCloud (free) → connect GitHub repo
- [ ] Create `sonar-project.properties` in project root
- [ ] Add SonarCloud scan step to `ci.yml` (runs after tests, before Docker build)
- [ ] Add `SONAR_TOKEN` to GitHub Secrets
- [ ] Create `.gitleaks.toml` config file
- [ ] Add GitLeaks step as the **first** stage in `ci.yml`
- [ ] Test: add a fake secret to a branch → confirm GitLeaks blocks it → remove secret

**Deliverables:** PRs show SonarCloud Quality Gate result + GitLeaks scan result.

---

### Day 5 — CD Pipeline (Deploy to AKS)

**Goal:** Automated deployment to AKS triggered after successful CI.

**Tasks:**
- [ ] Write Kubernetes manifests in `k8s/`:
  - `deployment.yaml` — 2 replicas, liveness/readiness probes, non-root securityContext
  - `service.yaml` — ClusterIP type
  - `ingress.yaml` — expose app via LoadBalancer
  - `hpa.yaml` — scale on CPU > 70%
- [ ] Create `.github/workflows/cd.yml` — triggered after `ci.yml` passes
- [ ] CD workflow: `az aks get-credentials` → `kubectl set image` (rolling update)
- [ ] Add smoke test step: `curl /health` → fail pipeline if non-200
- [ ] Test rollback: deploy a broken image → confirm pipeline fails + old version stays live

**Deliverables:** App live on AKS public IP, accessible from browser.

---

### Day 6 — Monitoring Stack (Prometheus + Grafana)

**Goal:** Real-time metrics dashboard live on AKS.

**Tasks:**
- [ ] Add Prometheus Python client to FastAPI app (`prometheus-fastapi-instrumentator`)
- [ ] Install Prometheus on AKS via Helm:
  ```bash
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
  ```
- [ ] Install Grafana (included in kube-prometheus-stack)
- [ ] Port-forward Grafana: `kubectl port-forward svc/grafana 3000:80 -n monitoring`
- [ ] Import dashboard: add `monitoring/grafana-dashboard.json` with RED metrics
- [ ] Export dashboard JSON and commit to repo
- [ ] Create alert rule: error rate > 5% → fire alert

**Deliverables:** Grafana dashboard showing request rate, error rate, latency, CPU, memory.

---

### Day 7 — Documentation & Polish

**Goal:** Recruiter-ready GitHub repository.

**Tasks:**
- [ ] Write complete `README.md`:
  - Project overview + badges (pipeline status, SonarCloud quality gate)
  - Architecture diagram (use `docs/architecture.png`)
  - Prerequisites and setup guide
  - How the pipeline works (stage by stage)
  - Screenshot of Grafana dashboard
  - Demo GIF of a full pipeline run
- [ ] Draw architecture diagram (use draw.io or Excalidraw → export PNG)
- [ ] Record demo GIF using Terminalizer or screen recorder
- [ ] Clean up commit history: `git rebase -i` for meaningful commits
- [ ] Add `.trivyignore` for accepted false positives
- [ ] Add GitHub Topics: `devops`, `azure`, `kubernetes`, `devsecops`, `terraform`, `github-actions`
- [ ] Post on LinkedIn with architecture image and 3 key metrics

**Deliverables:** Clean public GitHub repo + LinkedIn post published.

---

## 10. Repository Structure

```
securedeploy/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Build, test, SAST, container scan
│       └── cd.yml                  # Deploy to AKS on CI success
│
├── app/
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Container image definition
│   └── tests/
│       └── test_main.py            # Unit tests
│
├── terraform/
│   ├── main.tf                     # Root Terraform module
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   ├── backend.tf                  # Remote state config (Azure Blob)
│   └── modules/
│       ├── aks/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── acr/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── keyvault/
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
│
├── k8s/
│   ├── deployment.yaml             # App deployment with health probes
│   ├── service.yaml                # ClusterIP service
│   ├── ingress.yaml                # Public LoadBalancer
│   └── hpa.yaml                    # Horizontal Pod Autoscaler
│
├── monitoring/
│   ├── prometheus-values.yaml      # Helm values for Prometheus stack
│   └── grafana-dashboard.json      # Exported Grafana dashboard config
│
├── docs/
│   └── architecture.png            # Architecture diagram
│
├── .gitleaks.toml                  # GitLeaks config (exclusion rules)
├── sonar-project.properties        # SonarCloud project config
├── .trivyignore                    # Accepted CVE exceptions
├── .gitignore
├── README.md                       # Full project documentation
└── PRD.md                          # This file
```

---

## 11. Copilot Prompt Guide

> Use these prompts directly with GitHub Copilot Chat or Copilot in your editor.
> Each prompt is scoped to a specific file or task.

---

### 🔧 Day 1 — Terraform

**Prompt for `terraform/modules/aks/main.tf`:**
```
Create a Terraform module for Azure Kubernetes Service (AKS) with the following:
- Resource group reference via variable
- AKS cluster named "aks-securedeploy" in East US
- Default node pool: Standard_B2s, 2 nodes, auto-scaling 2 to 4
- System-assigned managed identity
- Network profile: Azure CNI, kubenet DNS
- Output: cluster name, kube_config, cluster_id
- Use var.resource_group_name, var.location, var.cluster_name
```

**Prompt for `terraform/modules/acr/main.tf`:**
```
Create a Terraform module for Azure Container Registry with:
- Basic SKU, admin enabled
- Named via var.acr_name in var.resource_group_name
- Role assignment: grant AKS managed identity AcrPull role on this registry
- Output: login_server, acr_id, admin_username
```

**Prompt for `terraform/modules/keyvault/main.tf`:**
```
Create a Terraform module for Azure Key Vault with:
- Standard SKU, soft delete enabled (7 days retention)
- RBAC authorization enabled (not access policies)
- Role assignment: grant AKS managed identity "Key Vault Secrets User" role
- Output: vault_uri, vault_id, vault_name
```

**Prompt for `terraform/backend.tf`:**
```
Write a Terraform backend config using Azure Blob Storage for remote state:
- resource_group_name = "rg-securedeploy-tfstate"
- storage_account_name = "stsecuredeploytf"
- container_name = "tfstate"
- key = "securedeploy.terraform.tfstate"
```

---

### 🐍 Day 2 — FastAPI Application

**Prompt for `app/main.py`:**
```
Create a Python FastAPI application with:
- GET / → returns {"message": "SecureDeploy API", "version": "1.0.0"}
- GET /health → returns {"status": "ok", "timestamp": current UTC time}
- GET /metrics → expose Prometheus metrics using prometheus-fastapi-instrumentator
- Include CORS middleware for all origins
- Add proper logging with structlog or Python logging
- No hardcoded secrets or credentials anywhere
```

**Prompt for `app/Dockerfile`:**
```
Write a production-ready Dockerfile for a Python FastAPI app:
- Base image: python:3.11-slim
- Non-root user: create user "appuser" with UID 1000, run app as this user
- Copy only requirements.txt first (layer caching), then pip install, then copy app
- Expose port 8000
- Health check: curl http://localhost:8000/health every 30s
- CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
- No secrets, no .env files, no hardcoded values
```

**Prompt for `app/tests/test_main.py`:**
```
Write pytest unit tests for a FastAPI app with endpoints /, /health, /metrics:
- Use TestClient from fastapi.testclient
- Test GET / returns 200 and contains "message" key
- Test GET /health returns 200 and status is "ok"
- Test GET /health returns a valid ISO timestamp
- Use pytest fixtures for the test client
```

---

### ⚙️ Day 3 — GitHub Actions CI

**Prompt for `.github/workflows/ci.yml`:**
```
Write a GitHub Actions CI workflow for a Python FastAPI project with these sequential stages:
1. Secret scan using GitLeaks action (zricethezav/gitleaks-action) — fail if secrets found
2. Checkout code, setup Python 3.11, install dependencies, run pytest
3. Build Docker image tagged as: ${{ env.ACR_LOGIN_SERVER }}/securedeploy:${{ github.sha }}
4. Run Trivy scan on the built image — fail on HIGH or CRITICAL severity
5. Login to Azure using AZURE_CREDENTIALS secret, login to ACR
6. Push image to ACR only if all previous steps pass

Use environment variables for ACR_LOGIN_SERVER. Use GitHub Secrets for AZURE_CREDENTIALS.
Each stage should be a separate job or clearly separated step with a descriptive name.
```

---

### 🔐 Day 4 — Security Tools

**Prompt for `.gitleaks.toml`:**
```
Write a GitLeaks v8 configuration file (.gitleaks.toml) that:
- Uses the default ruleset
- Adds an allowlist to exclude test files: path = '''tests/.*'''
- Adds an allowlist to exclude the .trivyignore file
- Sets title = "SecureDeploy GitLeaks Config"
```

**Prompt for `sonar-project.properties`:**
```
Write a sonar-project.properties file for a Python project with:
- sonar.projectKey = kovendhan5_securedeploy
- sonar.organization = kovendhan5
- sonar.sources = app
- sonar.tests = app/tests
- sonar.python.coverage.reportPaths = coverage.xml
- sonar.exclusions = **/__pycache__/**, **/migrations/**
```

**Prompt for adding SonarCloud to `ci.yml`:**
```
Add a SonarCloud analysis step to my existing GitHub Actions workflow.
It should run after pytest and before Docker build.
Use the SonarSource/sonarcloud-github-action@master action.
Pass SONAR_TOKEN from GitHub secrets.
Set GITHUB_TOKEN for PR decoration.
The step should be named "SonarCloud SAST Scan".
```

---

### ☸️ Day 5 — Kubernetes Manifests

**Prompt for `k8s/deployment.yaml`:**
```
Write a Kubernetes Deployment manifest for a FastAPI app with:
- Name: securedeploy-app, namespace: default
- 2 replicas
- Image: pulled from ACR (use placeholder IMAGE_TAG for CI substitution)
- Container port: 8000
- Liveness probe: GET /health, initialDelaySeconds: 30, periodSeconds: 10
- Readiness probe: GET /health, initialDelaySeconds: 5, periodSeconds: 5
- securityContext: runAsNonRoot: true, runAsUser: 1000, readOnlyRootFilesystem: true
- Resource requests: cpu 100m, memory 128Mi
- Resource limits: cpu 500m, memory 256Mi
- Rolling update strategy: maxUnavailable 1, maxSurge 1
```

**Prompt for `k8s/hpa.yaml`:**
```
Write a Kubernetes HorizontalPodAutoscaler for the securedeploy-app deployment:
- Min replicas: 2, Max replicas: 6
- Scale up when CPU utilization exceeds 70%
- Scale up when memory utilization exceeds 80%
- Use autoscaling/v2 API version
```

**Prompt for CD workflow `.github/workflows/cd.yml`:**
```
Write a GitHub Actions CD workflow that:
- Triggers only after the CI workflow completes successfully (workflow_run event)
- Logs into Azure using AZURE_CREDENTIALS secret
- Gets AKS credentials: az aks get-credentials
- Runs kubectl set image to update the deployment with new image SHA
- Waits for rollout: kubectl rollout status deployment/securedeploy-app --timeout=5m
- Runs smoke test: curl the /health endpoint and fail if not 200
- On failure: runs kubectl rollout undo deployment/securedeploy-app
```

---

### 📊 Day 6 — Monitoring

**Prompt for adding Prometheus metrics to `app/main.py`:**
```
Add Prometheus instrumentation to my FastAPI app using prometheus-fastapi-instrumentator:
- Instrument all routes automatically
- Expose metrics at /metrics endpoint
- Add a custom counter metric: "securedeploy_requests_total" with labels: method, endpoint, status
- Add a custom histogram: "securedeploy_response_duration_seconds"
- Initialize the instrumentator in the startup event
```

**Prompt for `monitoring/prometheus-values.yaml`:**
```
Write a Helm values file for the kube-prometheus-stack chart that:
- Enables Grafana with admin password from a Kubernetes secret (not hardcoded)
- Sets Prometheus retention to 7 days
- Enables scraping of all pods with annotation: prometheus.io/scrape: "true"
- Disables alertmanager (not needed for portfolio)
- Sets resource limits: Prometheus 500m CPU, 512Mi memory
```

---

### 📝 Day 7 — README

**Prompt for `README.md`:**
```
Write a professional GitHub README for a DevSecOps portfolio project called SecureDeploy with:
- Badges: GitHub Actions status, SonarCloud quality gate, license
- One-paragraph project summary targeting Cloud & DevOps Engineer recruiters
- Architecture section with a placeholder for architecture.png
- Tech stack table: tool, version, purpose
- How it works section describing the 8-stage pipeline
- Quick start guide: prerequisites, clone, terraform apply, pipeline trigger
- Key results section with metrics: pipeline time, security tools count, Azure services used
- Project structure tree (abbreviated)
- Author: Kovendhan P., Jeppiaar Institute of Technology
Keep it concise — recruiters spend 30 seconds on a README.
```

---

### 🧪 Debugging Prompts (Use When Stuck)

**Trivy blocking on base image CVEs:**
```
My Trivy scan is failing because of CVEs in the python:3.11-slim base image that I cannot patch.
How do I add these CVE IDs to a .trivyignore file?
Show me the format and also suggest if I should switch to python:3.11-alpine or distroless.
```

**Terraform AKS managed identity + ACR issue:**
```
My Terraform is failing when trying to assign the AcrPull role to the AKS managed identity.
The error is "principal not found". This is a timing issue where the identity isn't ready yet.
How do I add a depends_on or time_sleep resource to fix this in Terraform?
```

**kubectl rollout timeout:**
```
My GitHub Actions CD job is failing at kubectl rollout status with a timeout.
The pods are stuck in ImagePullBackOff. How do I:
1. Debug why the image pull is failing from ACR
2. Check if the AKS managed identity has AcrPull permission
3. Fix the CD workflow to show pod describe output on failure
```

**SonarCloud Quality Gate blocking on existing code:**
```
SonarCloud is failing my pipeline on existing code issues, not just new code.
How do I configure the Quality Gate in SonarCloud to only fail on NEW issues introduced
in the current PR, not pre-existing issues in the codebase?
```

---

## 12. Success Criteria

### 12.1 MVP Checklist

- [ ] Git push to `main` triggers pipeline with no manual steps
- [ ] GitLeaks runs first and blocks on any detected secret
- [ ] SonarCloud scan runs and Quality Gate result appears in PR
- [ ] Trivy scan blocks deployment on HIGH/CRITICAL CVEs
- [ ] Docker image is pushed to ACR after all scans pass
- [ ] Application is deployed to AKS after successful CI
- [ ] App responds with `{"status": "ok"}` at `/health` endpoint
- [ ] All Azure infrastructure created via Terraform (nothing manual)

### 12.2 Full Completion Checklist

- [ ] All 8 MVP criteria above are met
- [ ] Prometheus scraping app metrics in AKS cluster
- [ ] Grafana dashboard showing RED metrics (Rate, Errors, Duration)
- [ ] README has architecture diagram, setup guide, and demo GIF
- [ ] GitHub repo has clean commit history with meaningful messages
- [ ] GitHub repo has relevant topics/tags added
- [ ] LinkedIn post published with 3 measurable results

### 12.3 Resume Bullet Points (Copy These After Completion)

```
• Built SecureDeploy — an end-to-end Azure DevSecOps pipeline using GitHub Actions,
  integrating 3 security tools (Trivy, SonarCloud, GitLeaks) with automatic deployment
  blocking on HIGH/CRITICAL vulnerabilities

• Provisioned 5+ Azure services (AKS, ACR, Key Vault, VNet, Blob Storage) entirely via
  Terraform IaC with remote state management and modular reusable modules

• Achieved zero-downtime rolling deployments to AKS with automated rollback on
  health check failure and < 15-minute end-to-end pipeline execution

• Implemented real-time observability with Prometheus + Grafana, monitoring request
  rate, error rate, and latency across the production Kubernetes cluster
```

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Azure free credits exhausted mid-week | Medium | High | Monitor costs daily in Azure Portal; use `Standard_B2s` (cheapest); run `terraform destroy` every night |
| SonarCloud Quality Gate too strict on first run | High | Low | Configure QG to only evaluate new code — uncheck "On New Code" threshold in SonarCloud settings |
| Trivy blocks pipeline on base image CVEs | High | Medium | Add known acceptable CVE IDs to `.trivyignore`; consider switching to `python:3.11-slim-bookworm` |
| AKS provisioning time (15–20 min) | Medium | Low | Pre-provision AKS on Day 1 and leave it running through Day 6 |
| Terraform state corruption | Low | High | Always use remote state with locking; never run `terraform apply` from two places simultaneously |
| kubectl auth fails in GitHub Actions | Medium | Medium | Use `azure/login@v1` + `azure/aks-set-context@v3` actions; ensure service principal has AKS RBAC roles |

---

## 14. Glossary

| Term | Definition |
|---|---|
| **AKS** | Azure Kubernetes Service — managed Kubernetes cluster on Microsoft Azure |
| **ACR** | Azure Container Registry — private Docker image registry on Azure |
| **CI/CD** | Continuous Integration / Continuous Deployment — automated build and release pipeline |
| **SAST** | Static Application Security Testing — scanning source code for vulnerabilities without executing it |
| **CVE** | Common Vulnerabilities and Exposures — a publicly known software security flaw |
| **IaC** | Infrastructure as Code — managing cloud resources through version-controlled code files |
| **DevSecOps** | Development + Security + Operations — integrating security into every phase of the DevOps lifecycle |
| **HPA** | Horizontal Pod Autoscaler — Kubernetes feature to scale pod replicas based on CPU/memory usage |
| **Key Vault** | Azure service for securely storing secrets, certificates, and cryptographic keys |
| **GitLeaks** | Open-source tool to detect hardcoded secrets and credentials in git repositories |
| **Trivy** | Open-source container image and filesystem vulnerability scanner by Aqua Security |
| **SonarCloud** | Cloud-based code quality and security analysis platform |
| **RED Metrics** | Rate, Errors, Duration — the three key metrics for monitoring a microservice |
| **Shift-Left Security** | Practice of integrating security testing early in the development pipeline |
| **Rolling Update** | Kubernetes deployment strategy that replaces pods gradually with zero downtime |

---

> **Document maintained by:** Kovendhan P.
> **Last updated:** May 2025
> **Repository:** `github.com/kovendhan5/securedeploy`
