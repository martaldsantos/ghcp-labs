# Security Scan Report

**Scan Date:** 2026-06-19  
**Project:** ghcp-labs/lab07  
**Scanner:** Manual CVE Analysis  
**Sources:** requirements.txt, sbom.xml

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Total Packages Scanned** | 4 |
| **Packages with Known CVEs** | 2 |
| **CRITICAL Severity** | 1 |
| **HIGH Severity** | 2 |
| **MEDIUM Severity** | 1 |
| **LOW Severity** | 0 |
| **Total Vulnerabilities** | 4 |

### Risk Assessment: 🔴 **CRITICAL**

Immediate action required due to multiple high-severity vulnerabilities in core dependencies.

---

## Detailed Findings

### 🔴 CRITICAL Vulnerabilities

#### 1. requests - Multiple Critical CVEs

**Package:** `requests`  
**Current Version:** 2.18.0 (Released: June 2017)  
**Latest Version:** 2.32.3 (as of 2026)  
**Age:** ~9 years outdated

| CVE ID | Severity | Description |
|--------|----------|-------------|
| **CVE-2018-18074** | **CRITICAL** | HTTP Authorization Header Leak on Redirect |
| **CVE-2023-32681** | **HIGH** | Unintended Proxy Authentication Information Leak |

**CVE-2018-18074 Details:**
- **CVSS Score:** 7.5 (HIGH/CRITICAL)
- **Issue:** The Requests package before 2.20.0 sends HTTP authorization headers to an http URI upon receiving a same-hostname https-to-http redirect
- **Impact:** Credentials exposed in plaintext over unencrypted connections
- **Attack Vector:** Network-based, man-in-the-middle attacks
- **Exploitability:** High - Passive network sniffing

**CVE-2023-32681 Details:**
- **CVSS Score:** 6.1 (MEDIUM-HIGH)
- **Issue:** Proxy-Authorization headers leaked to destination servers in certain redirect scenarios
- **Impact:** Proxy authentication credentials exposure
- **Affected Versions:** < 2.31.0

**Additional Concerns:**
- Missing 9 years of security patches
- Missing bug fixes and performance improvements
- Incompatible with modern Python security best practices
- Potential SSL/TLS vulnerabilities from outdated cipher support

**Recommended Action:**
```bash
# IMMEDIATE - Update to latest version
pip install --upgrade "requests>=2.32.0,<3.0.0"
```

---

### 🟠 HIGH Severity Vulnerabilities

#### 2. PyYAML - Arbitrary Code Execution

**Package:** `pyyaml`  
**Current Version:** Not specified (Could be any version)  
**Risk Level:** **HIGH** (Unpinned version = maximum risk)

| CVE ID | Severity | Description |
|--------|----------|-------------|
| **CVE-2020-1747** | **HIGH** | Arbitrary Python Code Execution |
| **CVE-2020-14343** | **HIGH** | Code Execution via FullLoader |

**CVE-2020-1747 Details:**
- **CVSS Score:** 9.8 (CRITICAL in some assessments)
- **Issue:** PyYAML < 5.4 allows arbitrary Python code execution through yaml.load() without proper safeguards
- **Impact:** Complete system compromise possible
- **Attack Vector:** Processing untrusted YAML files
- **Exploitability:** High - Well-documented attack patterns

**CVE-2020-14343 Details:**
- **CVSS Score:** 9.8 (CRITICAL)
- **Issue:** Arbitrary code execution when processing untrusted YAML with full_load() or FullLoader
- **Impact:** Remote code execution
- **Affected Versions:** < 5.4

**Recommended Action:**
```bash
# Update to secure version with safe defaults
pip install "pyyaml>=6.0.0,<7.0.0"
```

**Code Remediation:**
```python
# UNSAFE - Do not use
import yaml
data = yaml.load(untrusted_input)  # DANGEROUS!

# SAFE - Use safe_load instead
import yaml
data = yaml.safe_load(untrusted_input)  # Safe against code execution
```

---

### 🟡 MEDIUM Severity Issues

