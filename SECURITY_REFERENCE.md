# 🔐 Security Quick Reference Guide

## Key Security Concepts

### Secrets Management
- **Never hardcode credentials** in code, config files, or Dockerfiles
- **Use Azure Key Vault** for centralized secret storage
- **GitHub Secrets** for CI/CD pipeline credentials
- **Environment variables** at runtime (never in code)

### Identity & Access Control
- **Service Principal:** Azure identity for automation (CI/CD, Terraform)
- **Managed Identity:** Azure identity for resources (AKS, containers)
- **RBAC:** Role-Based Access Control - assign minimal permissions needed
- **Principle of Least Privilege:** Give only required permissions

### Container Security
- **Non-root user:** Run containers as non-root (UID 1000+)
- **Read-only FS:** Mount root filesystem as read-only
- **No privileged mode:** Never run with --privileged or CAP_SYS_ADMIN
- **Vulnerability scanning:** Scan images with Trivy for CVEs

### Kubernetes Security
- **Security context:** Define pod security requirements
- **Network policies:** Restrict pod-to-pod communication
- **Resource limits:** Prevent DoS via resource exhaustion
- **Health probes:** Ensure pods are actually healthy

### CI/CD Security
- **Shift-left:** Run security scans early in pipeline
- **Fail fast:** Block deployment on security issues
- **GitLeaks:** Detect credentials in code before commit
- **SAST:** Static code analysis (SonarCloud)
- **DAST:** Dynamic scanning (in advanced setups)

---

## SecureDeploy Security Features

### ✅ What's Protected

| What | How | Tools |
|---|---|---|
| **Secrets** | Stored only in Key Vault + GitHub Secrets | GitLeaks detects leaks |
| **Code** | Scanned for vulnerabilities | SonarCloud SAST |
| **Images** | Scanned for CVEs | Trivy |
| **Containers** | Run as non-root with read-only FS | Kubernetes SecurityContext |
| **Network** | Restricted with NetworkPolicies | Kubernetes NetworkPolicy |
| **Access** | RBAC on all resources | Azure RBAC |
| **Secrets at Runtime** | Retrieved safely | Managed Identity |
| **Deployment** | Rolls back on failure | kubectl rollout undo |

---

## Common Security Patterns

### Pattern 1: Safe Credential Handling
```
❌ WRONG:
  DB_PASSWORD="mysecretpassword"  # In code!
  
✅ CORRECT:
  DB_PASSWORD=$(cat /run/secrets/db_password)  # From secret at runtime
```

### Pattern 2: Secure AKS Pod
```yaml
✅ CORRECT:
securityContext:
  runAsNonRoot: true          # Don't run as root
  runAsUser: 1000             # Use specific UID
  readOnlyRootFilesystem: true # Can't modify system
  allowPrivilegeEscalation: false  # No escalation
  capabilities:
    drop:
    - ALL               # Remove all capabilities
```

### Pattern 3: Network Policy
```yaml
✅ CORRECT:
ingress:
- from:
  - podSelector:      # Only allow from monitoring pods
      matchLabels:
        app: prometheus
  ports:
  - protocol: TCP
    port: 8000        # Only port 8000 allowed
```

### Pattern 4: Secret Storage in Key Vault
```bash
✅ CORRECT:
# Store in Key Vault
az keyvault secret set \
  --vault-name kv-securedeploy-prod \
  --name sonar-token \
  --value <actual_token>

# Retrieve at runtime (never in code)
SONAR_TOKEN=$(az keyvault secret show \
  --vault-name kv-securedeploy-prod \
  --name sonar-token \
  --query value -o tsv)
```

---

## Security Scanning Commands

### Check for Secrets
```bash
# Find potential secrets in code
grep -r "password\|secret\|api_key\|apikey" . \
  --exclude-dir=.git \
  --exclude="*.tfstate"

# Check only staged changes (before commit)
git diff --cached | grep -i "password\|secret"
```

### Validate Terraform Security
```bash
# Check RBAC configuration
grep -r "role_assignment\|enable_rbac" terraform/

# Verify no hardcoded secrets
grep -r "password\|secret" terraform/ --exclude-dir=.terraform
```

### Check Docker Image Security
```bash
# Build and scan image
docker build -t securedeploy:test app/
trivy image securedeploy:test

# Check for non-root user
docker inspect securedeploy:test | grep User
```

### Verify Kubernetes Security
```bash
# Check pod security context
kubectl get pod -o jsonpath='{.items[*].spec.containers[*].securityContext}'

# Check network policies
kubectl get networkpolicy

# Verify RBAC
kubectl auth can-i get secrets --as=system:serviceaccount:default:appname
```

---

## Security Checklist Before Pushing

