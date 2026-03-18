## Re-triggering graceful-degradation security workflows

Use this guide when a security workflow needs a fresh pull-request evaluation in this repository, especially after changing workflow logic on `main`.

### Why this exists

Some security features used by GitHub Actions can be unavailable on private repositories without the required GitHub plan or GitHub Advanced Security features.

In this repo, these workflows are designed to degrade gracefully:

- `SAST - CodeQL`
- `SCA - Dependency Review`
- `Config Scan`

Instead of hard-failing the whole pipeline when a platform capability is missing, the workflow should detect that condition and either skip cleanly or summarize why analysis did not run.

### Safest way to retrigger on a Dependabot PR

For an **open** Dependabot pull request, prefer commenting:

`@dependabot rebase`

Why:

- it is low risk
- it refreshes the bot branch against current `main`
- it emits a fresh `pull_request` update event
- it avoids editing the PR branch manually

### What to avoid

Avoid closing a Dependabot PR just to retrigger workflows.

Why:

- Dependabot may delete the branch immediately after close
- GitHub can then refuse to reopen the PR
- recovery may require `@dependabot recreate`, which is slower and less predictable

### Recovery if a Dependabot PR was closed

If a Dependabot PR was closed and its branch was deleted:

1. Open the closed PR conversation
2. Add a comment with `@dependabot recreate`
3. Wait for Dependabot to recreate the branch and/or PR
4. Verify that new workflow runs appear on the recreated branch

### Verification checklist

After retriggering a PR:

1. Open the latest `SCA - Dependency Review` run
2. Confirm `check-dependency-review` succeeds
3. If repo support is unavailable, confirm:
   - `dependency-review` is skipped
   - `dependency-review-disabled` succeeds
4. Read the job summary for the skip explanation

### Expected result for this repository

At the time this guide was written, the repository's dependency-review capability check did not return a success response for the private repo setup.

That means the expected healthy behavior is:

- preflight check passes
- dependency review analysis job is skipped
- summary job completes successfully

### Good operational habits

- Prefer retriggering an existing open PR over creating throwaway commits
- Use Dependabot commands instead of manual branch edits
- Treat workflow verification as complete only after observing a new GitHub Actions run
- Update branch protection expectations to match the graceful-degradation behavior