# Pre-Deployment Security Checklist

## Phase 1: Code Review (Before Git Push)

- [ ] **No secrets in repository**
  ```bash
  git log -p | grep -iE "password|secret|token|apikey|api_key" | head
  ```
  
- [ ] **GitLeaks configuration valid**
  ```bash
  cat .gitleaks.toml | head -5
  ```
  
- [ ] **SonarCloud project initialized**
  - [ ] Visit https://sonarcloud.io/organizations/kovendhan5/projects
  - [ ] Project is connected to GitHub repo
  - [ ] Quality Gate is configured

- [ ] **All Python code has no hardcoded values**
  ```bash
  grep -r "password\|secret\|token\|apikey" app/ --exclude-dir=tests
  ```

---

## Phase 2: Terraform Validation

- [ ] **Terraform syntax valid**
  ```bash
  cd terraform
  terraform fmt -check
  terraform validate
  ```

- [ ] **No hardcoded credentials in Terraform**
  ```bash
  grep -r "password\|secret\|api_key" *.tf modules/
  ```

- [ ] **Backend configuration ready**
  ```bash
  # Verify state storage account exists
  az storage account show --name stsecuredeploytf --resource-group rg-securedeploy-tfstate
  ```

- [ ] **Review Terraform plan (READ CAREFULLY!)**
  ```bash
  terraform plan -out=tfplan
  # Review output for:
  # - Correct region (East US)
  # - Correct VM sizes (Standard_B2s)
  # - RBAC roles properly assigned
  ```

---

## Phase 3: Docker Security

- [ ] **Dockerfile uses non-root user**
  ```bash
  grep -A5 "USER appuser" app/Dockerfile
  ```

- [ ] **No secrets in Dockerfile**
  ```bash
  grep -i "env.*password\|secret\|apikey" app/Dockerfile
  ```

- [ ] **Health check configured**
  ```bash
  grep -A3 "HEALTHCHECK" app/Dockerfile
  ```

- [ ] **Build succeeds locally** (optional)
  ```bash
  cd app
  docker build -t securedeploy:test .
  ```

---

## Phase 4: Kubernetes Configuration

- [ ] **Security context enforced**
  ```bash
  grep -A10 "securityContext:" k8s/deployment.yaml | grep "runAsNonRoot: true"
  ```

- [ ] **Resource limits defined**
  ```bash
  grep -A5 "resources:" k8s/deployment.yaml | grep -E "cpu|memory"
  ```

- [ ] **Health probes configured**
  ```bash
  grep -E "livenessProbe|readinessProbe" k8s/deployment.yaml
  ```

- [ ] **No hardcoded secrets in manifests**
  ```bash
  grep -iE "password|secret" k8s/*.yaml
  ```

---

## Phase 5: GitHub Actions Configuration

- [ ] **CI workflow has correct secret usage**
  ```bash
  grep "secrets\." .github/workflows/ci.yml | wc -l
  ```

- [ ] **No secrets displayed in logs**
  ```bash
  grep -i "echo.*secret\|echo.*password" .github/workflows/*.yml
  ```

- [ ] **GitLeaks runs first in CI pipeline**
  ```bash
  head -50 .github/workflows/ci.yml | grep -i "gitleaks"
  ```

- [ ] **Trivy fails on HIGH/CRITICAL CVEs**
  ```bash
  grep "exit-code:" .github/workflows/ci.yml | grep "1"
  ```

---

## Phase 6: Azure Secrets Configuration

- [ ] **Create GitHub Secrets** (6 required)
  ```
  ACR_LOGIN_SERVER      (e.g., acrsecuredeployprod.azurecr.io)
  ACR_NAME              (e.g., acrsecuredeployprod)
  AKS_RESOURCE_GROUP    (e.g., rg-securedeploy-prod)
  AKS_CLUSTER_NAME      (e.g., aks-securedeploy-prod)
  SONAR_TOKEN           (get from https://sonarcloud.io/account/security/tokens)
  AZURE_CREDENTIALS     (JSON output from az ad sp create-for-rbac)
  ```

- [ ] **Service Principal created with minimum permissions**
  ```bash
  # Verify SP has only Contributor (can be narrowed further)
  az role assignment list --assignee <sp-app-id>
  ```

- [ ] **SonarCloud token is valid**
  ```bash
  # Test: curl -u <token>: https://sonarcloud.io/api/authentication/validate
  ```

---

## Phase 7: Final Security Checks

