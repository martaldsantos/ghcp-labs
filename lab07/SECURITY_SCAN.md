# SECURITY_SCAN.md

## Summary
- Total dependencies scanned: 4
- Confirmed CVE findings: 1
- Conditional CVE findings (depends on resolved version): 1
- Counts by severity: CRITICAL 0, HIGH 1, MEDIUM 1, LOW 0

## Findings
| Package | Current Version | Known CVE ID | Severity | Recommended Action |
|---|---|---|---|---|
| requests | 2.18.0 | CVE-2018-18074 | MEDIUM | Upgrade to a modern supported version (recommended: `requests>=2.32.0`) and re-run security scan. |
| pyyaml | Unpinned (version not specified) | CVE-2020-14343 (if resolved to vulnerable versions such as <=5.3.1) | HIGH | Pin to a safe version (recommended: `pyyaml>=6.0.1`), avoid unsafe `yaml.load` usage, and verify with lockfile-based scanning. |

## Remediation Plan
1. Pin all dependencies to explicit minimum-safe versions in `requirements.txt`.
2. Immediately upgrade `requests` from `2.18.0` to a currently supported release.
3. Pin `pyyaml` to `>=6.0.1` to prevent drift to vulnerable releases.
4. Add automated scanning (`pip-audit` or Dependabot) in CI and fail builds on HIGH/CRITICAL findings.
5. Regenerate `sbom.xml` after upgrades and attach the updated report to the PR.
