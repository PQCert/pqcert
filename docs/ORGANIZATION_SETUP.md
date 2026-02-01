# PQCert organization – Getting started checklist

GitHub organization: **[https://github.com/PQCert](https://github.com/PQCert)**

The steps below align with the suggestions on the organization page.

---

## 1. Create or import a repository

**Option A – New repo (recommended)**

1. On [PQCert](https://github.com/PQCert), go to **Repositories** → **New repository**.
2. Repository name: **pqcert**.
3. Create as Public, without adding a README (the local project already has one).
4. In your local project:
   ```bash
   cd /path/to/pqcert
   git remote add origin https://github.com/PQCert/pqcert.git
   git branch -M main
   git push -u origin main
   ```

**Option B – Import**

1. **Repositories** → **Import repository**.
2. Enter the URL of an existing repo (if any); or create an empty repo and push as above.

---

## 2. Organization profile (README)

The organization profile can show a “README and pinned repositories” to the public.

- **Profile README:** Create a **public** repo named `.github` under the PQCert organization. Add a **README.md** at the **root** of that repo (not under `profile/`). This file is shown on the organization profile.
- Example content: “PQCert – Post-Quantum Certificates for local development. https://github.com/PQCert/pqcert”

---

## 3. Invite your first member

1. Go to **People** → **Invite member**.
2. Search by GitHub username or email (e.g. **your-username**).
3. Role: **Owner** (founder) or **Member**.
4. Send the invite.

---

## 4. Branch ruleset (recommended)

Use **Rulesets** → **New branch ruleset** to protect `main`. Suggested values:

| Field | Value |
|-------|--------|
| **Ruleset name** | `Protect main` |
| **Enforcement status** | **Active** |
| **Bypass list** | Leave empty, or add a team (e.g. org owners) if maintainers need to bypass for emergencies. |
| **Target branches** | **Branch name pattern** → `main` (and optionally `master` if you use it). |
| **Rules** | Enable these: |
| | ☑ **Require a pull request before merging** — All changes go through a PR. Optionally set “Require approvals” (e.g. 1). |
| | ☑ **Require status checks to pass** — Add the **CI** workflow (so the `CI` job must pass before merge). |
| | ☑ **Block force pushes** — No force push to `main`. |
| | ☐ **Restrict creations** — Leave **off** (so people can still create branches). |
| | ☐ **Restrict updates** — Leave **off** (updates go via PR, not direct push). |
| | ☐ **Restrict deletions** — Optional: enable if only admins should delete `main`. |
| | ☐ **Require linear history** — Optional: enable for a strict linear history (no merge commits). |
| | ☐ **Require signed commits** — Optional: enable if you want verified signatures. |
| | ☐ **Require merge queue** — Optional: for high-traffic repos. |

**Do not enable:** “Restrict creations” and “Restrict updates” for everyone without a bypass list, or collaborators cannot push new branches or update them.

After creating the ruleset, under **Require status checks to pass** add the status check name: **CI** (from `.github/workflows/ci.yml`).

### Only the founder can merge

To ensure **only the founder** (e.g. kursat.arslan@outlook.com) can merge into `main`:

1. **Repo permissions**  
   - Go to the **pqcert** repo → **Settings** → **Collaborators and teams** (or **Manage access**).  
   - Grant **Maintain** or **Admin** only to the founder’s GitHub account (the one linked to kursat.arslan@outlook.com).  
   - Do **not** give **Write** or **Maintain** to other users or teams if only the founder should merge.  
   - Others can contribute via fork + pull request; only the founder will be able to merge those PRs.

2. **Optional: Bypass list**  
   - In the ruleset, **Bypass list**: leave **empty** if you want every change (including yours) to go through a PR.  
   - If you want to allow yourself to push directly to `main` in emergencies, add **your user** (or a team that contains only you) to the bypass list. Then only you can bypass “Require a pull request” and push to `main`; others still must use PRs and only you can merge.

Result: only the founder can merge PRs; others can open PRs but cannot merge.

**Alternative (legacy):** If your repo uses **Settings** → **Branches** → **Branch protection rules** instead of Rulesets, create a rule for branch name **main** with “Require a pull request before merging” and “Require status checks to pass” (CI).

---

## 5. CI/CD – Simple test (optional)

To run the install script or tests via GitHub Actions:

1. In the **pqcert** repo → **Actions** → **New workflow** → **set up a workflow yourself**.
2. Or use the existing `.github/workflows/ci.yml` in the project:
   - Runs `install.sh` syntax check and CLI (Linux runner).
   - Optional backend health check.

This satisfies the “Run a continuous integration test” suggestion.

---

## 6. Discussions (optional)

1. In the **pqcert** repo → **Settings** → **General** → **Features**.
2. Enable **Discussions**.
3. You can also enable discussions at the organization level from the org page (**Set up discussions**).

---

## Summary

| Suggestion | Action |
|------------|--------|
| Repo | Create `PQCert/pqcert` and push your local code. |
| Invite | People → Invite member (e.g. your-username or others). |
| Branch ruleset | Add a ruleset for `main` (PR + status check + block force push). |
| CI | Use the existing Actions workflow (install/test). |
| Discussions | Enable on the repo or org. |
| Profile | Optional: create a `.github` repo with a README for the org profile. |

Start with **creating the repo and pushing**, then use **People** and **Settings** for the rest.
