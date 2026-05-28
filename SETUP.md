# SecureDeploy Project Setup Guide

Complete step-by-step instructions to build and deploy the SecureDeploy project.

## Prerequisites

### Local Tools Required
- Azure CLI (`az`) - [Install](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Terraform >= 1.5 - [Install](https://www.terraform.io/downloads)
- kubectl - [Install](https://kubernetes.io/doc/install-tools/)
- Docker - [Install](https://docs.docker.com/get-docker/)
- Git - [Install](https://git-scm.com/downloads)
- Python 3.11+ (for local testing)

### Azure Requirements
- Azure Student subscription with credits
- GitHub account with repository access
- GitHub Personal Access Token (for Actions)

## Day 1 - Infrastructure Setup

### Step 1.1: Clone Repository

```bash
git clone https://github.com/kovendhan5/securedeploy.git
cd securedeploy
```

### Step 1.2: Create Terraform State Storage (Manual - only once)

```bash
# Set variables
TFSTATE_RG="rg-securedeploy-tfstate"
TFSTATE_STORAGE="stsecuredeploytf"
LOCATION="East US"

# Create resource group for state
az group create \
  --name $TFSTATE_RG \
  --location "$LOCATION"

# Create storage account
az storage account create \
  --resource-group $TFSTATE_RG \
  --name $TFSTATE_STORAGE \
  --sku Standard_LRS \
  --encryption-services blob

# Create container for Terraform state
az storage container create \
  --name tfstate \
  --account-name $TFSTATE_STORAGE \
  --auth-mode login
```

### Step 1.3: Enable Terraform Backend

Uncomment the backend block in `terraform/backend.tf`:

```hcl
backend "azurerm" {
  resource_group_name  = "rg-securedeploy-tfstate"
  storage_account_name = "stsecuredeploytf"
  container_name       = "tfstate"
  key                  = "securedeploy.terraform.tfstate"
}
```

### Step 1.4: Initialize Terraform

```bash
cd terraform
terraform init

# Verify the backend is configured
terraform backend show
```

### Step 1.5: Review and Deploy Infrastructure

```bash
# Plan the deployment
terraform plan -out=tfplan

# Review the plan output carefully

# Apply the configuration
terraform apply tfplan

# Save outputs for later use
terraform output > ../terraform-outputs.txt
```

### Step 1.6: Verify AKS Cluster

```bash
# Get Azure resource group name from Terraform outputs
RG_NAME=$(terraform output -raw resource_group_name)
AKS_NAME=$(terraform output -raw aks_cluster_name)
ACR_NAME=$(terraform output -raw acr_name)

# Get AKS credentials
az aks get-credentials \
  --resource-group $RG_NAME \
  --name $AKS_NAME

# Verify cluster access
kubectl get nodes
kubectl get pods --all-namespaces

# Verify ACR
az acr repository list --name $ACR_NAME
```

**Troubleshooting:**
- If `kubectl get nodes` fails: re-run `az aks get-credentials`
- If role assignments fail: wait 30 seconds and re-run `terraform apply`
- Check Azure Portal > Resource Groups > rg-securedeploy-prod for resource creation status

---

## Day 2 - Local Testing

### Step 2.1: Test FastAPI Application Locally

```bash
cd app

# Install dependencies
pip install -r requirements.txt

# Run unit tests
pytest tests/ -v

# Start app locally
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

### Step 2.2: Build Docker Image Locally

```bash
cd app

# Build image
docker build -t securedeploy:v1 .

# Test image
docker run -p 8000:8000 securedeploy:v1

# In another terminal, test endpoints
curl http://localhost:8000/health

# Stop container
docker stop <container_id>
```

---

## Day 3 - GitHub Actions Setup

### Step 3.1: Create GitHub Secrets

Set these secrets in GitHub repo (Settings > Secrets and variables > Actions):

```
ACR_LOGIN_SERVER=acrsecuredeployprod.azurecr.io
ACR_NAME=acrsecuredeployprod

AKS_RESOURCE_GROUP=rg-securedeploy-prod
AKS_CLUSTER_NAME=aks-securedeploy-prod

SONAR_TOKEN=<your_sonarcloud_token>

AZURE_CREDENTIALS=<service_principal_json>
```

### Step 3.2: Create Service Principal (for AZURE_CREDENTIALS)

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az ad sp create-for-rbac \
  --name "GitHubActions-SecureDeploy" \
  --role "Contributor" \
  --scopes "/subscriptions/$SUBSCRIPTION_ID" \
  --json-auth
```

Copy the JSON output and paste it as `AZURE_CREDENTIALS` secret.

### Step 3.3: Setup SonarCloud

- Go to https://sonarcloud.io/
- Sign up with GitHub account
- Add your repository
- Generate token: https://sonarcloud.io/account/security/tokens/
- Copy token and paste as `SONAR_TOKEN` secret on GitHub

### Step 3.4: Test CI Pipeline

```bash
# Make a small change
echo "# Test" >> README.md
git add .
git commit -m "Test CI pipeline trigger"
git push origin main

# Watch pipeline in GitHub > Actions tab
```

---

## Day 4 - Security Configuration

### Step 4.1: Update SonarCloud Settings (Optional)

In SonarCloud project settings:
- Set Quality Gate to focus on NEW code only
- Adjust security rules as needed

### Step 4.2: Configure Trivy Exceptions

Edit `.trivyignore` to add acceptable CVE IDs (if needed):

```
CVE-2021-12345
CVE-2021-67890
```

---

## Days 5-7 - Deployment & Monitoring

### Complete CI/CD Setup

Once ALL secrets are configured and CI passes:

```bash
git push origin main
# Watch GitHub Actions > Workflows
# CD should automatically trigger after CI passes
```

### Monitoring Setup

After successful deployment:

```bash
# Install Prometheus stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open http://localhost:3000 (admin/admin123)
```

---

## Monitoring & Logs

### Check Pipeline Status

```bash
# GitHub Actions logs (always check here first)
# https://github.com/kovendhan5/securedeploy/actions

# Check ACR for images
az acr repository show-manifests \
  --name acrsecuredeployprod \
  --repository securedeploy

# Check AKS deployment status
kubectl get deployment securedeploy-app -o wide
kubectl get events --sort-by='.lastTimestamp'
kubectl logs -l app=securedeploy-app --tail=50

# Check service and loadbalancer
kubectl get svc securedeploy-app
kubectl get endpoints securedeploy-app
```

### Troubleshooting

**Pod stuck in ImagePullBackOff:**
```bash
# Check pod details
kubectl describe pod <pod-name>

# Check ACR credentials
kubectl get secret -o yaml
```

**AKS cannot connect:**
```bash
# Get credentials again
az aks get-credentials \
  --resource-group rg-securedeploy-prod \
  --name aks-securedeploy-prod \
  --overwrite-existing
```

**Terraform state locked:**
```bash
# Force unlock state
terraform force-unlock <LOCK_ID>
```

---

## Cost Management (Student Tier)

### Monitor Costs
```bash
az costmanagement export create \
  --scope subscriptions/<subscription-id> \
  --definition-name SecureDeployDaily
```

### Save Money
- Tear down infrastructure at night: `terraform destroy`
- Use `Standard_B2s` (cheapest VM)
- Set ACR to "Basic" SKU only
- Monitor Azure Portal daily

---

## Cleanup

To delete all resources (free up credits):

```bash
cd terraform
terraform destroy

# Manually delete state storage (optional)
az group delete --name rg-securedeploy-tfstate
```

---

## Next Steps

1. Complete Day 1: Verify AKS cluster running
2. Complete Day 2: Test app locally
3. Complete Day 3: CI pipeline green
4. Complete Day 4: All security gates passing
5. Complete Day 5-7: App live on AKS with monitoring
6. Document and create LinkedIn post

**Success Criteria:**
- ✅ Git push → Auto pipeline runs
- ✅ All security scans pass
- ✅ App deployed to AKS
- ✅ Public endpoint accessible
- ✅ Grafana dashboard showing metrics
