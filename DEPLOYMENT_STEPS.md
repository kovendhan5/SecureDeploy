# 🚀 Step-by-Step Deployment Guide

**Status:** Ready to Deploy  
**Estimated Time:** 40 minutes  
**Current Date:** June 3, 2026

---

## 📋 Pre-Deployment (Choose One)

### Option A: Quick Azure Check (5 min)
```powershell
# Check if you have Azure CLI installed
az version

# Login to Azure
az login

# List subscriptions
az account list
```

### Option B: Complete Setup
```powershell
# If Azure CLI not installed, install it:
# Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# Then login:
az login

# Set default subscription (if multiple)
az account set --subscription "Visual Studio Enterprise Subscription" 
# (or your student subscription name)
```

---

## 🔑 Step 1: Create Azure Service Principal (10 min)

This creates credentials for GitHub Actions to deploy to Azure.

```powershell
# Create the service principal
$sp = az ad sp create-for-rbac --name "GitHubActions-SecureDeploy" --role Contributor --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID> | ConvertFrom-Json

# Display credentials (save these!)
$sp | ConvertTo-Json

# Copy the JSON output to clipboard for GitHub Secrets
$sp | ConvertTo-Json | Set-Clipboard

Write-Host "✅ Service Principal created!"
Write-Host "📋 JSON output copied to clipboard"
```

**Save this JSON - you'll need it for GitHub!**

---

## 🔐 Step 2: Configure GitHub Secrets (10 min)

### Steps:
1. Go to: https://github.com/kovendhan5/securedeploy/settings/secrets/actions
2. Click: "New repository secret"

### Add 6 secrets:

#### 1️⃣ ACR_LOGIN_SERVER
```
Get from Azure Portal:
1. Azure Portal → Container Registries
2. Select: acrsecuredeployprod (or similar)
3. Copy: Login server (e.g., acrsecuredeployprod.azurecr.io)
```

#### 2️⃣ ACR_NAME
```
Just the name part without domain
e.g., acrsecuredeployprod
```

#### 3️⃣ AKS_RESOURCE_GROUP
```
The resource group name
e.g., securedeploy-rg-prd
```

#### 4️⃣ AKS_CLUSTER_NAME
```
The AKS cluster name
e.g., aks-securedeploy-prd
```

#### 5️⃣ SONAR_TOKEN
```
From SonarCloud.io:
1. Visit: https://sonarcloud.io/account/security
2. Create new token (e.g., "GitHub Actions")
3. Copy the token
```

#### 6️⃣ AZURE_CREDENTIALS
```
Paste the JSON from Step 1:
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

✅ All 6 secrets configured

---

## 📂 Step 3: Setup Terraform (5 min)

```powershell
# Navigate to Terraform directory
cd k:\Devops\SecureDeploy\terraform

# Initialize Terraform
terraform init

# (If using Azure backend, it will ask to authenticate)
# Follow prompts to complete backend setup
```

**Output should show:**
```
Terraform has been successfully initialized!
```

---

## 📋 Step 4: Review Infrastructure Plan (10 min)

```powershell
# Generate a plan (don't apply yet!)
terraform plan -out=tfplan

# Review the plan carefully
# It should show:
# - 1 Resource Group
# - 1 Virtual Network + subnet + NSG
# - 1 AKS Cluster (2-4 nodes)
# - 1 Container Registry
# - 1 Key Vault
# - Various role assignments

# If plan looks good, apply it
terraform apply tfplan

# Wait for deployment (5-10 minutes)
# You'll see: "Apply complete! Resources: X added, 0 changed, 0 destroyed."
```

---

## ✅ Step 5: Verify AKS Cluster (5 min)

```powershell
# Get AKS credentials
az aks get-credentials --resource-group "securedeploy-rg-prd" --name "aks-securedeploy-prd"

# Verify cluster is running
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES   AGE    VERSION
# aks-node1  Ready    agent   2m     v1.28.0
# aks-node2  Ready    agent   2m     v1.28.0

# Check cluster info
kubectl cluster-info

# You should see:
# Kubernetes master is running at https://...
```

---

## 🚀 Step 6: Push Code to GitHub (5 min)

```powershell
# Navigate to repo root
cd k:\Devops\SecureDeploy

# Configure Git (if first time)
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"

# Add all files
git add .

# Commit with message
git commit -m "Initial SecureDeploy deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Push to GitHub (triggers CI/CD pipeline)
git push origin main

# If you get auth error, use GitHub token:
# 1. Generate token: https://github.com/settings/tokens
# 2. Use as password when prompted
```

---

## 👀 Step 7: Monitor CI/CD Pipeline (10 min)

```powershell
# Watch the pipeline online
# Visit: https://github.com/kovendhan5/securedeploy/actions

# You should see:
# 1. ✅ GitLeaks (secret scanning)
# 2. ✅ pytest (unit tests)  
# 3. ✅ SonarCloud (code quality)
# 4. ✅ Trivy (CVE scanning)
# 5. ✅ Docker build & push
# 6. ✅ Terraform apply (infrastructure)
# 7. ✅ kubectl deploy
# 8. ✅ Smoke test (health check)

# To check locally:
kubectl get pods

# Expected: 2 pods running
# NAME                                READY   STATUS    RESTARTS   AGE
# securedeploy-app-xxxxx              1/1     Running   0          1m
# securedeploy-app-yyyyy              1/1     Running   0          1m
```

---

## 🌐 Step 8: Access Your Application (5 min)

```powershell
# Get service details
kubectl get svc securedeploy-app

