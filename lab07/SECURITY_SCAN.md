---
title: "Lab 07 Security Scan Report"
description: "Security analysis of lab07 requirements with CVE findings and remediation steps"
author: "GitHub Copilot"
ms.date: 2026-06-19
ms.topic: "reference"
---

## Summary

Scanned file: `lab07/requirements.txt`

Total direct dependencies scanned: 4

Potential issues identified: 6

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 5 |
| LOW | 0 |

## Findings

| Package name | Current version | Known CVE ID | Severity | Recommended action |
|--------------|-----------------|--------------|----------|--------------------|
| requests | 2.18.0 | CVE-2018-18074 | HIGH | Upgrade to `requests>=2.32.0` immediately. This CVE is fixed in versions after `2.20.0`. |
| requests | 2.18.0 | CVE-2023-32681 | MEDIUM | Upgrade to `requests>=2.31.0` (covered by `>=2.32.0`). Avoid exposing proxy credentials through redirects. |
| requests | 2.18.0 | CVE-2024-35195 | MEDIUM | Upgrade to `requests>=2.32.0` to address TLS verification persistence issues in Session reuse. |
| pytest | unpinned | N/A | MEDIUM | Pin to a tested minimum and cap major version drift, for example `pytest>=8.2,<9.0`, then update regularly. |
| bcrypt | unpinned | N/A | MEDIUM | Pin to a tested version range, for example `bcrypt>=4.1,<5.0`, and monitor advisories. |
| pyyaml | unpinned | N/A | MEDIUM | Pin to a secure maintained release, for example `pyyaml>=6.0.1,<7.0`, and use `safe_load` in application code. |

Notes:

* CVE severities above are based on advisory/NVD metadata for affected `requests` version ranges.
* Unpinned dependencies are treated as a supply-chain and reproducibility risk even when no specific CVE is currently mapped.

## Remediation Plan

1. Update `requests` first.

   * Change `requests==2.18.0` to `requests>=2.32.0,<3.0`.
   * Reinstall dependencies and run the full test suite.

2. Pin remaining dependencies to controlled ranges.

   * Define explicit version ranges for `pytest`, `bcrypt`, and `pyyaml`.
   * Commit the updated `requirements.txt` after test validation.

3. Add recurring dependency scanning.

   * Run a scanner in CI for every pull request.
   * Fail builds on HIGH and CRITICAL vulnerabilities.

4. Establish update cadence.

   * Review dependencies monthly.
   * Apply patch/minor upgrades promptly and re-run tests.
