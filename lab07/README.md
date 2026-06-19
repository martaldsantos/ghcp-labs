# Lab 07 - Copilot for Deployment

**Duration:** ~90 min  
**SDLC Phase:** Integration → Deployment → Release  
**Autonomy Level:** 🟡 Human reviews, Copilot automates  
**Prerequisites:** Git + a remote repository (GitHub), VS Code with GitHub Copilot
**Works with:** GitHub Issues

---

Lab 07 is self-contained. **Copilot is your pair programmer throughout**: it generates the Bicep or Terraform that provisions your infrastructure, scaffolds the CI/CD pipeline YAML that enforces SBOM and CVE gates, and helps reason about cost before any resource is created. The lab covers the full path from a local commit to a pipeline-gated, infrastructure-validated, Copilot-assisted deployment.

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Branch setup | 5 min | Copilot PR scaffold |
| **2** | Supply chain security (hands-on) | 12 min | SBOM generation + vulnerability scanning |
| **3** | Docker Compose — containerised deployment | 15 min | Copilot chat + inline YAML |
| **4** | CI/CD pipeline as code | 20 min | GitHub Actions YAML authoring |
| **5** | IaC + GitOps | 25 min | MCP tools + community skills (`azure-deployment-preflight`, `import-infrastructure-as-code`) |
| **6** | Open PR, validate & deploy | 10 min | Chat verification + deployment |

---

## Setup

```bash
cd lab07
pip install -r requirements.txt
```

---

## The Scenario

You're an engineer taking a feature from a local commit to a production-ready deployment. **Copilot is your pair programmer for every artifact**: it generates the IaC that provisions resources, scaffolds the pipeline YAML that enforces security gates, and helps you reason about cost before any resource is created.

Your path through the lab:
1. **Create a feature branch** — your unit of deployable change
2. **Scan the supply chain** — generate an SBOM and surface CVEs before the pipeline does
3. **Containerise the service** — Docker Compose with Copilot-generated YAML
4. **Author the CI/CD pipeline** — build → scan → validate-iac → copilot-review + manual-approval → deploy stages
5. **Provision infrastructure** — Bicep or Terraform generated and validated with Copilot + MCP
6. **Open the PR and ship** — real artifacts, enforced gates, Copilot-assisted review

---

## Part 1 — Branch Setup (5 min)

Create your working branch now. The PR opens in Part 6, once real artifacts exist — not on an empty commit.

### Your tasks

1. **Create and track your feature branch:**
   ```bash
   git checkout -b lab07/pr-workflow
   git push -u origin lab07/pr-workflow
   ```

2. **Ask Copilot to draft your PR description** (you’ll paste it when opening the PR in Part 6):
   ```
   Chat prompt: “Draft a GitHub PR description for a lab07 deployment branch.
   Include sections: Description, Changes (SBOM, pipeline YAML, IaC),
   Supply Chain Security checklist.
   Use markdown. Keep it under 30 lines.”
   ```
   Save the draft — you’ll fill in real findings as you work through the lab.

---

## Part 2 — Supply Chain Security: SBOM & Vulnerability Scanning (12 min)

Modern DevOps requires supply chain security awareness. You'll generate a bill-of-materials (SBOM) and scan for vulnerabilities — practices that are now standard in enterprise pipelines.

### What is an SBOM?

A Software Bill of Materials (SBOM) is a machine-readable inventory of all dependencies in your software. It:
- Lists every dependency and its version
- Enables vulnerability tracking across your supply chain
- Supports compliance audits and security policies
- Integrates with automated scanning tools

### Your tasks

#### Task 1: Generate SBOM from dependencies (5 min)

1. **Create a SBOM file from local dependencies:**
   ```bash
   # Navigate to your lab directory
   cd lab07
   
   # Install the CycloneDX SBOM generator
   python -m pip install cyclonedx-bom
   
   # Generate a CycloneDX SBOM from requirements.txt
   python -m cyclonedx_py requirements -i requirements.txt 2>/dev/null > sbom.xml
   cat sbom.xml
   ```

