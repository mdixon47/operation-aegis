## GitHub ruleset and branch protection checklist

Use this checklist to align repository protection with the workflows in `.github/workflows/`.

### Protect the default branch

- Apply the ruleset to `main`
- Require a pull request before merge
- Require at least 1 approval; prefer 2 for workflow or deployment changes
- Dismiss stale approvals when new commits are pushed
- Require all review conversations to be resolved
- Block force pushes and branch deletion
- Restrict direct pushes and bypass permissions to repository administrators/security leads only

### Require these status checks

Mark these checks as required for `main`:

- `CI Test Gate`
- `Secrets Scan`
- `SCA - Dependency Review`
- `SAST - CodeQL`
- `Config Scan`

If you later make staging deploys mandatory before promotion, also require the deployment workflow or a release workflow that wraps it.

### Protect the staging environment

- Create a GitHub environment named `staging`
- Add required reviewers for production-sensitive repos
- Set `STAGING_URL` so the deployment and DAST workflows can report a real target URL
- Keep environment secrets scoped to `staging`
- Restrict deployment branches to `main` and approved release branches

### Repository configuration

- Keep `CI_TEST_COMMAND` unset unless the default test detection is insufficient
- Leave `DEPLOY_STAGING_COMMAND` unset to use the repository scaffold, or set it to your real deploy command
- Enable Dependabot updates for both GitHub Actions and Docker base images

### Operational hygiene

- Review alerts from `Notify Security` promptly
- Rehearse the blocked-PR demo drills on throwaway branches only
- Treat changes to workflows, Dockerfiles, and deployment scripts as high-risk and require peer review
- If you use the `Release Bundle` workflow, limit who can create release tags and review published release assets
