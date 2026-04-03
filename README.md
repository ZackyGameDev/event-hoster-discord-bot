# Event Hoster Discord Bot

> A Discord bot built to handle everything a giveaway and events-hosting server needs — giveaways, Simon Says events, a ticket support system, moderation utilities, and fun commands. Currently on version **v0.0.8**.

[![Add to Server](https://img.shields.io/badge/Add%20to%20Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=759290479069626418&permissions=2147483639&scope=bot)
[![Support Server](https://img.shields.io/badge/Support%20Server-Join-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/QNsmC84)

---

## Features

- 🎉 **Giveaways** — Conversational giveaway wizard; live countdown on the embed; automatic winner selection via reaction.
- 🤡 **Simon Says Events** — Full event lifecycle: participant sign-up, kill/revive, alive-count, and reset.
- 🎟 **Ticket System** — Private per-user ticket channels with staff access; clean close flow with DM notification.
- 🔨 **Moderation** — Ban, kick, and unban commands with permission guards.
- 🎮 **Fun** — Magic 8-ball, coin flip, dice roll, and Reddit meme fetching.
- ⚙️ **Per-server prefix** — Every guild can set its own command prefix.

---

## Prerequisites

- **Python 3.7+**
- A **Discord Bot Token** (from the [Discord Developer Portal](https://discord.com/developers/applications))
- A **Reddit App** (for meme commands) — [create one here](https://www.reddit.com/prefs/apps)
- A **Google Service Account** (for the optional Google Sheets database sync) — [Google Cloud Console](https://console.cloud.google.com/)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/ZackyGameDev/event-hoster-discord-bot.git
cd event-hoster-discord-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the required secret files (see Configuration below)

# 4. Run the bot
python event-hoster.py
```

---

## Configuration

### `token.txt`
Place your Discord bot token in this file — one line, no quotes.

```
YOUR_DISCORD_BOT_TOKEN_HERE
```

### `reddit_creds.json`
Required for `$meme` and `$dank_meme` commands.

```json
{
  "client_id": "YOUR_REDDIT_CLIENT_ID",
  "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
  "username": "YOUR_REDDIT_USERNAME",
  "password": "YOUR_REDDIT_PASSWORD",
  "user_agent": "EventHosterBot/0.0.8"
}
```

### `ServiceAccountCreds.json`
Required for the optional Google Sheets database sync. Download this from your Google Cloud project's service account. If you don't need Sheets sync, add `"data.events.database-fetcher"` to `blacklisted_extensions` in `config.json` to disable it.

### `config.json` (already in repo — edit as needed)

| Key | Type | Description |
|---|---|---|
| `blacklisted_extensions` | list | Extension module paths that will **not** be loaded at startup |
| `json_file_upload_channel_id` | int | Channel ID where `id-list.json` backups are posted every 60 minutes |
| `suggestions_channel_id` | int | Channel ID where `$suggest` posts land |
| `bug_reports_channel_id` | int | Channel ID where `$report` posts land |
| `bot_info` | string | Text displayed by `$botinfo` |

---

## Required Bot Permissions

The bot requires the following permissions (the invite link above already requests them):

| Permission | Why |
|---|---|
| Manage Roles | Simon Says participant/disqualified role assignment |
| Manage Channels | Creating and deleting ticket channels |
| Ban Members | `$ban` / `$unban` commands |
| Kick Members | `$kick` command |
| View Audit Log | Verifying that a channel is a bot-created ticket |
| Manage Messages | Deleting command invocations |
| Embed Links | Sending rich embeds |
| Send Messages | All commands |
| Read Message History | Ticket and giveaway message fetching |
| Add Reactions | Giveaway and Simon Says participation messages |

---

## Server Setup

Before using event or ticket commands, a server admin must run the setup wizards once. The bot will ask questions in sequence — reply in the same channel.

### Simon Says Setup
```
$SimonSaysSetup
```
You will be asked to name or mention:
1. The **Simon Says Participant** role
2. The **Simon Says Controller** role (event host)
3. The **Simon Says Disqualified** role
4. The **Simon Says event channel**

### Ticket System Setup
```
$TicketSystemSetup
```
You will be asked to name or mention:
1. The **Ticket Staff** role (can see all tickets)
2. The **ticket category** (channel category where tickets are created)

---

## Command Reference

The default prefix is `$`. Use `$prefix <new_prefix>` to change it per server. Mentioning the bot (`@EventHoster`) will remind you of the current prefix.

### General

| Command | Description | Permission |
|---|---|---|
| `$help` | Interactive help menu — react with an emoji to browse categories | Everyone |
| `$ping` | Shows response delay and WebSocket latency | Everyone |
| `$prefix <prefix>` | Changes the bot prefix for this server | Manage Server |
| `$botinfo` | Shows information about the bot | Everyone |
| `$invite` | Shows the invite link and support server | Everyone |
| `$report <issue>` | Sends a bug report to the bot's creator | Everyone |
| `$suggest <suggestion>` | Sends a feature suggestion to the bot's creator | Everyone |

### Giveaways

| Command | Description | Permission |
|---|---|---|
| `$giveaway start` | Starts a giveaway via a step-by-step wizard (duration, prize, winner count, channel) | `Manage Server` **or** role named `Giveaways` |

**How it works:**
1. Run `$giveaway start` and answer the prompts (type `stop` at any prompt to cancel).
2. Duration format: `1d 2h 30m` (days, hours, minutes, seconds).
3. Max 10 winners; prize text limited to 240 characters.
4. The bot posts a 🎉-reaction embed in the chosen channel and updates the countdown automatically.
5. At the end, the bot mentions the winner(s) and edits the embed.

### Simon Says Events

| Command | Aliases | Description | Permission |
|---|---|---|---|
| `$SimonSaysStart <duration>` | `SimonSaysParticipationMessage` | Posts a 🎉-reaction participation embed; auto-assigns Participant role | Simon Says Controller role |
| `$SimonSays <message>` | `ss` | Posts a "Simon Says!" embed in the event channel | Simon Says Controller role |
| `$SimonLeftAlive` | `simonLeft`, `simonRemainingParticipants` | Lists participants still alive | Everyone |
| `$SimonKill @member...` | `kill` | Disqualifies one or more participants | Simon Says Controller role |
| `$SimonRevive @member...` | `revive` | Re-instates disqualified participants | Simon Says Controller role |
| `$SimonReset` | `simonpackup`, `simonresetroles` | Strips event roles from all members | Simon Says Controller role |
| `$SimonSaysSetup` | `simon-says-setup` | Interactive server setup wizard | Manage Roles + Manage Channels |

**Duration format for `$SimonSaysStart`:** `5m`, `2h`, `1h 30m`, etc. Maximum is 24 hours.

### Ticket System

| Command | Aliases | Description | Permission |
|---|---|---|---|
| `$new [reason]` | `newTicket`, `new-ticket` | Creates a private ticket channel | Everyone |
| `$add @user_or_role` | `adduser`, `addrole` | Adds a user or role to the current ticket | Inside a ticket channel |
| `$remove @user_or_role` | `removeuser`, `removerole` | Removes a user or role from the current ticket | Inside a ticket channel |
| `$close [reason]` | `closeticket`, `ticket-close` | Closes the ticket after a 10-second window (send any message to cancel) | Inside a ticket channel |
| `$TicketSystemSetup` | `ticket-system-setup` | Interactive server setup wizard | Server admin |

### Moderation

| Command | Description | Permission |
|---|---|---|
| `$ban @member [reason]` | Bans a member (reason max 150 chars) | Ban Members |
| `$kick @member [reason]` | Kicks a member (reason max 150 chars) | Kick Members |
| `$unban Username#0000` | Unbans a user by their `Username#Tag` | Ban Members |

### Fun

| Command | Aliases | Cooldown | Description |
|---|---|---|---|
| `$8ball <question>` | `eight_ball` | — | Magic 8-ball prediction |
| `$flipcoin` | `coinflip`, `flip_coin` | — | Flips a coin |
| `$rolldice` | `roll_dice` | — | Rolls a dice (0–5) |
| `$meme` | `memes` | 5 s / user | Random image from r/memes |
| `$dankmeme` | `dank_meme`, `dankmemes` | 5 s / user | Random image from r/dankmemes |
| `$sendMemes <count> [dank]` | `send_memes`, `send-memes` | 30 s / user | Sends 1–25 memes to your DMs (add `dank` for r/dankmemes) |

---

## Data Storage

All persistent data is stored in **`id-list.json`** (created automatically on first run, gitignored).

- Saved to disk every **30 seconds**.
- Backed up to the configured Discord channel every **60 minutes**.
- Stores: per-guild prefixes, ticket counts, Simon Says role/channel IDs, ticket system role/category IDs, and active giveaway state.

An optional **Google Sheets** integration (`data/events/database-fetcher.py`) syncs a separate Simon Says config table every 15 minutes. Disable it by adding `"data.events.database-fetcher"` to `blacklisted_extensions` in `config.json` if you don't have a service account set up.

---

## Deployment

No Docker or process manager config is included. The simplest approach is a direct Python invocation on a VPS or any machine with Python installed:

```bash
python event-hoster.py
```

For daemonization, you can wrap it with **PM2**, **systemd**, or **screen**/**tmux** yourself. The bot logs all activity to `console.log` (gitignored) with timestamps.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Create the required secret files (`token.txt`, `reddit_creds.json`) pointing at a test Discord application and Reddit app.
3. Edit `config.json` with channel IDs from your test server.
4. Run `python event-hoster.py` and verify your changes.
5. There are no automated tests or linters configured — manual testing against a Discord server is the current workflow.

The bot uses a **cog/extension** system (`discord.ext.commands`). Every `.py` file under `data/` with a `setup(client)` function is automatically loaded at startup. Add new features by creating a new file in the appropriate subdirectory and implementing a cog.

---

## License

See [LICENSE.md](LICENSE.md).

---

*This README was written by [GitHub Copilot](https://github.com/features/copilot).*