2. **Use Copilot to summarize:**
   ```
   Chat prompt: "Create a markdown summary of this CycloneDX SBOM showing:
   - Total number of dependencies
   - High-level dependency categories (web framework, database, testing, etc.)
   - Any dependencies that appear outdated
   
   Format as a table with columns: Package, Version, Category"
   ```

3. **Commit your SBOM:**
   ```bash
   git add sbom.xml
   git commit -m "lab07: Add CycloneDX SBOM"
   ```

#### Task 2: Vulnerability scanning (7 min)

1. **Scan for vulnerabilities and document findings:**
   ```
   Chat prompt: "Analyze this requirements.txt for known CVEs and security issues:
   
   [paste contents of sbom.xml or requirements.txt]
   
   For each potential issue, provide:
   - Package name
   - Current version
   - Known CVE ID
   - Severity (LOW, MEDIUM, HIGH, CRITICAL)
   - Recommended action
   
   Then generate a SECURITY_SCAN.md report with sections: Summary (total scanned,
   counts by severity), Findings (your analysis above), and Remediation Plan."
   ```

   Save the generated report as `SECURITY_SCAN.md` in the `lab07/` directory.

2. **Commit the security report:**
   ```bash
   git add SECURITY_SCAN.md
   git commit -m "lab07: Add security vulnerability scan report"
   ```

### Dependency Update Policy

Document this in your PR description:

```markdown
## Dependency & Supply Chain Policy

- **SBOM requirement**: All releases must include an updated SBOM
- **Vulnerability scanning**: Mandatory before PR merge
- **Severity thresholds**: 
  - CRITICAL: Block merge immediately, remediate before release
  - HIGH: Address within 72 hours
  - MEDIUM: Address within 2 weeks
  - LOW: Track and batch with regular updates
- **Update cadence**: Dependencies reviewed and updated monthly
- **Approval**: Security team reviews scan reports before merge
```

### Key Insight

Supply chain security is not optional. SBOM generation and vulnerability scanning are standard practices in enterprise DevOps.

> **GitHub Advanced Security does this for you.** If your repository is on GitHub, [GitHub Advanced Security (GHAS)](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) automates the entire vulnerability workflow: Dependabot continuously monitors your dependencies against the GitHub Advisory Database and opens PRs to remediate vulnerable packages; secret scanning prevents credentials from ever being committed; and code scanning (powered by CodeQL) detects security weaknesses in your own source code. Rather than running ad-hoc scans locally, GHAS integrates these checks directly into your pull request flow — blocking merges until findings are resolved — so supply chain security becomes a policy, not a manual step.

---

## Part 3 — Docker Compose: Containerised Deployment (15 min)

Docker Compose defines your entire service topology as YAML — the same format as CI/CD pipeline jobs (Part 4) and IaC modules (Part 5). Copilot generates the file; your job is to validate, understand, and commit it.

### Instructions Installation (1 min)

Before generating any YAML, let's use the community Copilot skills that give Copilot deep knowledge of Docker and container best practices. You should see several skills on the lab07/skills folder. 

1. **Verify Copilot can see the instructions:**
   Open Copilot Chat and type:
   ```
   What Docker and containerization best practices do you have available?
   ```
   Copilot should reference the installed instructions. This is a great file to adapt and use it according to your Company's own best practices and needs. 

### Your tasks

1. **Use Copilot to build a multi-service composition** into `docker-compose.yml`:
   - Chat prompt:
     ```
     Create a docker-compose.yml file that:
     - Defines a Python service running the reminder engine
     - Includes a PostgreSQL database service
     - Sets up environment variables for database connection
     - Configures volume mounts for data persistence
     - Defines a custom bridge network for service-to-service communication
     - Includes health checks for both services
     - Contains comments explaining each section
     
     Make it production-ready with proper error handling.
     ```

2. **Your docker-compose.yml will include:**
   ```yaml
   services:
     reminder-engine:
       # Python service running the reminder engine
     postgres:
       # Database service
     # networks, volumes, health checks defined below
   ```

3. **Validate the Docker Compose file:**
   ```bash
   # Check syntax (requires Docker)
   docker compose config
   ```
   Or ask Copilot using the installed instructions:
   ```
   Review this docker-compose.yml for syntax errors and best practices.
   ```

