## Skyline DevSecOps Pipeline

This repository now includes a GitHub-native DevSecOps baseline that scans, blocks, tests, and reports before code is merged or deployed.

### Included controls

- `CI Test Gate` runs repository tests on pull requests and protected-branch pushes.
- `Secrets Scan` blocks commits that introduce leaked credentials.
- `SCA - Dependency Review` blocks pull requests that add vulnerable dependencies.
- `SAST - CodeQL` analyzes source code and GitHub Actions for security issues.
- `Config Scan` scans infrastructure and workflow configuration with Trivy.
- `Deploy - Staging` re-runs gates before any staging deployment command is executed.
- `DAST - ZAP Baseline` can scan the deployed staging URL after deployment.
- `Notify Security` comments on failing PRs and opens tracking issues for non-PR failures.

### Repository settings to enable

To fully enforce merge blocking in GitHub, enable branch protection or a ruleset on `main` and require these status checks:

- `CI Test Gate`
- `Secrets Scan`
- `SCA - Dependency Review`
- `SAST - CodeQL`
- `Config Scan`

To fully enforce deployment guarding in GitHub, create a `staging` environment and optionally add required reviewers.

### Repository variables to configure

- `CI_TEST_COMMAND` — optional override for custom test execution.
- `DEPLOY_STAGING_COMMAND` — required to activate the staging deployment step.
- `STAGING_URL` — required to activate post-deploy DAST with ZAP.

### Security reporting surfaces

- GitHub Actions checks block pull requests and deployments.
- Code scanning results are uploaded from CodeQL and Trivy when supported.
- Dependency review annotates pull requests.
- Security failures are summarized back to PRs or tracking issues.
