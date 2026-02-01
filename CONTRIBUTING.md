# Contributing

Contributions to PQCert are welcome from everyone—regardless of background, identity, or experience level. The steps below will help you get started.

## Code of Conduct

This project follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please be respectful, constructive, and inclusive when contributing.

## How to contribute

1. **Open an issue** — Use [GitHub Issues](https://github.com/PQCert/pqcert/issues) for bugs or feature requests.
2. **Fork the repo** — Fork the repository to your account.
3. **Create a branch** — Do not work directly on `main`; use e.g. `fix/install-linux` or `feat/windows-powershell`.
4. **Make changes** — Implement your changes; add tests when possible.
5. **Open a pull request** — Submit a PR to `main` with a clear title and, if applicable, the issue number.

## Development environment

- **Python 3.10+** — For CLI and backend.
- **OpenSSL** — For certificate generation.
- Local test: `make localhost` and `make test`.

## Code style

- Python: PEP 8; the project uses `.editorconfig` at the repo root.
- Shell: `install.sh` is written in bash; keep it portable.

## Documentation

- Install guides live under `docs/` (macOS, Windows, Linux).
- When changing behavior, update the relevant `docs/*.md` file.

## Questions

- **Bugs:** Open an [issue](https://github.com/PQCert/pqcert/issues); include OS and steps to reproduce.
- **Features:** Discuss in an issue first; link your PR to it.

Thank you.