4. **Commit and push:**
   ```bash
   git add docker-compose.yml
   git commit -m "lab07: Add Docker Compose for containerized deployment"
   git push origin lab07/pr-workflow
   ```

### Key Insight

Docker Compose gives you a reproducible, infrastructure-parity environment in a single YAML file. The same patterns — named services, environment variables, health checks — appear in Kubernetes manifests and cloud container services.

---

## Part 4 — CI/CD Pipeline as Code (20 min)

A markdown checklist is a reminder. A required status check is a **contract**. This part closes that gap: you'll author the pipeline YAML so that SBOM generation, CVE scanning, and IaC validation are enforced job gates — not aspirational bullet points.

### Pipeline structure

```
build → scan → validate-iac → (copilot-review + manual-approval) → deploy
```

Each job depends on the previous one (`needs:`). A CVE above the threshold fails `scan`, which prevents `validate-iac` from starting, which prevents the approval gate from appearing. Evidence artifacts are uploaded with `if: failure()` so reviewers can inspect findings in the run.

---

### Your tasks

#### Task 1: Author the pipeline YAML (10 min)

**GitHub Actions track:**

1. Create the workflow file:
   ```bash
   mkdir -p .github/workflows
   touch .github/workflows/lab07-pipeline.yml
   ```

2. Use Copilot to scaffold it:
   ```
   Chat prompt: "Create a GitHub Actions workflow named 'Lab07 Supply-Chain CI/CD'
   triggered on push to lab07/pr-workflow and pull_request to main.

   Define these jobs in sequence using 'needs:':

   build:
     - checkout, setup Python 3.11
     - install lab07/requirements.txt
     - generate a CycloneDX SBOM: pip install cyclonedx-bom && python -m cyclonedx_py requirements -i lab07/requirements.txt > lab07/sbom.xml
     - upload sbom.xml as artifact 'sbom'

   scan:
     - download artifact 'sbom'
     - run pip-audit: pip install pip-audit && pip-audit -r lab07/requirements.txt --format=json -o lab07/cve-report.json
     - upload cve-report.json as artifact 'cve-report' using 'if: failure()'
     - add a step with 'if: failure()' that prints ::error:: and exits 1 to surface failures clearly

   validate-iac:
     - if hashFiles('lab07/main.bicep') != '', run: az bicep install && az bicep build --file lab07/main.bicep
     - if hashFiles('lab07/main.tf') != '', run: cd lab07 && terraform init -backend=false && terraform validate
     - add a step with 'if: failure()' that prints ::error:: IaC validation failed

   manual-approval:
     - runs-on: ubuntu-latest, environment: production  (requires required-reviewers in Settings)
     - single step: echo 'All gates passed. Pending approval.'

   deploy:
     - dry-run only: echo 'Would run: az deployment group create --what-if / terraform plan'
     - no real deployment"
   ```

3. Review the generated file against this reference structure:
   ```yaml
   name: Lab07 Supply-Chain CI/CD

   on:
     push:
       branches: [lab07/pr-workflow]
     pull_request:
       branches: [main]

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'
         - run: pip install -r lab07/requirements.txt
         - name: Generate SBOM (CycloneDX)
           run: |
             pip install cyclonedx-bom
             python -m cyclonedx_py requirements \
               -i lab07/requirements.txt > lab07/sbom.xml
         - uses: actions/upload-artifact@v4
           with: { name: sbom, path: lab07/sbom.xml }

     scan:
       runs-on: ubuntu-latest
       needs: build
       steps:
         - uses: actions/checkout@v4
         - uses: actions/download-artifact@v4
           with: { name: sbom, path: lab07/ }
         - name: CVE scan
           run: |
             pip install pip-audit
             pip-audit -r lab07/requirements.txt \
               --format=json -o lab07/cve-report.json
         - name: Upload CVE report on failure
           if: failure()
           uses: actions/upload-artifact@v4
           with: { name: cve-report, path: lab07/cve-report.json }
         - name: Surface CVE failures
           if: failure()
           run: |
             echo "::error::CVE scan failed. Download the cve-report artifact for details."
             exit 1

     validate-iac:
       runs-on: ubuntu-latest
       needs: scan
       steps:
         - uses: actions/checkout@v4
         - name: Validate Bicep
           if: hashFiles('lab07/main.bicep') != ''
           run: az bicep install && az bicep build --file lab07/main.bicep
         - name: Validate Terraform
           if: hashFiles('lab07/main.tf') != ''
           run: |
             cd lab07
             terraform init -backend=false && terraform validate
         - name: Surface IaC errors
           if: failure()
           run: echo "::error::IaC validation failed — fix before requesting approval."

     manual-approval:
       runs-on: ubuntu-latest
       needs: validate-iac
       environment: production   # configure Required reviewers in Settings → Environments
       steps:
         - run: echo "All gates passed. Awaiting reviewer approval."

     deploy:
       runs-on: ubuntu-latest
       needs: manual-approval
       steps:
         - uses: actions/checkout@v4
         - name: Dry-run deploy (no real resources)
           run: |
             echo "Would run: az deployment group create --what-if ..."
             echo "Or: terraform plan -out=tfplan"
   ```

