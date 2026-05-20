# Lab 05 — RPI Workflow: GitHub MCP, HVE & Coding Agent

**Duration:** ~1 hour  
**SDLC Phase:** Plan → Implement  
**Autonomy Level:** 🔴 Agent acts autonomously, human reviews & approves  
**Prerequisites:** Lab 04 completed, VS Code with GitHub Copilot, [HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) or [HVE Core All](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core-all) extension

---

## Learning Objective

Experience the full **RPI (Research → Plan → Implement)** workflow powered by agents that are connected to real tools — the GitHub MCP server, HVE experiences, and the Coding Agent. By the end you will have directed an autonomous agent to research a live GitHub repo, plan work against it, and implement changes — all without leaving VS Code.

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Demo — octocat-supply-copilot-demo | 15 min | GitHub MCP + Chat agents |
| **2** | Connect agents to GitHub MCP server | 10 min | MCP tool configuration |
| **3** | HVE collection walkthrough | 15 min | HVE Core agent experiences |
| **4** | Coding Agent end-to-end | 20 min | Coding Agent (autonomous) |

---

## The Exercise Repository

All exercises in this lab use the **octocat-supply-copilot-demo** as your working codebase:

> **https://github.com/colindembovsky/octocat-supply-copilot-demo**

This is a realistic supply-chain application that demonstrates GitHub Copilot features across the full development lifecycle. You will **fork it** so the Coding Agent can open PRs against your own copy.

---

## Setup

### 1 — Add an MCP server (choose one)

This lab requires an MCP server to connect agents to your source control platform. Pick the option that matches your environment:

#### Option A — GitHub MCP server

In VS Code open your user or workspace `settings.json` and add:

```jsonc
{
  "mcp": {
    "servers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_TOKEN}"
        }
      }
    }
  }
}
```

Verify the `GITHUB_TOKEN` environment variable is set (it is pre-configured in this dev container). Restart the MCP server via the **MCP: Restart Server** command palette entry, then confirm the `github` server shows a green dot in the MCP panel.

#### Option B — Azure DevOps MCP server

If your team works in Azure DevOps, configure the ADO MCP server instead:

```jsonc
{
  "mcp": {
    "servers": {
      "azure-devops": {
        "command": "npx",
        "args": ["-y", "@nicepkg/azure-devops-mcp"],
        "env": {
          "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/your-org",
          "AZURE_DEVOPS_PAT": "${env:AZURE_DEVOPS_PAT}"
        }
      }
    }
  }
}
```

Set the `AZURE_DEVOPS_PAT` environment variable with a Personal Access Token that has **Work Items (Read & Write)**, **Code (Read & Write)**, and **Build (Read)** scopes. Restart the MCP server and confirm `azure-devops` shows a green dot.

> **Note:** When using Azure DevOps, substitute "issues" with "work items" and "PRs" with "pull requests in Azure Repos" throughout the exercises. The HVE Core extension ships with dedicated ADO agents that activate automatically when ADO MCP tools are available.

### 2 — Fork & clone the exercise repo

#### GitHub path

```bash
# Fork via GitHub CLI then clone your fork
gh repo fork colindembovsky/octocat-supply-copilot-demo --clone --remote
cd octocat-supply-copilot-demo
```

#### Azure DevOps path

```bash
# Clone your team's ADO repo
git clone https://dev.azure.com/your-org/your-project/_git/your-repo
cd your-repo
```

Open the cloned folder in VS Code (`code .`). This is the codebase you will research, modify, and raise PRs against for the rest of the lab.

### 3 — Install HVE Core


