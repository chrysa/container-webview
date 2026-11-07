---
name: docker-engine-security
description: "Safe usage patterns for the Docker Engine API via the `docker` Python SDK — the highest-risk surface in this codebase."
when_to_use: "editing api/app code that talks to the Docker Engine API/SDK, reviewing a diff touching container lifecycle, exec, mounts, or image handling"
metadata:
  version: "1.0.0"
---

# Docker Engine API Security

`api/app` controls the Docker Engine directly via the `docker` SDK. A mistake
here is container escape or host compromise, not a UI bug.

## Do

- Validate/allowlist container and image names before passing them to any SDK call.
- Set a timeout on every Engine API call (`docker.DockerClient(timeout=...)`).
- Scope the Docker socket mount to the minimum required (read-only where possible).
- Log every privileged operation (start/stop/exec/remove) with the acting user.

## Don't

- Never pass `privileged=True`.
- Never expose `/var/run/docker.sock` to an unauthenticated endpoint.
- Never interpolate user input into a shell command run via `exec_run`.
- Never mount the host filesystem into a container without an explicit, reviewed allowlist.

## Review checklist for diffs touching `api/app/**docker**`

- [ ] Container/image identifiers validated against a known allowlist or regex.
- [ ] No `privileged=True`.
- [ ] Timeout set on the client or call.
- [ ] No raw user input reaches `exec_run`/`create_container` unescaped.
