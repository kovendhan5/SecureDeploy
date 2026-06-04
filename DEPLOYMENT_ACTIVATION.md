# 🚀 DEPLOYMENT ACTIVATION GUIDE

**Status:** ✅ Ready for Deployment  
**Date:** June 4, 2026  

---

## 📋 PREREQUISITES

Before starting, you need:

- ✅ Azure CLI installed
- ✅ Azure subscription (verified)
- ✅ Git repo cloned locally (`k:\Devops\SecureDeploy\`)
- ✅ Service Principal created
- ✅ Terraform installed (or ready to install)

---

## 🔑 SECURING YOUR CREDENTIALS

Your Service Principal credentials should have been output to your terminal when created. These **MUST** be saved securely:

```
Do NOT commit these to GitHub!
Do NOT share via email/chat!
Do save in a password manager or secure local file!
```

The 4 values you need:
- `clientId` (appId)
- `clientSecret` (password)
- `subscriptionId`
- `tenantId`

---

## 📝 STEP-BY-STEP DEPLOYMENT (10 Steps)

### Step 1: Configure GitHub Secrets

Go to: **https://github.com/kovendhan5/securedeploy/settings/secrets/actions**

Add 6 repository secrets (click "New repository secret" 6 times):

| Secret Name | Value | Source |
|---|---|---|
| `AZURE_CREDENTIALS` | `{"clientId":"<VALUE>","clientSecret":"<VALUE>","subscriptionId":"<VALUE>","tenantId":"<VALUE>"}` | From terminal output |
| `ACR_LOGIN_SERVER` | `acrsecuredeployprod.azurecr.io` | Fixed value |
| `ACR_NAME` | `acrsecuredeployprod` | Fixed value |
| `AKS_RESOURCE_GROUP` | `securedeploy-rg-prd` | Fixed value |
| `AKS_CLUSTER_NAME` | `aks-securedeploy-prd` | Fixed value |
| `SONAR_TOKEN` | (Get from sonarcloud.io) | Create if needed |

**Time:** ~10 minutes

---

### Step 2: Install Terraform (if needed)

Check if installed:
```powershell
terraform version
```

If not installed, download from: **https://www.terraform.io/downloads.html**

Or use Chocolatey:
```powershell
choco install terraform
```

**Time:** ~5 minutes (or skip if already installed)

---

### Step 3: Initialize Terraform

```powershell
cd k:\Devops\SecureDeploy\terraform
terraform init
```

This downloads the necessary Azure provider files.

**Expected output:**
```
Terraform has been successfully configured!
```

**Time:** ~2 minutes

---

### Step 4: Review Terraform Plan

```powershell
terraform plan -out=tfplan
```

This shows what will be created. **Review carefully!**

**Expected:** ~15-20 resources listed (AKS, ACR, KeyVault, VNet, etc.)

**Time:** ~5 minutes

---

### Step 5: Deploy Infrastructure

```powershell
terraform apply tfplan
```

This creates all Azure resources. **This is the point of no return.**

**Expected output:**
```
Apply complete! Resources added: 15.
```

**Time:** ~5-10 minutes

---

### Step 6: Get AKS Credentials

```powershell
az aks get-credentials --resource-group "securedeploy-rg-prd" --name "aks-securedeploy-prd"
```

This allows kubectl to connect to your cluster.

**Verify:**
```powershell
kubectl get nodes
```

Should show 2 nodes in READY state.

**Time:** ~1 minute

---

### Step 7: Verify Kubernetes Deployment

```powershell
kubectl get pods -n default
kubectl get svc
```

Check that services are created.

**Time:** ~1 minute

---

### Step 8: Push Code to GitHub

```powershell
cd k:\Devops\SecureDeploy

# Stage all changes
git add .

# Commit
git commit -m "Deployment activation - infrastructure ready"

# Push (triggers CI/CD pipeline automatically)
git push origin master
```

**Time:** ~2 minutes

---

### Step 9: Monitor CI/CD Pipeline

Go to: **https://github.com/kovendhan5/securedeploy/actions**

Watch the 8-stage pipeline:
1. ✅ GitLeaks (secret scanning)
2. ✅ Build (compile code)
3. ✅ SonarCloud (quality scan)
4. ✅ Trivy (vulnerability scan)
5. ✅ Docker build (create image)
6. ✅ Push to ACR (container registry)
7. ✅ Terraform Deploy (infrastructure)
8. ✅ Smoke Test (verify endpoints)

**Expected:** All stages pass (green checkmarks)

**Time:** ~5-10 minutes

---

### Step 10: Access Your Application

Once pipeline completes:

1. Get the public IP:
```powershell
kubectl get svc -o wide
```

2. Find the EXTERNAL-IP for the app service (LoadBalancer)

3. Open in browser: `http://<EXTERNAL-IP>`

Should see:
```
{"status": "OK", "service": "SecureDeploy", "timestamp": "..."}
```

**Access Grafana:**
- URL: `http://<EXTERNAL-IP>:3000`
- Username: `admin`
- Password: (auto-generated, check logs for details)

**Time:** ~2 minutes

---

## ✅ DEPLOYMENT COMPLETE!

Your app is now running in production on Azure!

---

## 🆘 TROUBLESHOOTING

### Terraform fails with "insufficient quota"
→ Check Azure quotas: `az vm list-usage --location eastus`

### kubectl get nodes shows "NotReady"
→ Wait 2-3 minutes for nodes to start
→ Check logs: `kubectl describe node <node-name>`

### GitHub Actions pipeline fails
→ Go to the failed workflow
→ Check the error message
→ Review logs in the Actions tab

### Can't access app from browser
→ Verify Service got external IP: `kubectl get svc`
→ Check security group allows port 80: `az network nsg rule list ...`

### Out of budget
→ Delete resources: `terraform destroy`

---

## 📊 ESTIMATED COSTS

```
AKS (2 nodes):        ~$15/day
Container Registry:   ~$0.50/day
KeyVault:            ~$0.50/day
Network:             ~$0.50/day
Storage:             ~$1/day

TOTAL: ~$17-25/day (~$500-750/month)
```

For student tier, this should be well within budget.

---

## 🎉 NEXT STEPS

1. Monitor the app for 24 hours
2. Check Grafana dashboards
3. Review logs in Azure Monitor
4. Set up alerts
5. Plan for scaling if needed

---

**Congratulations! Your SecureDeploy application is live on Azure!** 🚀