Open the Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`), search for **HVE Core All** (publisher: `ise-hve-essentials`), and install it. Once installed, you should see HVE agents available in the Chat agent picker.

![alt text](image.png)
---

## Part 1 — Demo: octocat-supply-copilot-demo (15 min)

Walk through the key Copilot features demonstrated in the reference repo. The goal is to understand *how* the demo is structured so you can apply the same patterns in your own projects.

### Your tasks

1. **Feature inventory.** Ask Chat:
   ```
   Using MCP, read the docs/ folder in colindembovsky/octocat-supply-copilot-demo.
   Create a table of every Copilot feature the demo showcases, what part of
   the codebase demonstrates it, and which SDLC phase it belongs to.
   ```

2. **Pick an open issue to work on.** Ask Chat:
   ```
   Using MCP, list the open issues in my fork of octocat-supply-copilot-demo.
   Recommend the best one to tackle as a first contribution — something
   self-contained, clearly scoped, and representative of the codebase.
   ```
   Note the issue number. You will use it in Parts 3 and 4.

3. **Compare agent outputs.** Run the same prompt twice — once with the GitHub MCP server active, once without (disable it temporarily in settings). Compare the depth and accuracy of the two responses.

   > **Discussion:** When does grounding with MCP tools matter most?

### Takeaway
You now have a real issue scoped and a research summary in hand. The rest of the lab drives this issue all the way to a merged PR.

---

## Part 2 — Connect Agents to the GitHub MCP Server (10 min)

The GitHub MCP server exposes tools like `search_repositories`, `get_file_contents`, `list_issues`, `create_issue`, and `create_pull_request` directly to Chat agents. This is what makes agents **grounded** in your actual GitHub context instead of relying solely on model knowledge.

### Your tasks

1. **Verify tool availability.** In Copilot Chat, type:
   ```
   What GitHub tools do you have access to right now?
   ```
   You should see a list of MCP-provided tools (search, issues, PRs, code, etc.).

2. **Explore the repo structure.** Ask:
   ```
   Using the GitHub MCP tools, fetch the README and list the top-level
   directories of my fork of octocat-supply-copilot-demo.
   Summarise what the application does and its tech stack.
   ```
   The agent will call `get_file_contents` and `list_directory` live — watch the tool call annotations in Chat.

3. **Fetch the issue you chose in Part 1.** Ask:
   ```
   Fetch issue #<number> from my fork of octocat-supply-copilot-demo.
   Identify every file likely involved in the fix and explain why.
   ```

4. **Read the relevant source files.** Ask:
   ```
   Fetch the files you identified and summarise the current implementation.
   What is missing or broken relative to the issue description?
   ```

### Takeaway
When an agent has MCP tools, it can **act on real data** rather than hallucinating structure. The GitHub MCP server turns Chat into a live interface to your repositories.

---

## Part 3 — HVE Collection (15 min)

**Hypervelocity Engineering (HVE) Core** ([github.com/microsoft/hve-core](https://github.com/microsoft/hve-core)) is Microsoft's open-source prompt library for GitHub Copilot. It ships 49 specialised agents, 102 auto-applied coding instructions, 63 reusable prompts, and 11 skills — all tuned for convention-driven, RPI-style engineering workflows. Once installed, agents activate automatically in Copilot Chat; there is no extra configuration.

### Install

Two extensions are available — pick one:

| Extension | Artifacts | Best for |
|-----------|-----------|----------|
| [HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) | 41 (flagship RPI collection) | Getting started with RPI workflows |
| [HVE Core All](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core-all) | 221 (all domains) | Full library access |

**VS Code:**
1. Open the Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`).
2. Search **HVE Core** (publisher: `ise-hve-essentials`) and click **Install**.


**GitHub Copilot CLI (alternative):**
```bash
copilot plugin marketplace add microsoft/hve-core
copilot plugin install hve-core@hve-core
```

> Full documentation: **<https://microsoft.github.io/hve-core/>**

### Key agents used in this lab

| Agent | RPI phase | What it does |
|-------|-----------|--------------|
| `task-researcher` | Research | Deep-reads a task or codebase area; produces a structured research report before any code is written |
| `rpi-agent` | R → P → I | Drives the full Research → Plan → Implement cycle; pauses for human approval between phases |
| `pr-reviewer` | Review | Fetches a PR diff and produces a structured review covering correctness, security, test coverage, and style |
| `memory` | All | Persists agent findings across sessions so context is not lost between conversations |

