# Security

## Reporting a vulnerability

If you find a security-related issue, please **do not** open a public issue. Report it directly to the project maintainers.

### How to report

- **Email:** Reach out via the [PQCert organization](https://github.com/PQCert) on GitHub; or
- **GitHub Security:** Use **Security** → **Report a vulnerability** on the repo page (if enabled).

When possible, include:

- A short description of the issue
- Affected component (CLI, backend, install script, etc.)
- Steps to reproduce (if possible)
- Suggested fix (if any)

### What to expect

- We will review the report in a timely manner.
- We will keep details confidential until a fix is released (coordinated disclosure).
- We may acknowledge the reporter(s) (optional) in credits.

### Scope of PQCert

PQCert generates a **local development** Root CA and localhost certificate. Use this CA only on machines you trust; use your own CA in production.

Certificate files (`~/.pqcert`) and especially private keys must not be shared and should be stored securely.
