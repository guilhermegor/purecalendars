# mike versioned docs (#64, part of #56)

Branch: `docs/64-mike-versioned-docs`.

## Done

- [x] `release-pypi.yaml`: the template's `deploy_docs` job (`cz changelog`, `mike deploy
      --update-aliases <X.Y> latest`, `mike set-default latest`), stable releases only.
- [x] `docs.yaml`: strict build check on push and pull request, deploys nothing.
- [x] `poe enable_pages` task (`bin/enable_pages.sh`, already vendored).
- [x] `mike` in the docs dependency group; `poetry.lock` refreshed.
- [x] `AGENTS.md`, `docs/contributing.md`, `docs/template-updates.md` describe the mike flow.

## Open

- [ ] Owner, once after the first release that runs `deploy_docs`: `bash bin/poe_exec.sh
      enable_pages` (points Pages at `gh-pages`; `GITHUB_TOKEN` cannot).
- [ ] Follow-up: the template's PEP 440 version validation step and `timeout-minutes` were not
      adopted here.
