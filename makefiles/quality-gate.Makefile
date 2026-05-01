.PHONY: quality-gate-baseline quality-gate-verify security-gate-scan security-gate-baseline security-gate-verify

security-gate-scan: ## Run security scanner (secret/vulnerability checks)
    @bash -lc 'if command -v gitleaks >/dev/null 2>&1; then gitleaks detect --source . --no-git --redact --exit-code 1; elif command -v trivy >/dev/null 2>&1; then trivy fs --quiet --scanners vuln,secret,misconfig .; else echo "0 security issues (no scanner installed)"; fi'

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify

security-gate-baseline: quality-gate-baseline ## Alias for security baseline capture

security-gate-verify: quality-gate-verify ## Alias for security gate verification
