---
name: setup
description: Install the Algolia CLI and configure a profile with credentials.
skill: algolia-cli
---

# Algolia CLI Setup

Guide the user through installing the Algolia CLI and configuring their credentials.

## Step 1: Check if the CLI is installed

Run:

```bash
algolia --version
```

- **If the command succeeds**, skip to Step 3.
- **If the command fails** (command not found), proceed to Step 2.

## Step 2: Install the CLI

Detect the platform and install:

**macOS (Homebrew):**

```bash
brew install algolia/algolia-cli/algolia
```

**Linux (Debian/Ubuntu):**

```bash
echo "deb [trusted=yes] https://algolia.github.io/cli/deb/ /" | sudo tee /etc/apt/sources.list.d/algolia-cli.list
sudo apt update && sudo apt install algolia
```

**Other platforms:** Direct the user to https://www.algolia.com/doc/tools/cli/get-started for download options.

After installation, verify:

```bash
algolia --version
```

## Step 3: Check for existing profiles

Run:

```bash
algolia profile list
```

- **If profiles exist**, ask the user if they want to use an existing profile or create a new one.
- **If no profiles exist** (or the command shows an empty list), proceed to Step 4.

## Step 4: Create a profile

Ask the user for:
1. **Application ID** — Found in Algolia Dashboard → Settings → API Keys
2. **Admin API key** — Same location. Needed for write operations.

Then run:

```bash
algolia profile add --name "default" --app-id "<APP_ID>" --api-key "<API_KEY>" --default
```

> **Important:** Always provide all three flags to avoid interactive prompts.

## Step 5: Verify the connection

Run:

```bash
algolia indices list
```

- **If indices are listed**, setup is complete. Tell the user they're ready to go.
- **If an error occurs**, check:
  - Invalid API key → ask user to double-check credentials
  - Network error → ask user to check connectivity
  - No indices → that's fine, the connection works but the app has no indices yet