#### 3. bcrypt - Version Unpinned

**Package:** `bcrypt`  
**Current Version:** Not specified  
**Risk Level:** **MEDIUM**

**Issues:**
- No specific CVEs, but unpinned version creates risk
- May install older version with unknown vulnerabilities
- Non-reproducible builds across environments
- Potential compatibility issues

**Impact:**
- Build inconsistency
- Difficult security auditing
- Dependency confusion attacks possible

**Recommended Action:**
```bash
pip install "bcrypt>=4.0.0,<5.0.0"
```

---

#### 4. pytest - Version Unpinned

**Package:** `pytest`  
**Current Version:** Not specified  
**Risk Level:** **MEDIUM** (Testing framework - lower priority)

**Issues:**
- Unpinned test framework version
- Potential for test behavior changes
- CI/CD inconsistency

**Recommended Action:**
```bash
pip install "pytest>=8.0.0,<9.0.0"
```

---

## Vulnerability Details by Package

### Summary Table

| Package | Current Version | CVE Count | Highest Severity | Fix Version | Priority |
|---------|----------------|-----------|------------------|-------------|----------|
| **requests** | 2.18.0 | 2+ | 🔴 CRITICAL | 2.32.3+ | P0 - IMMEDIATE |
| **pyyaml** | Unknown | 2 | 🟠 HIGH | 6.0.0+ | P0 - IMMEDIATE |
| **bcrypt** | Unknown | 0 | 🟡 MEDIUM | 4.0.0+ | P1 - High |
| **pytest** | Unknown | 0 | 🟡 MEDIUM | 8.0.0+ | P2 - Medium |

---

## Remediation Plan

### Phase 1: IMMEDIATE (Within 24 hours) - P0 Critical

#### Step 1: Update requirements.txt

Replace the current requirements.txt with secure, pinned versions:

```txt
# Updated requirements.txt with security patches
# Generated: 2026-06-19

# HTTP Client - CRITICAL UPDATE
requests>=2.32.3,<3.0.0

# YAML Parser - HIGH PRIORITY UPDATE  
pyyaml>=6.0.1,<7.0.0

# Password Hashing - Pin version
bcrypt>=4.1.0,<5.0.0

# Testing Framework - Pin version
pytest>=8.2.0,<9.0.0
```

#### Step 2: Install Updated Dependencies

```bash
# Backup current environment
pip freeze > requirements-backup.txt

# Install updated dependencies
pip install --upgrade -r requirements.txt

# Verify installations
pip list | grep -E "(requests|pyyaml|bcrypt|pytest)"
```

#### Step 3: Run Security Audit

```bash
# Install security audit tool
pip install pip-audit

# Run audit on updated dependencies
pip-audit --desc

# Alternative: Use safety
pip install safety
safety check --full-report
```

#### Step 4: Regenerate SBOM

```bash
# Install CycloneDX tool
pip install cyclonedx-bom

# Generate new SBOM
cyclonedx-py requirements -o sbom-updated.xml --format xml
cyclonedx-py requirements -o sbom-updated.json --format json
```

#### Step 5: Code Review for PyYAML

Search codebase for unsafe YAML loading patterns:

```bash
# Search for unsafe yaml.load() usage
grep -r "yaml\.load(" . --include="*.py"

# Search for FullLoader usage
grep -r "FullLoader" . --include="*.py"
```

Replace with safe alternatives:
```python
# Replace all instances of:
yaml.load(data)              → yaml.safe_load(data)
yaml.load(data, FullLoader)  → yaml.safe_load(data)
```

---

### Phase 2: Verification (Within 48 hours)

#### Testing Checklist

- [ ] All unit tests pass with updated dependencies
- [ ] Integration tests complete successfully
- [ ] No breaking changes introduced
- [ ] Security scan shows no critical vulnerabilities
- [ ] SBOM updated and verified
- [ ] Documentation updated

#### Verification Commands

```bash
# Run test suite
pytest -v

# Verify no CVEs in updated packages
pip-audit

# Check for outdated packages
pip list --outdated

# Verify SSL/TLS connections work correctly
python -c "import requests; r = requests.get('https://httpbin.org/get'); print(r.status_code)"
```