4. Commit the pipeline:
   ```bash
   git add .github/workflows/lab07-pipeline.yml
   git commit -m "lab07: Add CI/CD pipeline with supply-chain gates"
   git push origin lab07/pr-workflow
   ```

---

#### Task 2: Configure required status checks (5 min)

Required status checks turn optional CI runs into **merge blockers**. Without this step, the pipeline is advisory — a developer can merge even if `scan` is red.

**GitHub branch protection:**

1. Go to **Settings → Branches → Add branch protection rule** for `main`
2. Enable **"Require status checks to pass before merging"**
3. Search for and add these as required checks:
   - `scan`
   - `validate-iac`
4. Enable **"Require branches to be up to date before merging"**

   > Copilot prompt: `"What branch protection settings enforce supply-chain security gates on a Python repo? Include status checks and signed commits."`

**GitHub Environment for manual approval:**

1. Go to **Settings → Environments → New environment** → name it `production`
2. Add **Required reviewers** (yourself or a teammate)
3. The `manual-approval` job will pause at this gate until a reviewer approves in the Actions UI

**Code reviewer on the PR:**

1. On the PR page, go to **Reviewers** → add **Copilot** as a code reviewer
2. Copilot will post a structured code-quality review directly on the PR, separate from the pipeline approval gate
3. Resolve Copilot's review comments before the `manual-approval` gate is triggered

---

#### Task 3: Verify gate behavior (5 min)

1. **Break the CVE scan intentionally:**
   ```bash
   # Add a package with known CVEs to requirements.txt
   echo "requests==2.18.0" >> lab07/requirements.txt
   git add lab07/requirements.txt
   git commit -m "lab07: TEST — introduce CVE to verify gate"
   git push origin lab07/pr-workflow
   ```

2. **Observe the pipeline run:**
   - The `scan` job should fail
   - `validate-iac`, `manual-approval`, and `deploy` should never start
   - The `cve-report` artifact should be downloadable from the failed run
   - The PR merge button should be blocked (if required status checks are configured)

3. **Ask Copilot to review your pipeline:**
   ```
   Chat prompt: "Review this GitHub Actions pipeline for supply-chain security best practices:
   - Are job dependencies correctly sequenced with 'needs:'?
   - Are failure handlers using 'if: failure()' in the right places?
   - Is the manual approval gate positioned correctly in the flow?
   - What additional hardening would you recommend (pinned action SHAs,
     OIDC federation instead of long-lived secrets, artifact attestation)?"
   ```

4. **Revert the intentional CVE and push a clean commit:**
   ```bash
   # Remove the test line from requirements.txt
   git add lab07/requirements.txt
   git commit -m "lab07: Revert test CVE — restore clean requirements.txt"
   git push origin lab07/pr-workflow
   ```

### Key Insight

Embedding SBOM generation and CVE scanning as **pipeline job steps** with `if: failure()` gates and required-status-check enforcement is the difference between *documenting* supply-chain policy and *enforcing* it. Manual approval gates ensure that every deployment to production has a human sign-off — after all automated gates pass, never before.

