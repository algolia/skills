# Getting Started with the Algolia CLI

## Prerequisites

- **Algolia account** — [Sign up free](https://www.algolia.com/users/sign_up)
- **Application ID** — Found in [Dashboard → Settings → API Keys](https://dashboard.algolia.com/account/api-keys/all)
- **Admin API key** — Same location. Required for write operations (import, delete, settings).

## Installation

### macOS (Homebrew)

```bash
brew install algolia/algolia-cli/algolia
```

### Linux (deb/rpm)

```bash
# Debian/Ubuntu
echo "deb [trusted=yes] https://algolia.github.io/cli/deb/ /" | sudo tee /etc/apt/sources.list.d/algolia-cli.list
sudo apt update && sudo apt install algolia

# RPM-based (Fedora, RHEL)
echo "[algolia-cli]
name=Algolia CLI
baseurl=https://algolia.github.io/cli/rpm/
enabled=1
gpgcheck=0" | sudo tee /etc/yum.repos.d/algolia-cli.repo
sudo yum install algolia
```

### Windows (Chocolatey)

```bash
choco install algolia-cli
```

### Verify installation

```bash
algolia --version
```

## Profile Setup

A profile stores your Algolia credentials locally so you don't need to pass them with every command.

### Create a profile (non-interactive)

```bash
algolia profile add --name "default" --app-id "YOUR_APP_ID" --api-key "YOUR_ADMIN_API_KEY" --default
```

> **Important:** Always provide all three flags (`--name`, `--app-id`, `--api-key`) to avoid interactive prompts that require terminal input.

### Verify the profile

```bash
algolia indices list
```

This should list the indices in your application.

### List existing profiles

```bash
algolia profile list
```

### Configuration file location

Profiles are stored in:

```
~/.config/algolia/config.toml
```

### Multiple profiles

You can add multiple profiles for different applications:

```bash
algolia profile add --name "staging" --app-id "STAGING_ID" --api-key "STAGING_KEY"
algolia profile add --name "production" --app-id "PROD_ID" --api-key "PROD_KEY" --default
```

Use `-p <profile>` to target a specific profile:

```bash
algolia indices list -p staging
```

## Next Steps

- See the [Command Reference](commands.md) for full syntax and examples.
- See the [Algolia CLI documentation](https://www.algolia.com/doc/tools/cli/get-started) for additional details.
