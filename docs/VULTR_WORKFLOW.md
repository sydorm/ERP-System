# Vultr & GitHub Workflow Rules

## 1. Vultr Server Commands
- **Antigravity cannot execute commands directly on the Vultr server.**
- Every time a change needs to be applied to the server (database cleanup, migrations, logs check), Antigravity must provide the exact command for the user to copy and run in the Vultr terminal.
- Antigravity must explain what each command does before asking the user to run it.

## 2. GitHub Synchronization
- After every successful bugfix or code update, Antigravity must provide the Git commands to push the changes to GitHub.
- Commit messages must be descriptive of the changes made.

## 3. Server Sync (Vultr)
- After pushing to GitHub, Antigravity must remind the user to run `git pull` on the Vultr server to apply the changes.
