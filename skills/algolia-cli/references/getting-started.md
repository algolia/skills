# Getting Started with the Algolia CLI

## Prerequisites

- **Algolia account** — Optional upfront: `algolia auth signup` creates one from the CLI. You can also [sign up free](https://www.algolia.com/users/sign_up) on the web.
- **Application ID and API keys** — Nothing to copy by hand: `algolia auth login` fetches your applications and provisions credentials automatically (stored in your OS keychain).

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

## Authentication

Signing in stores your Algolia credentials locally so you don't need to pass them with every command. `algolia auth login` handles OAuth sign-in and profile creation in one step — no need to copy an API key by hand.

### Sign in

```bash
algolia auth login
```

This opens your browser for OAuth sign-in, then fetches your applications, lets you pick one, and creates a CLI profile with the Admin API key.

> **Tip:** On SSH sessions or containers where a browser can't open, use `algolia auth login --no-browser` to print the URL instead.

### Create a new account

If you don't have an Algolia account yet, sign up from the CLI:

```bash
algolia auth signup
```

This opens the sign-up page, then completes the same OAuth flow as `login`.

### Verify you're signed in

```bash
algolia auth status
```

This shows whether you're signed in, which application is current, and whether API credentials are available. You can also confirm your setup by listing indices:

```bash
algolia indices list
```

This should list the indices in your application.

### Sign out

```bash
algolia auth logout
```

This revokes the stored OAuth tokens and removes them from the local keychain.

### Where your credentials are stored

Non-secret settings (current application, application aliases, hosts) are stored in:

```
~/.config/algolia/state.toml
```

Your API keys are never written to this file — they're stored securely in your operating system's keychain.

### Multiple applications

Select a specific application by name when you sign in:

```bash
algolia auth login --app-name "production" --default
```

Switch the current application at any time:

```bash
algolia application select --app-name "staging"
```

## Next Steps

- See the [Command Reference](commands.md) for full syntax and examples.
- See the [Algolia CLI documentation](https://www.algolia.com/doc/tools/cli/get-started) for additional details.
