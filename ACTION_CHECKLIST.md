# ☑️ DEPLOYMENT CHECKLIST

**Choose Your Speed → Follow the Steps**

---

## 🚀 THREE DEPLOYMENT PATHS

Pick one based on your comfort level:

---

## ⚡ PATH A: FULL GUIDED (Recommended - 60 min)

**Best for:** First-time deployment, understanding every step

### Quick Overview
```
Step 1: Save credentials securely
Step 2: Configure 6 GitHub Secrets
Step 3: Install Terraform
Step 4: Initialize Terraform  
Step 5: Plan infrastructure
Step 6: Deploy infrastructure
Step 7: Get AKS credentials
Step 8: Verify deployment
Step 9: Push code to GitHub
Step 10: Monitor CI/CD
```

→ **Go to [DEPLOYMENT_ACTIVATION.md](DEPLOYMENT_ACTIVATION.md) for detailed steps**

---

## 🏃 PATH B: QUICK DEPLOY (40 min - Experienced Only)

**Best for:** Experienced DevOps engineers who know what they're doing

### One-Liner Summary
```
Configure Secrets → Install TF → terraform init/plan/apply → kubectl creds → git push
```

### Execute These Commands

```powershell
# 1. Save your Service Principal credentials
# (From terminal output - NOT from GitHub!)

# 2. Go to GitHub: github.com/kovendhan5/securedeploy/settings/secrets/actions
# Add 6 secrets (see table below)

# 3. Install Terraform (if needed)
terraform --version

# 4. Deploy infrastructure
cd k:\Devops\SecureDeploy\terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 5. Get cluster credentials
az aks get-credentials --resource-group "securedeploy-rg-prd" --name "aks-securedeploy-prd"
kubectl get nodes

# 6. Push code (triggers CI/CD)
cd k:\Devops\SecureDeploy
git add .
git commit -m "Deploy to production"
git push origin master

# 7. Monitor
# Open: https://github.com/kovendhan5/securedeploy/actions
# Watch the 8-stage pipeline complete
```

### GitHub Secrets Table

| Secret Name | Value |
|---|---|
| `AZURE_CREDENTIALS` | `{"clientId":"<YOUR_APP_ID>","clientSecret":"<YOUR_PASSWORD>","subscriptionId":"<YOUR_SUB_ID>","tenantId":"<YOUR_TENANT_ID>"}` |
| `ACR_LOGIN_SERVER` | `acrsecuredeployprod.azurecr.io` |
| `ACR_NAME` | `acrsecuredeployprod` |
| `AKS_RESOURCE_GROUP` | `securedeploy-rg-prd` |
| `AKS_CLUSTER_NAME` | `aks-securedeploy-prd` |
| `SONAR_TOKEN` | Get from sonarcloud.io |

---

## 🎓 PATH C: MOST THOROUGH (90 min - Maximum Verification)

**Best for:** Compliance requirements, audits, zero risk

→ **Go to [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md) for 10-phase verification**

Includes:
- ✅ Security review
- ✅ Code audit
- ✅ Infrastructure review
- ✅ Network validation
- ✅ RBAC verification
- ✅ Final sign-off

---

## ✅ PRE-FLIGHT CHECKLIST (5 Min)

Do these before choosing your path:

```
Azure
├─ ✅ Azure CLI installed: az --version ✓
├─ ✅ Logged in: az account list ✓
├─ ✅ Subscription active ✓
└─ ✅ Quota available ✓

Local Tools
├─ ✅ Git installed
├─ ✅ Code in k:\Devops\SecureDeploy\
└─ ✅ (Terraform installer ready? or already installed)

GitHub
├─ ✅ Repository ready: https://github.com/kovendhan5/securedeploy
├─ ✅ Can access Actions tab ✓
├─ ✅ Can access Secrets settings ✓
└─ ✅ Branch: master ✓

Credentials
├─ ✅ Service Principal appId saved
├─ ✅ Service Principal password saved
├─ ✅ Subscription ID saved
├─ ✅ Tenant ID saved
└─ ✅ Stored securely (password manager or .env, NOT in GitHub!)
```

---

## 🎯 WHICH PATH FOR YOU?

**I'm new to deployment:**
→ **PATH A** (Full guided with all details)

**I've done this before:**
→ **PATH B** (Quick deploy, trust yourself)

**I need to document everything:**
→ **PATH C** (Thorough with verification)

---

## 📊 TIMING BREAKDOWN

### Path A (Fully Guided)
```
Configure Secrets:      10 min
Install Terraform:       5 min
Terraform init:          2 min
Terraform plan:          5 min
Terraform apply:        10 min
kubectl setup:           2 min
Push code:               2 min
Watch pipeline:          5 min
Access app:              2 min
                        -------
TOTAL:                 ~43 min
```

Plus verification and setup: ~60 min total

### Path B (Quick Deploy)
```
Configure Secrets:      10 min
Terraform (all):        15 min
kubectl + push:          5 min
Watch pipeline:          5 min
                        -------
TOTAL:                 ~35 min
```

### Path C (Thorough)
```
Security review:       15 min
Infrastructure review: 20 min
Terraform verify:      15 min
GitHub verify:         10 min
Final review:          10 min
Deployment:            15 min
Post-verify:            5 min
                        -------
TOTAL:                 ~90 min
```

---

## 🚨 CRITICAL REMINDERS

### ⚠️ CREDENTIALS
- Do NOT commit credentials to GitHub
- Save them securely (password manager, .env file)
- Use ONLY via GitHub Secrets
- If leaked, regenerate immediately

### ⚠️ TERRAFORM
- Always review `terraform plan` output before applying
- Check resource count and types
- Verify regions and sizes
- Watch for destructive changes (marked with -)

### ⚠️ GITHUB ACTIONS
- Check all 8 pipeline stages turn green
- If any stage fails, read the error
- Common failures: secrets not set, quota exceeded
- Retry after fixing

### ⚠️ COSTS
- This deployment costs ~$20-30/day
- Make sure you have budget
- Use `terraform destroy` if over budget
- Student tier should cover this

---

## 📞 STUCK?

| Issue | Solution |
|---|---|
| "Resource already exists" | Already deployed - verify via Azure Portal |
| "Insufficient quota" | Request quota increase (24 hrs) or downsize |
| "Pipeline failed" | Check GitHub Actions log |
| "Can't connect to AKS" | Run `az aks get-credentials` again |
| "App not accessible" | Check LoadBalancer got external IP |
| "Out of budget" | Run `terraform destroy` to cleanup |

---

## ✨ SUCCESS CRITERIA

Deployment is successful when:

- ✅ All 8 pipeline stages show green checkmarks
- ✅ Pods are RUNNING in Kubernetes  
- ✅ App responds at external IP on port 80
- ✅ Grafana dashboard accessible on port 3000
- ✅ All 4 app endpoints return 200 OK:
  - `/` → {"status": "OK"}
  - `/health` → Alive
  - `/info` → Version info
  - `/metrics` → Prometheus metrics

---
