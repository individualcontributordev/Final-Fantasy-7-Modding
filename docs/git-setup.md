# Git and GitHub setup

This repo uses a **dedicated SSH key** for the `individualcontributordev` GitHub account.

## SSH key

| Item | Value |
|------|-------|
| Private key | `~/.ssh/id_ed25519_individualcontributordev` |
| Public key | `~/.ssh/id_ed25519_individualcontributordev.pub` |
| Email | `contributorindividual@gmail.com` |
| SSH host alias | `github.com-individualcontributordev` |

SSH config: `~/.ssh/config.d/individualcontributordev.config`

## One-time: add key to GitHub

1. Copy your public key:
   ```bash
   pbcopy < ~/.ssh/id_ed25519_individualcontributordev.pub
   ```
2. GitHub → **individualcontributordev** account → Settings → SSH and GPG keys → New SSH key
3. Paste and save

Test:
```bash
ssh -T git@github.com-individualcontributordev
# Expected: Hi individualcontributordev! You've successfully authenticated...
```

## Remote

```
git@github.com-individualcontributordev:individualcontributordev/ff7-modding.git
```

The `github.com-individualcontributordev` host alias ensures this repo uses the correct key (not work `id_rsa`).

## Create repo on GitHub (if empty)

If the remote repo does not exist yet:

1. https://github.com/new → name: `ff7-modding`, private or public as you prefer
2. **Do not** add README/license/gitignore (already in local repo)
3. Push:
   ```bash
   cd ~/ff7-modding
   git push -u origin main
   ```

## Local git identity (this repo only)

```
user.email = contributorindividual@gmail.com
user.name  = individualcontributordev
```

Set via `git config` without `--global` — does not affect other repos.
