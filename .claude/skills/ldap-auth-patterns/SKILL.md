---
name: ldap-auth-patterns
description: "Safe patterns for the custom LDAP bind + JWT auth stack (python-ldap, python-jose, bcrypt)."
when_to_use: "editing or reviewing auth code that binds to LDAP or issues/verifies JWTs"
metadata:
  version: "1.0.0"
---

# LDAP + JWT Auth Patterns

This codebase implements a custom auth stack: LDAP bind for identity,
`python-jose` for JWT issuance, `bcrypt` for local password hashing. Standard
framework auth flows don't apply here — review against these specific risks.

## LDAP

- Always escape user input used in LDAP filter strings (RFC 4515) — never
  build a filter with raw string concatenation/f-strings.
- Use LDAP bind (not a search-then-compare against a stored hash) to verify
  the password — never fetch and compare `userPassword` yourself.
- Fail closed: any bind exception is an authentication failure, not a bypass.

## JWT (python-jose)

- Pin the algorithm explicitly on both issuance and verification
  (`algorithms=["HS256"]` or similar) — never accept `alg` from the token header.
- Always set and check `exp`; reject unsigned/`none`-algorithm tokens.
- Keep the signing secret out of source — see `.claude/skills` secrets handling
  conventions and the repo's env/secret loading pattern.

## bcrypt

- Use `bcrypt.checkpw` for comparison — never a manual string equality check
  (timing attack) or a homegrown compare loop.

## Review checklist

- [ ] LDAP filter inputs escaped.
- [ ] Auth uses LDAP bind, not password comparison.
- [ ] JWT algorithm pinned, `exp` checked, no `none` algorithm accepted.
- [ ] Password comparisons go through `bcrypt.checkpw`.