- [ ] **.gitignore includes secrets patterns**
  ```bash
  grep -E "\.env|\.tfvars|secrets|credentials" .gitignore
  ```

- [ ] **No secrets in README or documentation**
  ```bash
  grep -iE "password|api.?key|secret.*=|token.*=" README.md SETUP.md
  ```

- [ ] **All files have proper permissions**
  ```bash
  ls -la terraform/ | grep -v "^d" | grep -v "\.tf"
  ```

- [ ] **Git history is clean**
  ```bash
  git log --oneline | wc -l  # Should be < 10 commits
  ```

---

## Phase 8: Pre-Push Validation

**Run this before pushing to GitHub:**

```bash
#!/bin/bash
set -e

echo "🔒 Running pre-push security checks..."

# Check for secrets
echo "  ✓ Checking for hardcoded secrets..."
if git diff --cached | grep -iE "password|api.?key|secret.*=" > /dev/null; then
  echo "  ❌ FAILED: Secrets found in staged changes"
  exit 1
fi

# Verify Terraform
echo "  ✓ Validating Terraform..."
cd terraform && terraform validate && cd ..

# Verify Python syntax
echo "  ✓ Checking Python syntax..."
python -m py_compile app/main.py

# Check YAML syntax
echo "  ✓ Validating Kubernetes YAML..."
kubectl apply --dry-run=client -f k8s/deployment.yaml

echo "✅ All security checks passed!"
echo "🚀 Safe to push to GitHub"
```

---

## Phase 9: Post-Deployment Verification

**After `terraform apply` and pipeline succeeds:**

- [ ] **AKS cluster is running**
  ```bash
  kubectl get nodes
  kubectl get pods --all-namespaces
  ```

- [ ] **App is deployed**
  ```bash
  kubectl get deployment securedeploy-app
  kubectl get svc securedeploy-app
  ```

- [ ] **App health check passes**
  ```bash
  kubectl port-forward svc/securedeploy-app 8000:80 &
  curl http://localhost:8000/health
  ```

- [ ] **No suspicious logs**
  ```bash
  kubectl logs -l app=securedeploy-app --tail=20 | grep -iE "error|warning|critical"
  ```

- [ ] **RBAC is properly configured**
  ```bash
  kubectl auth can-i get secrets --as=system:serviceaccount:default:securedeploy-app
  ```

---

## Phase 10: Incident Response & Monitoring

### If a Secret is Committed

```bash
# 1. IMMEDIATELY revoke the token/credential in Azure
az keyvault secret delete --vault-name kv-securedeploy-prod --name <secret-name>

# 2. Remove from Git history
git filter-branch --tree-filter 'grep -r "secret_value" . && rm $f'

# 3. Force push to fix (WARNING: destructive)
git push --force-with-lease origin main

# 4. Rotate all secrets
az ad sp credential reset --id <sp-app-id>
```

### Continuous Monitoring

```bash
# 1. Check Azure Activity Log
az monitor activity-log list --resource-group rg-securedeploy-prod --max-items 20

# 2. Review Key Vault access logs
az keyvault secret show --name SONAR_TOKEN --vault-name kv-securedeploy-prod

# 3. Monitor pipeline failures
# Check GitHub > Actions for any CI/CD failures

# 4. Review Azure Security Center
# https://portal.azure.com > Security Center > Secure Score
```

---

## 💡 Quick Reference Commands

```bash
# Check for all common secret patterns
grep -rn "password\|secret\|token\|api_key\|apikey" \
  --exclude-dir=.git \
  --exclude-dir=terraform/.terraform \
  --exclude="*.tfstate" \
  .

# Verify no secrets in staged Git changes
git diff --cached | grep -iE "password|secret"

# Validate all YAML files
for f in k8s/*.yaml; do kubectl apply --dry-run=client -f "$f" && echo "✓ $f"; done

# Check container image security
docker inspect securedeploy:v1 | grep -E "User|Hostname"

# Verify Kubernetes pod running securely
kubectl get pod -o jsonpath='{.items[*].spec.containers[*].securityContext}'
```

---

## ✅ Sign-Off

- [ ] All phases completed
- [ ] No secrets found in code
- [ ] All security controls verified
- [ ] Ready to push to GitHub
- [ ] Ready for deployment

**Date Checked:** ___________  
**Checked By:** ___________  
**Status:** ✅ APPROVED / ❌ ISSUES FOUND

---