See the full [Agents Reference](https://github.com/microsoft/hve-core/blob/main/.github/CUSTOM-AGENTS.md) for all 49 agents.

### Copilot CLI `/research` for RPI tasks

The **GitHub Copilot CLI** includes a built-in [`/research` slash command](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/research) purpose-built for the Research phase of RPI workflows. Unlike normal chat (optimized for quick answers), `/research` activates a specialized agent that searches your codebase, organization repos, and the web to produce a comprehensive Markdown report with citations.

**Usage:**
```bash
copilot
/research How is the inventory service implemented in this repo?
```
You should see something like this:

![alt text](image-1.png)

**Why it matters for RPI:**
- **Depth over speed** — produces exhaustive reports (hundreds of lines) with architecture diagrams, code snippets, and citations.
- **Works across repositories** — searches your org's private repos, public repos, and the web; not limited to local files.
- **Permanent artifacts** — reports are saved as Markdown files you can share via `/share gist research` or `/share file research`.
- **Autonomous operation** — the agent never interrupts with clarifying questions; it documents assumptions in a "Confidence Assessment" section.

> **Tip:** Use `/research` before starting the Plan phase to gather context the agent can reference. Save the output as a gist or file to seed your planning session.

### Your tasks

1. **Research the issue with `rpi-agent`.** In Chat with the GitHub MCP server active:
   ```
   Issue #<number> in my fork of octocat-supply-copilot-demo.
   Fetch the issue and all relevant source files via MCP.
   Research the problem thoroughly, produce a detailed implementation plan,
   then implement the fix.
   ```
   Watch the three phases: **Research** (agent fetches files) → **Plan** (agent proposes steps, pauses for approval) → **Implement** (agent writes code).

2. **Review the plan before implementation.** After the Research phase the agent will present a plan. Check it covers:
   - The correct files identified
   - Edge cases mentioned in the issue
   - Tests that need updating or adding
   
   Approve the plan to let the agent proceed, or ask it to revise specific steps.

3. **Capture the research as a prompt file.**
   After the run, ask:
   ```
   Save the research findings as a reusable prompt file at
   .github/copilot/prompts/issue-<number>-research.prompt.md
   ```
   This preserves the context for future reviewers or follow-up work.

### Takeaway
HVE agents enforce a **research-first discipline**. They read before they write, plan before they implement. This dramatically reduces hallucination and increases the quality of agent-generated changes.

---

## Part 4 — Coding Agent End-to-End (20 min)

The **Coding Agent** is the highest-autonomy mode: given a GitHub Issue, it autonomously reads the codebase, plans changes, implements them, runs tests, and opens a PR — all without step-by-step human guidance.

### Your tasks

1. **Create a new issue in your fork.** Using the GitHub MCP tools from Chat:
   ```
   Create a GitHub issue in my fork of octocat-supply-copilot-demo.
   Title: "Add low-stock alert when inventory falls below reorder threshold"
   Body: When a product's quantity drops below its reorder_threshold,
   the system should emit a low-stock alert event. Add the logic and
   a unit test covering the threshold boundary.
   ```
   Note the issue number returned.

2. **Assign the issue to the Coding Agent.**
   - Open the issue on GitHub.com (or via the GitHub Pull Requests extension).
   - Assign it to **@github-copilot**.
   - Alternatively, in Chat:
     ```
     Assign issue #<number> in my fork to github-copilot using the MCP tools.
     ```

3. **Watch the agent work.** The Coding Agent will:
   - Read the relevant source files and tests in the forked repo
   - Implement the low-stock alert logic
   - Write or update tests
   - Open a draft PR linked to the issue - Open and check what is being planned and completed.
   Should take around 5 minutes to run

4. **Review and approve.** When the PR appears:
   - Use `Pr Reviewer` Agent to review it
   - Request any changes via PR comments — the Coding Agent will respond and push updates
   - Approve and merge when satisfied

5. **Reflect.** Ask Chat:
   ```
   What did the Coding Agent do well? What would a human developer
   have done differently? Where would you add a human checkpoint
   in this workflow for production use?
   ```

### Takeaway
The Coding Agent collapses the Research → Plan → Implement loop into a **single intent statement** (the issue). Your role shifts from implementer to reviewer and approver — this is the RPI workflow at its highest autonomy level.

---

## Lab Complete!

- ✅ Forked the octocat-supply-copilot-demo as your working codebase
- ✅ Configured and verified the GitHub MCP server connection
- ✅ Used MCP tools to ground agents in live repository data
- ✅ Drove a real issue end-to-end with the HVE `rpi-agent` (Research → Plan → Implement)
- ✅ Ran the Coding Agent autonomously: issue → implementation → PR → review
---

## Reference

- [GitHub MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [HVE Core extension](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core)
- [Copilot CLI `/research` command](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/research)
- [octocat-supply-copilot-demo](https://github.com/colindembovsky/octocat-supply-copilot-demo)
- [GitHub Copilot Coding Agent docs](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent)