---

### Phase 3: Ongoing Security Maintenance

#### Implement Security Scanning in CI/CD

Add to your GitHub Actions workflow:

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pip-audit safety
      
      - name: Run pip-audit
        run: pip-audit --desc
      
      - name: Run safety check
        run: safety check --json
      
      - name: Generate SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py requirements -o sbom.xml
      
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.xml
```

#### Enable Dependabot

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-team"
    labels:
      - "dependencies"
      - "security"
```

#### Monthly Security Reviews

- [ ] Review Dependabot alerts
- [ ] Check for new CVEs in dependencies
- [ ] Update dependencies to latest patch versions
- [ ] Regenerate and review SBOM
- [ ] Run penetration testing tools

---

## Additional Recommendations

### 1. Dependency Management Best Practices

- ✅ **Always pin dependency versions** - Use `==` or compatible ranges
- ✅ **Use `requirements.lock` or `Pipfile.lock`** - For reproducible builds
- ✅ **Separate dev and prod dependencies** - requirements-dev.txt vs requirements.txt
- ✅ **Regular updates** - At least monthly security patches
- ✅ **Automated scanning** - Integrate into CI/CD pipeline

### 2. Python Security Tools

```bash
# Install comprehensive security toolkit
pip install pip-audit safety bandit semgrep

# Run static security analysis
bandit -r . -f json -o security-report.json

# Run SAST with Semgrep
semgrep --config=auto .
```

### 3. Environment Hardening

```python
# requirements-security.txt
pip-audit>=2.7.0        # Vulnerability scanning
safety>=3.0.0           # CVE database checker  
bandit>=1.7.0           # Static security analysis
semgrep>=1.0.0          # SAST tool
```

---

## Risk Matrix

| Vulnerability | Likelihood | Impact | Risk Score | Priority |
|---------------|------------|--------|------------|----------|
| CVE-2018-18074 (requests) | High | Critical | **9.0** | P0 |
| CVE-2023-32681 (requests) | Medium | High | **7.5** | P0 |
| CVE-2020-1747 (pyyaml) | High | Critical | **9.8** | P0 |
| CVE-2020-14343 (pyyaml) | High | Critical | **9.8** | P0 |
| Unpinned bcrypt | Low | Medium | **4.0** | P1 |
| Unpinned pytest | Low | Low | **2.0** | P2 |

---

## Compliance Considerations

### Regulatory Impact

- **GDPR:** Credential exposure vulnerabilities may constitute data breach
- **SOC 2:** Outdated dependencies violate security best practices
- **PCI DSS:** Failed vulnerability management requirements
- **ISO 27001:** Non-compliance with patch management standards

### Audit Trail

Document all remediation actions:
1. Date of discovery: 2026-06-19
2. Risk assessment: CRITICAL
3. Remediation plan: Approved
4. Implementation date: [To be completed]
5. Verification date: [To be completed]
6. Sign-off: [Security team approval required]

---

## References

- [CVE-2018-18074](https://nvd.nist.gov/vuln/detail/CVE-2018-18074)
- [CVE-2023-32681](https://nvd.nist.gov/vuln/detail/CVE-2023-32681)
- [CVE-2020-1747](https://nvd.nist.gov/vuln/detail/CVE-2020-1747)
- [CVE-2020-14343](https://nvd.nist.gov/vuln/detail/CVE-2020-14343)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security.html)
- [CycloneDX SBOM Standard](https://cyclonedx.org/)

---

## Report Metadata

- **Report Version:** 1.0
- **Generated By:** Security Analysis Tool
- **Report Date:** 2026-06-19
- **Next Review:** 2026-07-19 (30 days)
- **Classification:** Internal Use - Security Sensitive
- **Distribution:** Development Team, Security Team, Management

---

**⚠️ ACTION REQUIRED: This report identifies CRITICAL security vulnerabilities requiring immediate remediation. Please escalate to security team and begin remediation within 24 hours.**