# Find the EXTERNAL-IP
# NAME               TYPE           CLUSTER-IP    EXTERNAL-IP    PORT(S)
# securedeploy-app   LoadBalancer   10.0.xx.xx    52.xxx.xx.xxx  80:8000/TCP

# Test the endpoints
$EXTERNAL_IP = "52.xxx.xx.xxx"  # Replace with actual IP

# Root endpoint
curl "http://$EXTERNAL_IP/"

# Health check
curl "http://$EXTERNAL_IP/health"

# Metrics
curl "http://$EXTERNAL_IP/metrics"

# Expected: Status 200 with JSON responses
```

---

## 📊 Step 9: Setup Monitoring (5 min)

```powershell
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
cd k:\Devops\SecureDeploy\monitoring
helm install prometheus prometheus-community/kube-prometheus-stack `
  -n monitoring `
  --create-namespace `
  -f prometheus-values.yaml

# Verify installation
kubectl get pods -n monitoring

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open browser: http://localhost:3000
# Default login: admin / <auto-generated>

# Get Grafana password:
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | ForEach-Object {[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_))}
```

---

## ✨ Verify Everything (5 min)

```powershell
# 1. Check pods
kubectl get pods
# Should see: 2 securedeploy-app pods running

# 2. Check service
kubectl get svc securedeploy-app
# Should have external IP assigned

# 3. Check metrics
kubectl get pods -n monitoring
# Should see prometheus and grafana pods

# 4. Test application
$APP_IP = "52.xxx.xx.xxx"
curl "http://$APP_IP/health" | ConvertFrom-Json
# Should return: {"status": "ok", "timestamp": "2026-06-03T..."}

# 5. Check Grafana
# Open: http://localhost:3000
# Login with admin / <password from above>
# Should see Kubernetes dashboards with metrics

Write-Host "✅ All systems operational!"
```

---

## 🎉 Success! You're Done

If all the above steps completed successfully:

✅ AKS cluster running on Azure  
✅ Container registry with images  
✅ Application deployed (2 replicas)  
✅ Prometheus collecting metrics  
✅ Grafana showing dashboards  
✅ Auto-scaling configured  
✅ Monitoring & alerts active  

---

## 📊 Dashboard Access

| Service | URL | Username | Password |
|---|---|---|---|
| **Grafana** | http://localhost:3000 | admin | (generated) |
| **App Health** | http://<EXTERNAL_IP>/health | - | - |
| **Metrics** | http://<EXTERNAL_IP>/metrics | - | - |
| **API Docs** | http://<EXTERNAL_IP>/docs | - | - |

---

## ⚠️ Troubleshooting

### AKS cluster creation fails
```powershell
# Check quota
az vm list-usage --location "eastus" -o table

# If quota exceeded, request increase or use different region
```

### GitLeaks blocks commit
```powershell
# Check what was found
git diff --cached | Select-String "password|secret|token"

# Remove the secret
# Then retry: git commit
```

### Terraform apply fails
```powershell
# Show detailed error
terraform apply tfplan -var-file="terraform.tfvars" -input=false

# Common causes:
# - Azure credentials expired → az login again
# - Quota exceeded → request increase
# - Invalid region → use "East US" or "West US"
```

### Pods won't start
```powershell
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Look for: ImagePullBackOff - ACR credentials issue
#           CrashLoopBackOff - application error
#           Pending - resource quota issue
```

### Can't connect to AKS
```powershell
# Refresh credentials
az aks get-credentials --resource-group "securedeploy-rg-prd" --name "aks-securedeploy-prd" --overwrite-existing

# Test connection
kubectl get nodes
```

---

## 💰 Monitoring Costs

Check your Azure spending daily:

```powershell
# View costs (Azure Portal)
# https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu

# Common costs for Azure Students:
# AKS: ~$5-10/month (2 Standard_B2s nodes)
# ACR: ~$5/month (Basic SKU)
# Storage: ~$1/month (state + logs)
# Bandwidth: ~$2-5/month
# Total: ~$25-30/month
```

Set up budget alerts to avoid surprises!

---

## ✅ Final Checklist

Before finishing, confirm:
- [ ] Azure CLI installed and logged in
- [ ] Service Principal created
- [ ] All 6 GitHub Secrets configured
- [ ] Terraform initialized
- [ ] Terraform plan reviewed and applied
- [ ] AKS cluster verified (kubectl get nodes)
- [ ] Code pushed to GitHub
- [ ] CI/CD pipeline completed
- [ ] Application pods running
- [ ] External IP assigned
- [ ] Application endpoints responding
- [ ] Grafana accessible
- [ ] Monitoring active

---

## 🎓 Next Steps

After deployment:

1. **Monitor**: Watch metrics in Grafana
2. **Scale**: Test HPA by creating load
3. **Update**: Deploy new versions via Git push
4. **Optimize**: Monitor costs and adjust
5. **Secure**: Review security logs weekly

---

## 📞 Support

Questions? Check:
- [SECURITY_INDEX.md](SECURITY_INDEX.md) - Security overview
- [QUICK_START.md](QUICK_START.md) - Quick reference
- [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md) - Detailed checklist
- [SECURITY_REFERENCE.md](SECURITY_REFERENCE.md) - Troubleshooting