- [ ] Run `bash scripts/security-scan.sh` - should pass
- [ ] Check `git log` has no exposed secrets
- [ ] Verify all GitHub Secrets are configured
- [ ] Review Terraform plan for hardcoded values
- [ ] Check Kubernetes manifests for security context
- [ ] Ensure Dockerfile uses non-root user
- [ ] Verify GitLeaks configuration is active

---

## What Each Tool Does

### GitLeaks
- **What:** Detects hardcoded secrets in git repositories
- **When:** Runs as first stage of CI/CD pipeline
- **Action:** Blocks deployment if secrets found
- **Config:** `.gitleaks.toml`

### SonarCloud
- **What:** SAST - scans source code for security issues
- **When:** Runs after unit tests, before image build
- **Action:** Blocks if Quality Gate fails
- **Config:** `sonar-project.properties`

### Trivy
- **What:** Scans container images for CVE vulnerabilities
- **When:** Runs after Docker build
- **Action:** Blocks if HIGH/CRITICAL CVEs found
- **Config:** `.trivyignore` (for exceptions)

### RBAC
- **What:** Azure role-based access control
- **When:** Applied during infrastructure provisioning
- **Action:** Restricts access to AKS, Key Vault, ACR
- **Config:** Terraform role_assignment resources

### NetworkPolicy
- **What:** Kubernetes network policies
- **When:** Applied to deployed pods
- **Action:** Restricts pod-to-pod communication
- **Config:** `k8s/networkpolicy.yaml`

---

## Incident Response

### If You Accidentally Commit a Secret

**IMMEDIATE ACTIONS:**
```bash
# 1. Revoke the credential in Azure
az keyvault secret delete --vault-name kv-securedeploy-prod --name <secret>

# 2. Remove from Git history (WARNING: destructive)
git filter-branch --tree-filter 'git rm --cached --ignore-unmatch <file>'

# 3. Force push to fix (only if repo is private)
git push --force-with-lease origin main
```

### If Image Scan Fails with CVE

```bash
# 1. Check what CVE was found
trivy image acrsecuredeployprod.azurecr.io/securedeploy:latest

# 2. If it's base image issue, update base image version
# In Dockerfile, change: FROM python:3.11-slim
# To:                   FROM python:3.11-slim-bookworm (newer)

# 3. Add to .trivyignore if it's a false positive
echo "CVE-2021-12345" >> .trivyignore

# 4. Rebuild and re-push
```

### If Deployment Fails Security Context

```bash
# Check security context
kubectl describe pod securedeploy-app

# If issue is found, update deployment:
kubectl set securitycontext --as-user=1000 deployment/securedeploy-app

# Or update k8s/deployment.yaml and re-deploy
```

---

## Quick Reference: What Runs When

```
LOCAL DEVELOPMENT
├── Code written
├── Git commit (GitLeaks checks locally)
└── Git push

GITHUB CI PIPELINE (automated)
├── GitLeaks scan (blocks if secrets)
├── Build & Unit tests
├── SonarCloud SAST
├── Docker build
├── Trivy image scan (blocks on HIGH/CRITICAL)
└── Push to ACR (only if all pass)

KUBERNETES DEPLOYMENT (automated)
├── Terraform provisions infrastructure
├── kubectl applies manifests
├── Deployment with 2 replicas
├── Health checks pass
└── Smoke test /health endpoint

CONTINUOUS MONITORING
├── Prometheus scrapes metrics
├── Grafana displays dashboard
└── Alerts on errors > 5%
```

---

## Resources & Links

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Microsoft Cloud Security Baseline](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/govern/security-baseline/)

### Tools Used
- [GitLeaks](https://github.com/gitleaks/gitleaks)
- [SonarCloud](https://sonarcloud.io/)
- [Trivy](https://github.com/aquasecurity/trivy)
- [OWASP ZAP](https://www.zaproxy.org/) (for advanced testing)

### Azure Security
- [Azure Security Baseline](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/govern/security-baseline/)
- [AKS Security Best Practices](https://docs.microsoft.com/en-us/azure/aks/concepts-security)
- [Azure Key Vault Best Practices](https://docs.microsoft.com/en-us/azure/key-vault/general/best-practices)

---

## Glossary

| Term | Definition |
|---|---|
| **RBAC** | Role-Based Access Control - limit access based on roles |
| **CVE** | Common Vulnerabilities and Exposures - known security flaws |
| **SAST** | Static Application Security Testing - scan code without running it |
| **DAST** | Dynamic Application Security Testing - test running app for issues |
| **OPA** | Open Policy Agent - policy enforcement engine |
| **PSP** | Pod Security Policy - Kubernetes security policies (deprecated) |
| **AuthZ** | Authorization - who can do what |
| **AuthN** | Authentication - who are you |
| **CredentialVault** | Secure storage for secrets |
| **NonRoot** | Not running as root user |
| **ReadOnlyFS** | Cannot modify system files |
| **CAP** | Linux capability - specific privileges not related to UID |

---

**Remember:** Security is never "done" - it's a continuous process! 🔐