---

## Part 5 — Infrastructure-as-Code + GitOps (25 min)

Modern infrastructure must be **versioned** and **auditable**. This section teaches IaC fundamentals alongside GitOps patterns — and uses community Copilot **skills** from [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/) to supercharge the workflow.

### Skill Installation (2 min)

Before you write a single line of IaC, install the relevant Copilot skill for your chosen track. Skills extend Copilot with domain-specific knowledge — giving it deep understanding of Bicep validation workflows or Terraform AVM module patterns.

**Step 2 — Verify Copilot can see the skill:**

Open Copilot Chat and type:
```
What skills do you have available for infrastructure deployments?
```

Copilot should describe the skill you just installed. If not, reload the VS Code window (`Ctrl+Shift+P → Developer: Reload Window`) and try again. If you can't find them or want to extend further, find your necessary skills on [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/)

> **Where these skills come from:** The skill files in `.github/skills/` are sourced directly from [github/awesome-copilot](https://github.com/github/awesome-copilot) — the community-curated library of VS Code Copilot skills. Anyone can contribute or install skills from [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/).

---

### Subsection A: Infrastructure-as-Code Fundamentals (18 min)

You have **two tracks**: Choose Bicep (Azure-native) or Terraform (multi-cloud).

#### Track A: Bicep (Azure-native) — with `azure-deployment-preflight` skill

**What is Bicep?**  
Bicep is an Azure-native DSL for Infrastructure-as-Code. It compiles to ARM templates. The `azure-deployment-preflight` skill guides Copilot through full preflight validation: syntax check → what-if analysis → permissions check → Markdown report.

##### Your tasks

1. **Create a Bicep file:**
   ```bash
   touch main.bicep
   ```

2. **Use Microsoft Learn MCP to build the Bicep template:**
   ```
   Chat prompt: "Use the Microsoft Learn MCP tool to find official Bicep examples for:
   - Creating an Azure Storage Account with encryption
   - Configuring access controls and network security
   - Adding monitoring and logging
   
   Then generate a Bicep file with these resources.
   Include metadata comments explaining the deployment pattern."
   ```

3. **Copilot will use the MCP to fetch code samples** from Microsoft Learn documentation

4. **Review the generated Bicep:**
   - Ensure it follows Azure naming conventions
   - Verify security best practices (encryption, access control)
   - Check for monitoring configuration

5. **Run preflight validation using the installed skill:**
   ```
   Chat prompt: "Run a preflight validation on lab07/main.bicep.
   Follow the azure-deployment-preflight skill:
   - Validate Bicep syntax with 'bicep build'
   - Check for what-if changes at resource group scope
   - Generate a preflight-report.md summarising all findings"
   ```

   Copilot will:
   - Run `bicep build main.bicep --stdout` to catch syntax errors
   - Execute `az deployment group what-if` (or note it locally if Azure CLI is not authenticated)
   - Write a `preflight-report.md` in your working directory

6. **Commit your Bicep file and preflight report:**
   ```bash
   git add main.bicep preflight-report.md
   git commit -m "lab07: Add Bicep IaC + preflight validation report"
   ```

#### Track B: Terraform (Multi-cloud) — with `import-infrastructure-as-code` skill

**What is Terraform?**  
Terraform is a cloud-agnostic IaC tool supporting AWS, Azure, GCP, and more. The `import-infrastructure-as-code` skill guides Copilot through Azure Verified Modules (AVM) — the Microsoft-curated, production-grade Terraform module library — and produces AVM-based configurations ready for `terraform validate`.

##### Your tasks

1. **Create Terraform files:**
   ```bash
   touch main.tf variables.tf outputs.tf
   ```

2. **Use the skill + Microsoft Learn MCP for Terraform + Azure:**
   ```
   Chat prompt: "Use the import-infrastructure-as-code skill and the Microsoft Learn MCP
   to generate a Terraform configuration using Azure Verified Modules (AVM) for:
   - Azure Resource Group with naming conventions
   - Azure Storage Account with encryption and network security
   
   Produce AVM-based Terraform files (main.tf, variables.tf, outputs.tf) with:
   - Correct required_providers block pinned to azurerm ~> 4.0
   - Comments explaining each resource and its AVM module source
   - Validation-ready output (no backend config required)"
   ```

3. **Copilot will retrieve AVM module examples** using the skill's knowledge of Azure Verified Modules

4. **Expected Terraform structure from the skill:**
   ```hcl
   # main.tf — generated with import-infrastructure-as-code skill
   terraform {
     required_providers {
       azurerm = {
         source  = "hashicorp/azurerm"
         version = "~> 4.0"
       }
     }
   }
   
   provider "azurerm" {
     features {}
   }
   
   # Azure Verified Module: Resource Group
   module "resource_group" {
     source  = "Azure/avm-res-resources-resourcegroup/azurerm"
     version = "~> 0.1"
     # ...
   }
   
   # Azure Verified Module: Storage Account
   module "storage" {
     source  = "Azure/avm-res-storage-storageaccount/azurerm"
     version = "~> 0.4"
     # ...
   }
   ```

5. **Validate using the skill's workflow:**
   ```
   Chat prompt: "Using the import-infrastructure-as-code skill,
   validate that lab07/main.tf is ready for planning:
   - Check the required_providers block
   - Verify AVM module sources are correctly referenced
   - Run: terraform init -backend=false && terraform validate"
   ```

6. **Run validation locally (no deployment):**
   ```bash
   # terraform CLI: install from https://developer.hashicorp.com/terraform/install if not present
   terraform init -backend=false
   terraform validate
   # Don't run "terraform apply" — validation only
   ```

7. **Commit your Terraform configuration:**
   ```bash
   git add main.tf variables.tf outputs.tf
   git commit -m "lab07: Add AVM-based Terraform IaC (import-infrastructure-as-code skill)"
   ```

### Key Insight

**Infrastructure-as-Code** ensures your infrastructure is versioned and reproducible. Using community **skills** from awesome-copilot gives Copilot the domain knowledge to validate correctly and follow Azure-approved module patterns — rather than generating generic code from general knowledge.  

---

## Part 6 — Open PR, Validate & Deploy (10 min)

### Your tasks

#### Task 1: Open your pull request (2 min)

You now have real artifacts to ship. Use Copilot to write the PR description from your branch diff — not from the placeholder you drafted in Part 1.

1. **Ask Copilot to write the PR description from your diff:**
   ```
   Chat prompt: “Write a PR description for the lab07/pr-workflow branch.
   Summarise: the SBOM and CVE scan findings (Part 2), the CI/CD pipeline
   structure with its security gates (Part 4), and the IaC resources defined
   (Part 5). Include the supply chain security checklist."
   ```

2. **Open the PR — pick the fastest method for your setup:**

   **Option A — GitHub CLI (fastest):**
   ```bash
   gh pr create \
     --title "lab07: Supply-chain CI/CD, Docker Compose, and IaC" \
     --body "$(cat <<'EOF'
   ## Summary
   Adds SBOM generation, CVE scanning pipeline gates, Docker Compose, and Bicep/Terraform IaC.

   ## Changes
   - SBOM (CycloneDX) and vulnerability scan report
   - GitHub Actions pipeline: build → scan → validate-iac → copilot-review + manual-approval → deploy
   - Docker Compose multi-service configuration
   - Bicep or Terraform IaC with preflight validation

   ## Supply Chain Security Checklist
   - [ ] SBOM generated and committed
   - [ ] CVE scan clean (or findings documented)
   - [ ] IaC validated locally
   - [ ] Pipeline gates configured as required status checks
   EOF
   )" \
     --base main \
     --head lab07/pr-workflow
   ```

   **Option B — Copilot Chat:**
   Type `/createPullRequest` in Copilot Chat — it drafts the title and description from your branch diff automatically.

   **Option C — GitHub web UI:**
   Repository → Pull requests → New pull request → select `lab07/pr-workflow` → base `main`.

3. **Reference tracker items:**
   - Group A (ADO work items): `AB#<ID>`
   - Group B (Jira): `PROJ-<ID>`
   - GitHub Issues: `Closes #<ID>`

#### Task 2: Validate containers (2 min)

1. **Validate your docker-compose.yml:**
   ```bash
   # Check syntax (requires Docker)
   docker compose config

   # Or ask Copilot:
   # "Validate this docker-compose.yml for syntax and best practices"
   ```

2. **Check for common issues:**
   - Indentation is 2 spaces (not tabs)
   - No trailing spaces
   - All required fields are present

#### Task 3: Validate infrastructure code (2 min)

1. **Validate using the installed skill (Bicep track):**
   ```
   Chat prompt: "Run a preflight validation on lab07/main.bicep. Generate or update preflight-report.md."
   ```
   Or run directly:
   ```bash
   bicep build main.bicep
   ```

2. **Validate using the installed skill (Terraform track):**
   ```
   Chat prompt: "Confirm lab07/main.tf is AVM-compliant and run terraform validate."
   ```
   Or run directly:
   ```bash
   terraform init -backend=false
   terraform validate
   ```

3. **Security review with Copilot:**
   ```
   Chat prompt: "Review this [Bicep/Terraform] code for security best practices:
   - Encryption at rest and in transit
   - Network isolation and access controls
   - Secrets management
   - Monitoring and logging
   
   Flag any issues and suggest fixes."
   ```

#### Task 4: Request code review on GitHub (2 min)

Code review happens in the PR on **github.com** — not in the IDE. Use Copilot's review features built into the GitHub PR UI.

1. **Open your PR on github.com:**
   - Go to your repository → **Pull requests** → open `lab07/pr-workflow`

2. **Start a Copilot code review:**
   - On the PR page, click **Reviewers** (top-right sidebar) → select **Copilot**
   - GitHub Copilot will analyse the diff and post inline review comments automatically
   - Copilot comments appear in the **Files changed** tab alongside human review comments

3. **Work through Copilot's comments:**
   - Read each inline comment in **Files changed**
   - For each suggestion: accept it, push a fix, or reply with a justification to dismiss it
   - Resolve threads as you address them — unresolved threads block merge if branch protection requires it

4. **Request Copilot as a code reviewer:**
   - In the **Reviewers** sidebar, add **Copilot** as a code reviewer — it will post a structured code-quality review as a reviewer, separate from the inline diff comments in step 2
   - If your repository defines a `CODEOWNERS` file, GitHub automatically requests the correct reviewer based on which files were changed; no manual assignment is needed
   - To set up `CODEOWNERS`:
     ```
     # .github/CODEOWNERS
     lab07/  @your-team/backend-reviewers
     .github/workflows/  @your-team/platform-engineers
     ```

5. **Use the suggested review prompts** from the checklist at the top of this lab if you want additional Copilot chat analysis inside the PR conversation tab.

#### Task 5: Merge when ready (optional)

When your PR passes all gates and a reviewer approves:

```bash
# Merge to main
git checkout main
git pull origin main
git merge lab07/pr-workflow
git push origin main

# Clean up feature branch
git branch -d lab07/pr-workflow
git push origin --delete lab07/pr-workflow
```

### Key Insight

Validation covers syntax and security before every merge.

---

## Summary

In this lab, you’ve practised **Copilot-assisted deployment**:

✅ **Supply Chain Security** — SBOM generation and CVE scanning as enforced pipeline gates  
✅ **Containerised Deployment** — Docker Compose generated and validated with Copilot  
✅ **CI/CD Pipeline Authoring** — build → scan → validate-iac → copilot-review + manual-approval → deploy in GitHub Actions or Azure Pipelines  
✅ **Policy-as-Code** — CVE and IaC failures as required status checks, not markdown checklists  
✅ **Infrastructure-as-Code** — Bicep or Terraform generated with Copilot + MCP, validated locally  
✅ **Community Copilot Skills** — `azure-deployment-preflight` (Bicep preflight + what-if) and `import-infrastructure-as-code` (AVM-based Terraform) from [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/)
✅ **GitOps Patterns** — Git as single source of truth for infrastructure state  
✅ **PR Authoring** — Copilot writes the PR description from your branch diff, not from a template  

These skills form the foundation of **Copilot-assisted DevOps** practice.
