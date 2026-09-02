# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-351] - 2026-09-02
### Bug Fixes

- **api:** Restore all files lost in rebase abort\n\n- Rewrite docker-compose.yml for full dev stack (api + frontend)\n- Restore api/app/main.py: use get_settings(), no CORS wildcard\n- Restore api/app/config.py: lru_cache, get_settings(), cors_origins\n- Rewrite api/app/security.py: SecurityService class, no passlib\n- Rewrite all routers to use service classes and constants\n- Rewrite project_manager.py: ProjectManager class with load/list_all\n- Rewrite docker_client.py: DockerClientService class singleton\n- Remove passlib[bcrypt] from requirements.txt

- **ops:** Rewrite pre-commit config + security hardening (LDAP, PyJWT, deps)"

- **k8s:** Mount Docker socket read-only in API deployment (cherry-pick from #22)

- **frontend:** Remove legacy CRA files and fix TypeScript build (#20)

- **pre-commit:** Fix yaml-sorter duplicate key, yamlfmt exclusions, and JSON formatting

- **standards:** Apply compliance fixes from shared-standards audit (#60)

- Standards compliance (pre-commit semver, cov-fail-under, GitVersion) (#61)

- **tests:** Resolve merge conflicts, rewrite tests with mocker.patch and Given-When-Then (#62)

- **e2e:** Add role=alert to error div, fix projects test timing (#64)

- **api:** Explicitly set package discovery to avoid setuptools flat-layout error

- **api:** Explicitly set package discovery to avoid setuptools flat-layout error

- **ci:** Use python 3.14 in pre-commit workflow to match default_language_version

- **ci:** Replace invalid Mainline mode with ContinuousDelivery for GitVersion v6

- **ts:** Add ignoreDeprecations 6.0 for baseUrl option in TypeScript 6

- **ci:** Apply prettier formatting and skip no-commit-to-branch in CI

- **security:** Untrack .env file containing real credentials

- **ci:** Bump actions/checkout and setup-python to v6 (#71)

- **ci:** Downgrade sonarqube-scan-action v8->v4.2.1 for SonarCloud (#72)

- **ci:** Add SKIP no-commit-to-branch for pre-commit action

- **security:** Add uv.lock for reproducible builds

- **security:** Remove secrets:inherit hotspot (S7227)

- **quality:** Fix void operator, cognitive complexity, and document HTTP responses (S3735/S8415/S3776)

- **quality:** Resolve SonarCloud issues S1192/S5864/S8415/S3504/S6479/S7924

- **tests:** Replace bare Exception with WebSocketDisconnect, merge nested with statements (SIM117/B017), remove duplicate test_streams_log_lines

- **security:** Restrict CORS origins, migrate python-jose to PyJWT, move kubeconfig secret to env

- **format:** Apply ruff format — wrap long decorators, fix assert order, remove unused imports

- **ci:** Add libldap2-dev system dep, remove invalid ignoreDeprecations 6.0 from tsconfig

- **lint:** Ruff working-directory=api, per-file-ignores tests/**

- **ci:** Run mypy from api/ working-directory (sources=app)

- **ci:** Revert ruff-check to config=api/pyproject.toml sources=api (@v1 has no working-directory)

- **lint:** Per-file-ignores with api/ prefix for repo-root ruff invocation

- **types:** Remove unused type:ignore comments, add ping() return type, disable warn_unused_ignores

- **ci:** Skip no-commit-to-branch hook in quality workflow

- **auth:** Skip 401 redirect for login endpoint to allow error display

- **api:** Sync ruff version and fix import ordering (#82)

- **pre-commit:** Update chrysa/pre-commit-tools to v0.1.1-92

- **ci:** Apply yamlfmt, prettier and markdownlint formatting (#104)

- **claude:** Wrap PreCompact/Notification hooks in hooks array (#132)

- **frontend:** Unbreak production build and Vitest unit tests (#137)

- **ci:** Run mypy on api-test image (was failing: No module named mypy) (#153)

- **pre-commit:** Repair makefile-check hook indentation (#158)

- **ci:** Repair Ruff/Mypy install and ESLint flat-config crash (#162)

- **ci:** Make main green — pre-commit JSON oscillation + missing sentry-sdk (#181)

- **pre-commit:** Drop leaked canonical-drift local hooks (#196)

- Resolve SonarCloud blocker & critical findings (#206)


### CI

- Add FUNDING.yml (sponsoring)

- **pre-commit:** Bump chrysa/pre-commit-tools to v0.1.1-72 (#63)

- **pre-commit:** Bump chrysa/pre-commit-tools to v0.1.1-73 (#65)

- Migrate lint-api job to chrysa/github-actions composite actions (#66)

- Migrate to chrysa/github-actions composite actions (#67)

- Fix python-version 3.12→3.14, add mypy job

- Centralize sonar scanning via chrysa/github-actions/sonar-scan@v1 (#73)

- **sonar:** Integrate SonarCloud scan into ci.yml with coverage artifacts

- Add workflow_dispatch trigger to ci.yml

- **github-actions:** Fix checkout@v4 across all workflows (#83)

- **actions:** Fix checkout@v4 and upload-artifact@v4 across all workflows (#105)

- **secret-scan:** Use reusable workflow (fixes gitleaks 403 perms) (#133)

- Fix dead label-sync action (marocchino 404 -> crazy-max v6) (#138)

- **quality-gate:** Fix startup_failure (grant write scopes to reusable caller) (#154)

- **pre-commit:** Wire makefile-check hook (v0.1.1-94) (#157)

- Pin chrysa/github-actions reusable workflows to @v1.2.0 (#193)

- **quality-gate:** Bump reusable workflow to v1.2.3 (skip when target absent)

- Bump ci-fullstack.yml to @v1.2.4

- Bump pre-commit.yml to @v1.2.4

- Adopt guideline-checker blocking gate (#303)

- Bump guideline-checker to v1.15.4 (#304)


### Documentation

- Add tests, typing and frontend instruction files

- **instructions:** Add loading states convention from Notion Engineering Standards (#76)


### Features

- **ci:** Add GitVersion + git-cliff versioning workflow\n\n- Add GitVersion.yml with Mainline strategy and conventional-commit bump rules\n- Add cliff.toml for automated CHANGELOG.md generation\n- Add release.yml workflow (GitVersion → git-cliff → GitHub Release)\n- Update cd.yml: trigger on release:published, use semver Docker tags\n- Add .env.example\n- Expand .gitignore with .vscode/, .env, __pycache__, node_modules\n- Add api/app/constants.py with all shared string constants\n- Add services layer: alerts, auth, lifecycle, metrics, topology\n- Add api docker entrypoint script\n- Add api/.dockerignore

- Full rewrite — FastAPI backend, React 19 frontend, K8s + Traefik manifests

- **ui:** Add responsive mobile design (#86)

- **demo:** Add demo mode with fixture data and DEMO banner (#159)

- **ui:** Neon Brutalist re-skin (chrysa design system) (#161)

- **frontend:** Project-workspace service inspector — Phase-4 IA pass (#203)


### Miscellaneous

- Migrate to pyproject.toml, add pre-commit and tests scaffold

- Migrate to GitHub — CI/CD, pre-commit, Copilot instructions

- **k8s:** Set GHCR owner to chrysa + dynamic deploy URL

- **docker:** Add HEALTHCHECK + non-root user to production stage (closes #16)

- **docker:** Add HEALTHCHECK + non-root user + K8s GHCR migration (#18)

- Sync issue/PR templates from shared-standards

- **deps:** Add dependabot configuration (#26)

- Add CLAUDE.md, dependabot + bump GHA actions to v6 (#15)

- **deps:** Bump docker/login-action from 3 to 4 (#31)

- **deps:** Bump actions/checkout from 4 to 6 (#30)

- **deps:** Bump softprops/action-gh-release from 2 to 3 (#29)

- **deps:** Bump docker/build-push-action from 6 to 7 (#28)

- **deps:** Bump azure/setup-kubectl from 4 to 5 (#27)

- **dx:** Add Claude Code optimization config (#25)

- Add automation & industrialization guidelines to copilot instructions

- **deps:** Bump docker/metadata-action from 5 to 6 (#33)

- **deps:** Bump actions/cache from 4 to 5 (#34)

- **deps:** Bump docker/setup-buildx-action from 3 to 4 (#35)

- **deps:** Bump actions/upload-artifact from 4 to 7 (#36)

- **deps:** Bump actions/setup-python from 5 to 6 (#37)

- **bootstrap:** Auto-sync via chrysa-bootstrap.sh

- **deps:** Bump gittools/actions from 3 to 4 (#39)

- Add CHANGELOG, DECISIONS and tests/README from quality-gate branch

- Bootstrap standards sync (#52)

- **ci:** Pre-commit hooks and GitHub Actions hardening (#53)

- **ci:** Update actions/checkout from v4 to v5 (#54)

- Apply standards compliance updates

- **ci:** Delegate utility workflows to chrysa/github-actions

- Reformat config, fix lint (I001), use api-test for lint, add README screenshot (#74)

- Format and docs update (#75)

- Port update, standards compliance, E2E fixes (#80)

- **observability:** Add Sentry SDK integration (#81)

- **ci:** Bump GitHub Actions to ecosystem standard versions (#85)

- **ui:** Add backend connection status banner (#87)

- Chore/backend-connection-banner (#88)

- Chore/format-and-docs-update (#89)

- Chore/install-project-composite (#90)

- Ci/actions-versions (#91)

- Ci/standards-compliance (#92)

- Feat/sentry-integration (#93)

- **pre-commit:** Add missing chrysa hooks from standards audit (#94)

- **frontend:** Remove vite server.proxy, use VITE_API_URL directly (#95)

- **ui-ux:** Reference ui-ux skill in CLAUDE.md (#102)

- **sonar:** Exclude coverage — no tests running in CI (#106)

- **dependabot:** Add npm, pip ecosystem coverage (#108)

- **standards:** Realign gitignore + sonar pin (#134)

- **config:** Normalize repo to chrysa standard (#155)

- **makefile:** Declare tier (fullstack) and add ci gate (#156)

- **claude:** Dump shared agents + .mcp.json + settings (#160)

- **compose:** Standardize container naming via project name (#182)

- Adopt lean fullstack CI + makefile-tier (#183)

- Sync chrysa shared standards (#194)

- Sync chrysa shared standards (#195)

- Adopt canonical cliff.toml (#197)

- Adopt canonical GitVersion.yml (ContinuousDeployment) (#198)

- **pre-commit:** Bump pre-commit-tools to v0.1.1-95 (makefile-check fix) (#199)

- Sync chrysa shared standards (#200)

- Sync chrysa shared standards (#201)

- Sync chrysa shared standards (#204)

- Sync chrysa shared standards (#207)

- **standards:** Distribute shared standards (Notion logging) (#226)

- Sync chrysa shared standards (#228)

- **claude:** Sync .claude config (#246)

- **deps:** Bump starlette from 0.37.2 to 1.3.1 in /api (#259)

- **deps:** Bump ujson from 5.12.1 to 5.13.0 in /api (#262)

- Sync chrysa shared standards (#263)

- **pre-commit:** Add css-outside-stylesheet hook (v0.1.1-96) (#264)

- **pre-commit:** Activate detection hooks (v0.1.1-97) (#265)

- Sync chrysa shared standards (#281)

- Sync chrysa shared standards (#282)

- Sync chrysa shared standards (#283)

- Artifact isolation — non-root docker + caches out of tree + prod/dev stages (#284)

- Sync chrysa shared standards (#285)

- Sync chrysa shared standards (#286)

- **deps:** Bump pyasn1 from 0.6.3 to 0.6.4 in /api (#288)

- Sync chrysa shared standards (#302)

- Sync chrysa shared standards (#305)

- Sync chrysa shared standards (#306)

- Sync chrysa shared standards (#307)

- Sync chrysa shared standards (#309)

- **repo:** Drop opencode.json and the unfilled DECISIONS template (#311)

- Sync chrysa shared standards (#312)

- Sync chrysa shared standards (#313)

- Bump guideline-checker to v1.30.10 (#314)

- Sync chrysa shared standards (#329)

- Sync chrysa shared standards (#330)

- Sync chrysa shared standards (#332)

- Sync chrysa shared standards (#333)

- **hooks:** Unblock the push gate (#331)

- Sync chrysa shared standards (#334)

- Sync chrysa transverse standards (#379)

- **docker:** Compliant multi-stage frontend Dockerfile (#388)


### Refactor

- **api:** Apply Padam Python guidelines

- **api:** Enforce Python guidelines from instructions


### Tests

- **e2e:** Complete user-journey coverage (error/empty/degraded paths) (#136)


### Design

- **frontend:** Migrate to Console persona (SCSS) (#180)


<--apply generated by [git-cliff](https://git-cliff.org) -->
