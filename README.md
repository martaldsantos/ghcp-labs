<img width="4400" height="657" alt="Designer (5)" src="https://github.com/user-attachments/assets/a51d37d9-4a4a-4fd4-ac30-547a2d23f278" />

# GitHub Copilot Advanced Labs

A hands-on workshop series for mastering GitHub Copilot across real-world development scenarios. Each lab is approximately **1 hour** and builds on practical, project-based exercises.

---

## Objectives

By the end of this course, participants will be able to:

- Write comprehensive unit tests using GitHub Copilot Chat, inline suggestions, and Agent Mode
- Use Copilot to debug, troubleshoot, and document existing codebases
- Perform code refactoring and language/framework migrations with Copilot assistance
- Leverage knowledge bases and indexed repositories for context-aware suggestions
- Build and extend agents with GitHub Copilot
- Use Agent Mode for autonomous, multi-step coding tasks
- Apply Copilot to code security analysis, vulnerability detection, and more

---

## Labs

| # | Lab | Duration | Folder |
|---|-----|----------|--------|
| 02 | [Unit Testing](lab1/) | ~1 hour | `lab1/` |
| 03 | [Debugging, Troubleshooting & Documentation](lab2/) | ~1 hour | `lab2/` |
| 04 | [Refactoring & Migration](lab3/) | ~1 hour | `lab3/` |
| 05 | [Knowledge Bases & Indexed Repos](lab4/) | ~1 hour | `lab4/` |
| 06 | [Agents](lab5/) | ~1 hour | `lab5/` |
| 07 | [Agent Mode](lab6/) | ~1 hour | `lab6/` |
| 08 | [Code Security and More](lab7/) | ~1 hour | `lab7/` |

---

## Prerequisites

- **GitHub Copilot** license (Individual, Business, or Enterprise)
- **VS Code** with the GitHub Copilot and GitHub Copilot Chat extensions
- **Python 3.10+** (Labs 02–04)
- **GitHub CLI** (`gh`) with the Copilot extension — `gh extension install github/gh-copilot`
- Basic familiarity with Git and GitHub

---

## Getting Started

```bash
git clone https://github.com/martaldsantos/ghcp-labs.git
cd ghcp-labs
```

Then navigate to the lab folder and follow its README:

```bash
cd lab1
pip install -r requirements.txt
```

---

## Course Structure

Each lab follows a consistent format:

1. **Scaffolded project** — realistic production code is provided
2. **Starter skeletons** — partially completed files with TODOs for participants
3. **Step-by-step instructions** — timed parts with clear objectives
4. **Hints** — expandable hints for when participants get stuck
5. **Solutions** — complete reference implementations in a `solutions/` folder
