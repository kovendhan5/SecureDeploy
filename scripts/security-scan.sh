#!/bin/bash

###############################################################################
# SecureDeploy Pre-Deployment Security Scanner
# This script checks for common security issues before deployment
# Usage: bash scripts/security-scan.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

check_pass() {
    echo -e "${GREEN}✅ PASS:${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}❌ FAIL:${NC} $1"
    ((CHECKS_FAILED++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  WARN:${NC} $1"
    ((CHECKS_WARNING++))
}

# Main execution
print_header "🔒 SecureDeploy Security Scanner"

SOURCE_SCAN_PATHS=(app terraform k8s monitoring scripts .github)
SOURCE_SCAN_FILES=(--include='*.py' --include='*.tf' --include='*.yml' --include='*.yaml' --include='*.sh' --include='Dockerfile')

###############################################################################
# Phase 1: Secrets Detection
###############################################################################
print_header "Phase 1: Secrets Detection"

# Check for hardcoded secret assignments in implementation files only
if grep -RInE "(password|secret|api_key|apikey|token)[[:space:]]*[:=][[:space:]]*[\"'][^\"']{4,}[\"']" \
    "${SOURCE_SCAN_PATHS[@]}" \
    "${SOURCE_SCAN_FILES[@]}" 2>/dev/null | grep -v "placeholder" > /tmp/secrets.txt 2>&1; then
    check_fail "Potential secrets found in code"
    echo "Found the following hardcoded secret assignments:"
    head -5 /tmp/secrets.txt
    echo "Review with: grep -RInE '(password|secret|api_key|apikey|token)[[:space:]]*[:=][[:space:]]*[\"'\'''][^\"'\''']{4,}[\"'\''']' app terraform k8s monitoring scripts .github"
else
    check_pass "No obvious hardcoded secrets detected"
fi

# Check .gitignore for secret patterns
if grep -E "\.env|\.tfvars|secrets|credentials" .gitignore > /dev/null 2>&1; then
    check_pass ".gitignore includes secret patterns"
else
    check_warning ".gitignore might be missing secret patterns"
fi

###############################################################################
# Phase 2: Terraform Security
###############################################################################
print_header "Phase 2: Terraform Validation"

if command -v terraform &> /dev/null; then
    # Check Terraform syntax
    if cd terraform && terraform validate > /dev/null 2>&1; then
        check_pass "Terraform syntax valid"
        cd ..
    else
        check_fail "Terraform syntax invalid"
        cd ..
    fi
    
    # Check for hardcoded credentials in Terraform assignments only
    if grep -RInE "(password|secret|api_key|apikey|token)[[:space:]]*[:=][[:space:]]*[\"'][^\"']{4,}[\"']" \
        terraform/modules/ --include="*.tf" 2>/dev/null | grep -v "placeholder" > /tmp/tf_secrets.txt 2>&1; then
        check_fail "Terraform files contain potential secrets"
        head -3 /tmp/tf_secrets.txt
    else
        check_pass "No hardcoded secrets in Terraform modules"
    fi
    
    # Check RBAC configuration
    if grep -r "enable_rbac_authorization\|role_assignment" terraform/ --include="*.tf" > /dev/null 2>&1; then
        check_pass "RBAC configuration found in Terraform"
    else
        check_warning "RBAC configuration not verified in Terraform"
    fi
else
    check_warning "Terraform not installed, skipping validation"
fi

###############################################################################
# Phase 3: Docker Security
###############################################################################
print_header "Phase 3: Docker & Container Security"

if [ -f "app/Dockerfile" ]; then
    # Check for non-root user
    if grep -q "USER appuser" app/Dockerfile 2>/dev/null; then
        check_pass "Dockerfile uses non-root user"
    else
        check_fail "Dockerfile does not use non-root user"
    fi
    
    # Check for health check
    if grep -q "HEALTHCHECK" app/Dockerfile 2>/dev/null; then
        check_pass "Dockerfile includes health check"
    else
        check_warning "Dockerfile missing health check"
    fi
    
    # Check for secrets in Dockerfile
    if grep -i "ENV.*password\|ENV.*secret\|ENV.*api_key" app/Dockerfile > /dev/null 2>&1; then
        check_fail "Dockerfile contains environment variable secrets"
    else
        check_pass "No hardcoded secrets in Dockerfile environment"
    fi
else
    check_warning "Dockerfile not found at app/Dockerfile"
fi

###############################################################################
# Phase 4: Kubernetes Security
###############################################################################
print_header "Phase 4: Kubernetes Manifest Security"

# Check deployment security context
if grep -q "runAsNonRoot: true" k8s/deployment.yaml 2>/dev/null; then
    check_pass "Kubernetes pod runs as non-root"
else
    check_fail "Kubernetes pod does not enforce non-root user"
fi

# Check resource limits
if grep -q "cpu:" k8s/deployment.yaml 2>/dev/null && grep -q "memory:" k8s/deployment.yaml 2>/dev/null; then
    check_pass "Kubernetes resource limits defined"
else
    check_fail "Kubernetes resource limits not defined"
fi

# Check for hardcoded secrets in manifests
if grep -i "password\|api_key\|secret" k8s/*.yaml 2>/dev/null | grep -v "SONAR_TOKEN\|ACR_PASSWORD" > /dev/null 2>&1; then
    check_fail "Hardcoded secrets found in Kubernetes manifests"
else
    check_pass "No hardcoded secrets in Kubernetes manifests"
fi

# Check network policy
if [ -f "k8s/networkpolicy.yaml" ]; then
    check_pass "Network policy manifest exists"
else
    check_warning "Network policy manifest not found"
fi

###############################################################################
# Phase 5: GitHub Actions Security
###############################################################################
print_header "Phase 5: GitHub Actions Workflow Security"

if [ -f ".github/workflows/ci.yml" ]; then
    # Check GitLeaks runs first
    if head -100 .github/workflows/ci.yml | grep -q "gitleaks"; then
        check_pass "GitLeaks secret scanning enabled"
    else
        check_fail "GitLeaks secret scanning not found"
    fi
    
    # Check for secret exposure in logs
    if grep -q "echo.*secret\|echo.*password" .github/workflows/ci.yml 2>/dev/null; then
        check_fail "Secrets may be logged in GitHub Actions"
    else
        check_pass "No obvious secret logging in GitHub Actions"
    fi
    
    # Check Trivy scanning
    if grep -q "Trivy\|trivy" .github/workflows/ci.yml 2>/dev/null; then
        check_pass "Container image scanning (Trivy) configured"
    else
        check_fail "Container scanning (Trivy) not configured"
    fi
else
    check_warning "GitHub Actions workflow not found"
fi

###############################################################################
# Phase 6: Code Quality
###############################################################################
print_header "Phase 6: Code Quality & SAST"

# Check SonarCloud configuration
if [ -f "sonar-project.properties" ]; then
    check_pass "SonarCloud project properties found"
else
    check_warning "SonarCloud project properties not found"
fi

# Check Python syntax (if Python available)
if command -v python3 &> /dev/null; then
    if python3 -m py_compile app/main.py > /dev/null 2>&1; then
        check_pass "Python syntax valid"
    else
        check_fail "Python syntax errors found"
    fi
fi

# Check GitLeaks config
if [ -f ".gitleaks.toml" ]; then
    check_pass "GitLeaks configuration found"
else
    check_warning "GitLeaks configuration not found"
fi

###############################################################################
# Phase 7: Configuration Files
###############################################################################
print_header "Phase 7: Configuration Validation"

# Check .trivyignore
if [ -f ".trivyignore" ]; then
    check_pass "Trivy ignore file exists"
else
    check_warning "No .trivyignore file for CVE exceptions"
fi

# Check for commented-out secrets
if grep -r "# password\|# secret\|# api_key" . --exclude-dir=.git --exclude-dir=terraform/.terraform 2>/dev/null | grep -v "SECURITY_AUDIT\|PRE_DEPLOYMENT" > /tmp/commented_secrets.txt 2>&1; then
    LINES=$(wc -l < /tmp/commented_secrets.txt)
    if [ "$LINES" -gt 0 ]; then
        check_warning "Commented-out secrets found (verify they're not accidentally uncommented)"
        head -2 /tmp/commented_secrets.txt
    fi
fi

###############################################################################
# Phase 8: Summary
###############################################################################
print_header "Security Scan Summary"

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))

echo "Total Checks: $TOTAL"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo -e "${YELLOW}Warnings: $CHECKS_WARNING${NC}"

if [ "$CHECKS_FAILED" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ALL CRITICAL SECURITY CHECKS PASSED${NC}"
    if [ "$CHECKS_WARNING" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Review $CHECKS_WARNING warnings before deployment${NC}"
    fi
    exit 0
else
    echo ""
    echo -e "${RED}❌ SECURITY ISSUES FOUND - DO NOT DEPLOY${NC}"
    echo -e "${RED}Fix the $CHECKS_FAILED failing checks above${NC}"
    exit 1
fi
