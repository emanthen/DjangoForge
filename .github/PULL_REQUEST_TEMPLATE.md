## What does this PR do?

<!--
Describe the change clearly. What problem does it solve or what feature does it add?
Link to any relevant issue: Closes #123
-->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Performance improvement
- [ ] Refactoring (no functional change)
- [ ] Documentation update
- [ ] CI/CD / infrastructure change

## How has this been tested?

<!--
Describe the tests you ran to verify your changes.
Include instructions so reviewers can reproduce.
-->

- [ ] Unit tests added / updated
- [ ] Integration tests added / updated
- [ ] Manually tested locally with `docker compose up`
- [ ] Tested against a staging environment

## Screenshots (if UI change)

<!--
Paste a screenshot of the before and after if this changes any UI.
Dark mode and mobile views are a bonus.
-->

## Checklist

- [ ] My code follows the project's style (`ruff check .` and `ruff format .` pass)
- [ ] I have added tests for new behavior (coverage has not dropped)
- [ ] All existing tests pass (`pytest`)
- [ ] `python manage.py check --deploy` passes (for settings changes)
- [ ] I have updated `CHANGELOG.md` under `[Unreleased]`
- [ ] I have updated documentation if my change requires it
- [ ] No secrets, API keys, or credentials are in the code (`detect-secrets` scan passes)
- [ ] I have reviewed my own diff before submitting

## Migration notes

<!--
If this PR includes a database migration:
- Is the migration safe to run on a live database?
- Does it require any data backfill?
- Does it have a reverse migration?
-->

N/A
