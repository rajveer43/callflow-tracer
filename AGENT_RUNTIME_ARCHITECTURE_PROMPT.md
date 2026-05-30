# callflow-tracer → AgentRuntime: Architecture & Implementation Prompt

> **Document type:** Senior engineer implementation brief  
> **Version:** v1.0  
> **Target:** Evolve `callflow-tracer` from a Python tracing library into a call-aware agent
> runtime with native observability — production-ready, optimized, reliably extensible.

---

## [REFERENCE ARCHITECTURE — OpenClaw]

<!-- ============================================================ -->

OpenClaw
Architecture Document
Senior Developer Reference · v1.0


1. Project Overview


OpenClaw is a local-first personal AI assistant that acts as a single control plane for every messaging platform you already use — running on your own hardware, routing through one gateway, controllable from CLI, macOS, iOS, and Android.


What Problem Does It Solve?
Personal AI assistants are fragmented: you talk to ChatGPT in a browser, Claude in another tab, and nothing reaches you where conversations actually happen — WhatsApp, Telegram, Discord, Slack, iMessage. OpenClaw collapses these into one locally-hosted gateway. You get AI that shows up in your existing channels, uses your device's camera and screen, speaks back to you, and runs automations on a schedule — without any third party holding your conversation history.

Who Is It For?
Power users who want a self-hosted, privacy-respecting assistant across 20+ chat platforms
Developers who need programmable AI hooks embedded into their workspace tools
Teams routing different channels to isolated AI agents with separate memory and model configs

What Makes It Architecturally Interesting?
Hexagonal + Layered + Plugin — 40+ channel adapters plugged into a single normalized gateway without any platform SDK touching the core
In-process plugin safety — lazy-loaded via jiti, fully isolated npm graphs per extension, with dependency conflicts impossible by design
File-backed session state — reentrant OS-level write locks, 45s TTL cache, atomic writes with backup-verify-restore — survives process crashes without a database
Multi-agent routing — a single gateway can serve multiple isolated agents with different models, separate memory, and per-thread binding
Model failover — structured error classification drives auth-profile cooldowns and cascading model fallback automatically

Tech Stack at a Glance
Layer
Technology
Purpose
Language
TypeScript (strict)
End-to-end type safety
Runtime
Node.js
Single-process gateway
CLI framework
Commander.js
Command parsing & dispatch
HTTP server
Express
Webhook ingestion, API routes
Plugin loading
jiti
Lazy-load TypeScript extensions without compile step
Config format
JSON5
Human-friendly config with comments
Testing
Vitest (forks pool)
Process-isolated tests, 70% coverage threshold
Channels (built-in)
grammY, discord.js, @slack/bolt, Baileys, signal-cli, AppleScript
Platform-specific SDKs per adapter
Browser control
CDP (Chrome DevTools Protocol)
Headless browser automation
Voice / TTS
ElevenLabs + system TTS
Speech synthesis with cloud/local fallback
Deployment
Nix, Docker, Tailscale Serve/Funnel, SSH tunnels
Multiple deployment targets



2. Repository Structure
Spend 80% of your time in 
 src/  (core) and  extensions/  (channel plugins). Everything else is scaffolding.

openclaw/
├── src/                    ← Core source — DO NOT import channel SDKs here
│   ├── entry.ts            ← App bootstrap (start here)
│   ├── cli/                ← Commander.js CLI, command registry, DI factory
│   │   ├── run-main.ts     ← Entry point: dotenv + profile loading
│   │   ├── program/        ← Command registration (command-registry.ts)
│   │   └── deps.ts         ← CliDeps factory (dependency injection)
│   ├── commands/           ← Individual command handlers
│   ├── gateway/            ← HTTP server, call handler, outbound routing
│   │   └── server-methods/ ← Route handlers (POST /call, /webhooks/*)
│   ├── routing/            ← Agent/peer/session key resolution
│   │   ├── resolve-route.ts← Strategy pattern: 5 routing strategies
│   │   └── account-id.ts   ← LRU-cached ID normalization
│   ├── agents/             ← LLM integration, auth profiles, model failover
│   │   ├── model-fallback.ts← Failover chain orchestration
│   │   ├── auth-profiles.ts ← Profile cooldown & rotation
│   │   └── session-write-lock.ts ← Reentrant file-based write locks
│   ├── config/             ← Config loading, env substitution, includes, defaults
│   │   ├── config.ts       ← loadConfig() + validation
│   │   ├── paths.ts        ← Config file path resolution
│   │   ├── env-substitution.ts ← ${VAR} processing
│   │   ├── includes.ts     ← $include directive (circular + depth guard)
│   │   └── defaults.ts     ← Model/agent/session defaults
│   ├── channels/           ← Core channel implementations
│   │   ├── telegram/       ← grammY adapter
│   │   ├── discord/        ← discord.js adapter
│   │   ├── slack/          ← @slack/bolt adapter
│   │   ├── signal/         ← signal-cli bridge
│   │   ├── imessage/       ← macOS AppleScript bridge (macOS only!)
│   │   └── web/            ← WhatsApp via Selenium (fragile — see §12)
│   ├── plugins/            ← Plugin registry, jiti loader, runtime
│   ├── plugin-sdk/         ← Public SDK for extensions (~150 exports)
│   ├── acp/                ← Agent Control Protocol runtime sandbox
│   ├── infra/              ← Foundation: env normalization, errors, path
│   └── test-utils/         ← Stub plugins, env helpers
│
├── extensions/             ← 33+ optional channel plugins (one package each)
│   ├── mattermost/         ← Mattermost adapter
│   ├── matrix/             ← Matrix/Element adapter
│   ├── msteams/            ← Microsoft Teams adapter
│   ├── line/               ← LINE adapter
│   ├── irc/                ← IRC adapter
│   ├── nostr/              ← Nostr decentralized adapter
│   ├── twitch/             ← Twitch chat adapter
│   └── voice-call/         ← WebRTC voice + transcription
│
├── docs/                   ← Mintlify documentation (no .md in links)
│   ├── channels/           ← Per-channel docs
│   └── reference/          ← API reference
│
├── test/                   ← Global test setup
│   ├── setup.ts            ← Vitest init (HOME isolation, fake timer guard)
│   └── test-env.ts         ← Temp HOME + credential clearing
│
├── vitest.config.ts        ← Test config (forks pool, coverage thresholds)
├── package.json            ← Root deps only; channel SDKs live in extensions/
├── CLAUDE.md               ← Project guidelines (read this first!)
└── .github/
    ├── labeler.yml         ← Auto-labels PRs by file path
    └── workflows/          ← CI/CD




Non-obvious naming: extensions/ are not optional extras — they are fully independent npm packages with their own node_modules. The root package.json deliberately contains no channel-platform SDKs. src/channels/ contains the 6 built-in channels that ship with the core binary.



3. High-Level Architecture
OpenClaw uses a 
Layered + Hexagonal (Ports & Adapters) + Plugin architecture. The hexagonal core (gateway) is completely independent of all 40+ messaging platform SDKs. Platform adapters are injected as plugins. The layer hierarchy is strictly enforced: higher layers import from lower, never the reverse.

The 5 Dependency Layers
Layer
Path
Responsibility
Imports From
5 — CLI & Commands
src/cli/, src/commands/
User interface, command parsing & dispatch
Layer 4
4 — Business Logic
src/gateway/, src/routing/, src/agents/
Message routing, LLM calls, session management, auth
Layers 1–3
3 — Integration & Adapters
extensions/*/, src/channels/
40+ channel plugins, platform-specific parsing/delivery
Platform SDKs, Layers 1–2
2 — Utilities
src/config/, src/logging/, src/daemon/
Config loading, DI, logging, hooks
Layer 1 only
1 — Foundation
src/infra/, npm deps
Env normalization, runtime guards, error handling
node: only




Critical rule: Higher layers may import from lower, but NEVER the reverse. Extensions MUST NOT import from src/cli. This enables gateway to run without the CLI and plugins to load without coupling to command-line UI.


Architecture Diagram
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL MESSAGING                         │
│  WhatsApp │ Telegram │ Discord │ Slack │ Signal │ 15+ more   │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTPS Webhook / WebSocket / Polling
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              GATEWAY  (ws://127.0.0.1:18789)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ HTTP Server (Express)                                 │   │
│  │  POST /call · /webhooks/{channel} · /sessions        │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ Router & Session Resolver                             │   │
│  │  signature verify → normalize → sessionKey → agent   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ Rate Limit · Dedup · keyed-async-queue per session    │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ Agent Executor                                        │   │
│  │  load session (45s TTL) → load config → load plugins │   │
│  │  → Pi agent runtime → model fallover → stream deltas │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ Outbound Adapters                                     │   │
│  │  channel-specific send (direct or gateway mode)       │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ State Persistence                                     │   │
│  │  write lock → load fresh → atomic write → release    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Config: ~/.openclaw/openclaw.json                          │
│  Session: ~/.openclaw/sessions/{agentId}/*.json             │
│  Plugins: ./extensions/* + ~/.openclaw/plugins/*            │
└─────────────────────────┬────────────────────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          ▼                                 ▼
  ┌────────────────┐             ┌────────────────────────┐
  │  AI MODELS     │             │  CLIENTS               │
  │  OpenAI        │             │  CLI (openclaw ...)     │
  │  Anthropic     │             │  macOS App (menu bar)  │
  │  Google Gemini │             │  iOS Node (canvas)     │
  │  20+ others    │             │  Android Node (voice)  │
  └────────────────┘             └────────────────────────┘


Why This Architecture?
Decision
Tradeoff
Why
Hexagonal core
More abstraction layers
Gateway testable without any real channel SDK; swap WhatsApp library without touching business logic
Plugin/lazy loading
First call slightly slower
40+ platform SDKs coexist without startup bloat or npm conflicts
In-process plugins
Plugin crash = gateway crash
No IPC overhead; plugins access gateway context via AsyncLocalStorage
File-based session locks
Slower than in-memory mutex
Survives process crashes; PID + starttime check defeats PID recycling
Single-user local-first
No multi-device sync
Simplified auth, no backend dependency, full user control of data
Strict layer rule
More boilerplate
Gateway runs without CLI; channel adapters run without routing logic



4. Core Modules Breakdown
4.1 Gateway (src/gateway/)
The central HTTP hub — every inbound webhook and every outbound response passes through here.

Key files:
 server-methods/  — request handlers for POST /call and /webhooks/{channel}

Responsibilities:
Receive webhook POSTs from all channel platforms
Authenticate inbound requests (gateway.auth.token / gateway.auth.password)
Dispatch to Router, then to Agent Executor
Coordinate outbound delivery via channel adapters
Serve Control UI, WebChat, and WebSocket clients

Dependencies: src/routing/, src/agents/, src/channels/ (via adapters, not direct SDK imports)

Gotcha: Gateway deliberately does not import any platform SDK. All channel access goes through the ChannelPlugin interface.

4.2 Routing (src/routing/)
Translates an inbound message into a (agentId, sessionKey) pair, applying five layered resolution strategies.

Key files:
 resolve-route.ts  — Strategy pattern: peer / guild / team / account / default
 session-key.ts  — Session key format and parsing
 account-id.ts  — LRU-cached ID normalization (lowercase, trim, dedup special chars)

Session key format:
agent:{agentId}:{scope}:{peerId}[:{extra}]

Examples:
  agent:main:user:15551234567          # WhatsApp DM
  agent:coding:slack:C123456:user      # Slack channel + user
  agent:bot:telegram:-987654321:42     # Telegram group + topic


Resolution precedence (highest to lowest):
Explicit agentId override
ACP thread binding (persisted in ~/.openclaw/acp-bindings.json)
Manual routing rules (config.routing[])
Parsed from sessionKey
Default agent (fallback)

Gotcha: Missing any component of the session key (threadId, accountId, peerId) routes to the wrong session. ID normalization must stay canonical.

4.3 Agents (src/agents/)
Manages LLM execution including auth profile selection, model failover, session write locking, and tool policy enforcement.

Key files:
 model-fallback.ts  — Failover chain: try primary model → all auth profiles → fallback models
 auth-profiles.ts  — Profile store with cooldown state (10s auth, 5min rate_limit, 1hr billing)
 session-write-lock.ts  — Reentrant OS-level file lock with PID+starttime guard and watchdog cleanup
 bash-tools.ts  — Shell command execution with sandbox policy

Model failover classification:
Error Type
HTTP Status
Cooldown
Recovery
auth
401
10 seconds
Try next auth profile for same model
auth_permanent
403
None (never retry)
Fail immediately
rate_limit
429
1s → 2s → 4s → ... → 5min (exponential)
Retry with backoff
billing
402
1 hour
Try cheaper model
overloaded
503
Exponential backoff
Retry
timeout
—
None
Extend timeout + retry
model_not_found
404
None
Try fallback model


Gotcha: Always use updateSessionStore() to modify sessions — it owns the lock acquire/release lifecycle. Calling acquireSessionWriteLock() directly risks holding the lock forever if an error is thrown before release.

4.4 Config (src/config/)
Loads, validates, and resolves the openclaw.json config through a 12-step pipeline before any gateway component sees it.

Key files:
 config.ts  — loadConfig(): entry point for config loading + schema validation
 env-substitution.ts  — ${VAR} substitution; only uppercase names substituted; $${VAR} escapes to literal
 includes.ts  — $include directives with path-traversal prevention, circular detection, max depth 10
 defaults.ts  — Applies model/agent/session/compaction defaults in a fixed order

Config loading pipeline (12 steps):
Parse CLI arguments and --profile flag
Set OPENCLAW_STATE_DIR, OPENCLAW_CONFIG_PATH from profile
Load .env files (CWD first, then ~/.openclaw/.env as fallback)
Normalize runtime environment
Resolve config file path (search order: OPENCLAW_CONFIG_PATH → legacy dirs → default)
Parse JSON5
Resolve $include directives
Substitute ${VAR} references from process.env
Apply defaults (messages → session → logging → models → agents → compaction)
Validate schema (with plugin-contributed schemas)
Apply config.env.vars to process.env (non-destructive)
Cache runtime snapshot for write operations

4.5 Plugin System (src/plugins/)
Discovers, lazy-loads, and registers all channel adapters, CLI commands, HTTP routes, and hooks without loading any code at startup.

Key files:
 loader.ts  — jiti-based lazy loader; calls register(api) on first use
 runtime.ts  — Plugin registry: tracks enabled/disabled, loaded/error state, all registered artifacts
 cli.ts  — CLI command registration and conflict resolution (built-in wins on name collision)

Discovery order:
 ./extensions/*  — bundled built-in plugins
 ~/.openclaw/plugins/*  — user-installed plugins
 config.plugins[]  — config-specified paths

Gotcha: Plugin load failures are logged as warnings and the gateway starts in degraded mode — it does NOT abort. Test plugin load paths explicitly.

4.6 Channel Plugins (extensions/*)
Each channel is an independent npm package implementing the ChannelPlugin interface: a config adapter, an outbound adapter, and optionally an inbound (webhook) adapter.

Standard plugin structure:
extensions/{channel}/
├── src/
│   ├── index.ts       # exports async function register(api)
│   ├── channel.ts     # ChannelPlugin implementation
│   ├── config.ts      # Config schema helpers
│   └── outbound.ts    # Send adapters (text, media)
└── package.json       # Platform SDK deps only — NOT in root package.json


Delivery modes:
direct — Gateway calls platform REST API directly. Low latency. Used by Telegram, Discord, Slack, Signal.
gateway — Gateway forwards to a paired iOS/Android node, which sends via its local environment. Enables native iMessage and Android SMS.

4.7 Session Store (src/config/sessions.ts)
Repository-pattern abstraction over per-session JSON files, with 4-layer state management: in-memory → cache → write-lock → disk.

File location: ~/.openclaw/sessions/{agentId}/{normalized-session-key}.json
Cache TTL: 45 seconds with mtime + file-size invalidation
Write pattern: backup → write → read-back-verify → delete backup (restore on failure)
Rotation threshold: 10 MB — renames to .bak.{timestamp}, keeps 3 newest
Watchdog: Scans every 60s, force-releases locks held > ~2.5 minutes

Gotcha: Windows uses Atomics.wait(50ms) × 3 retries for atomic write lock — synchronous, blocks event loop for up to 150ms on contention.


5. Data Models & Entities
Core Entities
Entity
Represents
Key Fields
Lifecycle
Message
A normalized inbound message from any channel
channel, sender, peerId, text, media[], threadId, messageId, timestamp
Created on webhook receipt; passed to router; discarded after session update
Session
One conversation context between a user and an agent
sessionKey, messages[], totalTokens, updatedAt, agentId
Created on first message; appended on each turn; compacted at 30M chars; rotated at 10MB
Agent
A configured AI agent instance with its own memory and model
id, default, workspace, model.primary, model.fallbacks[], skills
Loaded from config; persists in ~/.openclaw/agents/{id}/
AuthProfile
LLM provider credentials with usage/cooldown state
id, provider, apiKey/token, cooldownUntil, failureCount, lastUsedAt
Loaded from auth-profiles.json; updated on each API call; persists cooldowns across restarts
ChannelPlugin
An adapter binding a messaging platform to the gateway
id, meta, capabilities, config adapter, outbound adapter
Discovered at startup; lazy-loaded on first use; persists for gateway lifetime
SessionWriteLock
OS-level exclusive write guard for one session file
pid, starttime, reentrantCount, maxHoldMs
Acquired before session load; released after atomic write; watchdog cleans stale locks
OpenClawConfig
The complete resolved configuration tree
agents, channels, routing, gateway, env, plugins
Loaded once at startup; cached snapshot for write operations; runtime overrides ephemeral
ResolvedAgentRoute
The routing decision for one inbound message
agentId, sessionKey, matchedBy
Computed per message by resolve-route.ts; not persisted
ACPBinding
A persistent per-thread agent routing override
channelKey, agentId, type (thread_binding | topic_binding)
Stored in acp-bindings.json; overrides config routing rules


Entity Relationships
OpenClawConfig
  ├── agents[]             ← One or more Agent configs
  ├── channels             ← Per-channel account configs
  └── routing[]            ← Manual routing overrides

Agent
  ├── has many Session     (one per unique session key)
  ├── has many AuthProfile (stored in agent workspace)
  └── has one workspace dir

Message
  ├── belongs to Channel   (via channel field)
  ├── resolves to Session  (via routing → sessionKey)
  └── resolves to Agent    (via routing → agentId)

Session
  ├── protected by SessionWriteLock  (one lock per session file)
  ├── cached in L3 Cache             (45s TTL, mtime/size invalidated)
  └── persisted to disk              (atomic write pattern)

ACPBinding
  └── overrides routing for Session   (highest priority in resolve-route)



6. Core Data Flows
Flow 1: Inbound Message → AI Response (Telegram Example)


This is the primary flow every message in the system follows. Understand this and you understand 80% of OpenClaw.


[Telegram] User sends message → Telegram pushes webhook POST /webhooks/telegram?accountId=default
[Channel Adapter] Verify HMAC-SHA256 signature with bot token
[Channel Adapter] Parse platform payload → normalized Message{ channel, sender, text, peerId, threadId, ... }
[Router] Check ACP binding → check manual routing rules → resolve defaultAgentId → derive sessionKey
[Rate Limiter] Check bucket[accountId]; if full return 429 with retry-after
[Dedup] Drop if duplicate messageId already processed (handles Telegram double-webhook edge case)
[Queue] Enqueue to keyedAsyncQueue(sessionKey) — ensures per-session ordering
[Agent Executor] Acquire session write lock (reentrant, 30s timeout)
[Session Store] Load session (cache hit if mtime+size unchanged, else disk read)
[Config] Load agent config for resolved agentId; apply defaults
[Plugins] jiti lazy-load required plugins; call before-agent-start hooks
[Model Failover] Select primary model + first non-cooldown auth profile; begin Pi agent runtime
[Pi Agent] Stream tokens from LLM; execute tools (memory_search, system.run, etc.) as needed
[Session Store] Append turn (user message + assistant response + tool calls); atomic write; release lock
[Outbound Adapter] Resolve account credentials; format message; POST to Telegram Bot API
[Telegram] Message delivered to user. Duration: ~3s (2s LLM + 0.5s I/O + 0.5s overhead)

Flow 2: Model Failover on Rate Limit
[Agent Executor] First LLM call returns HTTP 429
[Error Classifier] Classify as rate_limit; set 1s cooldown on current auth profile
[Model Failover] Try next auth profile for same model (if any)
[Model Failover] All profiles for primary model cooldowned → try fallback model
[Model Failover] Same profile selection logic applies for fallback model
[Model Failover] All models and profiles exhausted → return bounded error: 'All models failed (N): ...'
[Auth Profiles] Cooldown state persisted to auth-profiles.json; next gateway restart respects cooldowns

Flow 3: Config Load at Gateway Start
[CLI] Parse --profile=X → set OPENCLAW_STATE_DIR and port overrides
[infra/dotenv] Load .env from CWD, then ~/.openclaw/.env as fallback
[config/paths] Resolve config file: OPENCLAW_CONFIG_PATH → existing legacy files → default
[config/includes] Resolve $include directives with circular + depth guard
[config/env-substitution] Substitute ${UPPERCASE_VAR} from process.env; error on missing vars in strict mode
[config/defaults] Apply defaults in order: messages → session → logging → models → agents → compaction
[plugins] Validate schema with plugin-contributed config extensions
[config] Apply config.env.vars to process.env (non-destructive; shell env wins)
[config] Cache runtime snapshot for future write operations


7. Key Design Patterns
Pattern
Where Used
Why Chosen
Concrete Example
Hexagonal (Ports & Adapters)
Gateway ↔ Channel plugins
Keeps gateway testable without platform SDKs; swap WhatsApp library transparently
ChannelPlugin interface — gateway calls outbound.sendText(), never imports Baileys directly
Strategy
src/routing/resolve-route.ts
Multiple routing strategies (peer, guild, team, account, default) selectable at runtime
resolveSessionAgentIds() tries strategies in precedence order, returning first match
Adapter
extensions/*/
Each channel adapts platform SDK payload to normalized Message type
extensions/telegram/ wraps grammY update → Message{ channel, sender, text, ... }
Plugin + Lazy Loading
src/plugins/loader.ts via jiti
40+ independent plugins without startup bloat; each loads only when its channel is used
jiti dynamically imports extensions/mattermost/ only when first Mattermost webhook arrives
Factory
src/cli/deps.ts
Creates CLI dependencies, enables dependency injection and isolated testing
createCliDeps() returns { sendMessageTelegram, sendMessageDiscord, ... } injectable into commands
Repository
src/config/sessions.ts
Abstracts session persistence from business logic; cache and lock transparent to callers
updateSessionStore(sessionKey, fn) — callers modify session via callback; lock/cache/write hidden
Observer / Hooks
src/hooks/
Extensibility without coupling; plugins react to events without gateway knowing about them
before-tool-call hook: memory plugin indexes every tool call transparently
LRU Cache
src/routing/account-id.ts
Normalize untrusted IDs with bounded memory consumption
Normalize +1 (555) 123-4567 → 15551234567; LRU prevents unbounded growth from unique IDs
Null Object
DEFAULT_AGENT_ID, DEFAULT_ACCOUNT_ID
Avoid null checks throughout routing; always have a valid fallback
If no agent configured with default=true, DEFAULT_AGENT_ID ('main') used — no crash
Template Method
Channel inbound flow
All 40+ channels follow identical: parse → verify → normalize → route → format → send
Every channel plugin implements receive(payload) returning Message — same pipeline every time



8. External Integrations & Dependencies
Name
Purpose
Where Used
Notes
grammY
Telegram bot
src/channels/telegram/
Long-polling OR webhook mode
discord.js
Discord bot
src/channels/discord/
WebSocket real-time; Ed25519 webhook verification
@slack/bolt
Slack bot
src/channels/slack/
Socket Mode; HMAC timestamp+body verification
Baileys
WhatsApp (Baileys)
extensions/baileys/ or core whatsapp
Maintains WhatsApp Web session; community library (no official API)
signal-cli
Signal messenger
src/channels/signal/
Requires local signal-cli installation as sidecar
AppleScript / BlueBubbles
iMessage
src/channels/imessage/
macOS-only; echo-loop hardening required
Selenium / CDP
WhatsApp Web automation
src/channels/web/
Headless browser; fragile to UI changes (see §12)
jiti
TypeScript lazy loading
src/plugins/loader.ts
Loads extensions on-demand without pre-compile
Commander.js
CLI framework
src/cli/
Command parsing; plugins register via API, not directly
Express
HTTP server
src/gateway/
Webhook endpoints + static Control UI
ElevenLabs
TTS / voice synthesis
Voice features
Fallback to system TTS if unavailable
Tailscale
Secure remote access
Deployment
Serve (tailnet) or Funnel (public HTTPS) modes
OpenAI API
LLM provider
src/agents/
Auth profile rotation + exponential backoff
Anthropic API
LLM provider
src/agents/
claude-opus-4-6 default alias 'opus'
Google Gemini API
LLM provider
src/agents/
CLI auth; model alias 'gemini'
HashiCorp Vault
Secret management
src/config/ secrets
Optional VAULT provider; token-based auth
Vitest
Test framework
test/ + src/**/*.test.ts
Forks pool; 70% coverage threshold
Mintlify
Documentation
docs/
No trailing .md in links


How External Failures Are Handled
LLM providers: Classified error codes → per-profile cooldowns → model fallback chain → bounded error message
Channel webhooks: Signature verification failure returns 401; payload parse failure logged and dropped
Plugin load failures: Logged as warning; gateway starts in degraded mode (not crashed)
Secret resolution: Concurrent provider calls with limits (4 concurrent, 512 refs max, 256KB batch)
Session write failures: Backup restored; error surfaced to caller; session lock released


9. Configuration & Environment
Config File
Primary file:  ~/.openclaw/openclaw.json  (JSON5 format — supports comments)

Search order for config file:
 OPENCLAW_CONFIG_PATH  environment variable (explicit override, highest priority)
Existing files in default state dirs: openclaw.json, clawdbot.json, moldbot.json
State dir resolution: prefer ~/.openclaw, then legacy ~/.clawdbot or ~/.moldbot
 ~/.openclaw/openclaw.json  as final fallback

Environment Variable Substitution
// In openclaw.json:
"apiKey": "${ANTHROPIC_API_KEY}"   // Substituted from process.env
"literal": "$${NOT_SUBSTITUTED}"   // Double-$ escapes to ${NOT_SUBSTITUTED}
"ignored": "${my_lower_var}"       // lowercase names NOT substituted


Strict mode (default): throws MissingEnvVarError if variable undefined or empty
Lenient mode: emits warning, preserves placeholder as ${VAR}

CLI Profiles
Profile
State Dir
Config File
Port
default
~/.openclaw/
~/.openclaw/openclaw.json
18789
dev (--dev flag)
~/.openclaw-dev/
~/.openclaw-dev/openclaw.json
19001
custom (--profile=staging)
~/.openclaw-staging/
~/.openclaw-staging/openclaw.json
18789




Profile names accept only letters, numbers, underscores, and hyphens. Setting --dev is shorthand for --profile=dev with a different default port.


Key Configuration Sections
Config Key
Required?
Description
agents.list[]
Yes
Array of agent configs: id, default, workspace, model.primary, model.fallbacks[]
channels.telegram / discord / slack / ...
Per channel
Account tokens, webhook secrets, allowFrom lists
gateway.auth.token
Recommended
Bearer token for gateway WebSocket auth
gateway.tailscale.mode
Optional
serve | funnel — enables Tailscale integration
routing[]
Optional
Manual routing rules: match(channel, chatId) → route(agentId)
agents.defaults.sandbox.mode
Optional
non-main — runs group/channel sessions in Docker sandboxes
env.vars
Optional
Set process.env vars from config (non-destructive; shell env wins)
plugins[]
Optional
Additional plugin paths beyond ./extensions/* and ~/.openclaw/plugins/*


Environment Precedence (Highest to Lowest)
Shell environment (export VAR=value)
Process.env at startup
.env in process CWD
~/.openclaw/.env (global fallback)
config.env.vars (from config file)
Hardcoded defaults in source code


10. Testing Architecture
Test Types & Locations
Type
Pattern
Description
Run By Default?
Unit
src/**/*.test.ts
Colocated with source; mocked dependencies
Yes
E2E
src/**/*.e2e.test.ts, test/**.e2e.test.ts
Integration scenarios with mock LLM backends
No (separate command)
Integration E2E
*.integration.e2e.test.ts
Subset of E2E with deeper integration focus
No
Live
*.live.test.ts
Real LLM provider calls; requires LIVE=1 flag
No (opt-in only)
Compat
*.compat.e2e.test.ts
Model discovery and compatibility checks
No
Plugin tests
extensions/**/*.test.ts
Per-plugin unit tests
Yes


Framework & Configuration
Framework: Vitest with V8 coverage
Pool mode: forks — each test worker isolated in a separate process; no cross-test global state
Worker limits: 4–16 local, 2–3 CI
Coverage thresholds: 70% lines/functions/statements, 55% branches
Test timeout: 120s default, 180s on Windows

Test Isolation Pattern
Every test run creates an isolated HOME directory to prevent accidental reads from the real ~/.openclaw config:
// test/test-env.ts
withIsolatedTestHome()
  → creates /tmp/openclaw-test-home-{random}/
  → sets HOME, USERPROFILE, XDG_*, OPENCLAW_* to temp dir
  → clears sensitive env vars (tokens, keys) in non-live mode
  → restores everything and removes temp dir on teardown

// test/setup.ts (runs before all tests)
process.setMaxListeners(128)  // Prevents MaxListeners warnings in forks
VITEST=true                   // Enables test mode in runtime guards


Running Tests
# Default suite (unit + integration, no E2E, no live)
pnpm test

# With coverage report
pnpm test:coverage

# E2E tests only
pnpm test --run src/**/*.e2e.test.ts

# Live tests (requires real API credentials)
LIVE=1 pnpm test:live
CLAWDBOT_LIVE_TEST=1 pnpm test:live

# Docker-based live tests
pnpm test:docker:live-models       # LLM provider integration
pnpm test:docker:live-gateway      # Full gateway + channels

# Resource-constrained (CI or low memory)
OPENCLAW_TEST_PROFILE=low OPENCLAW_TEST_SERIAL_GATEWAY=1 pnpm test


What Is Well-Tested vs Blind Spots
Area
Coverage Level
Notes
Session write locking (reentrant, watchdog, stale)
Good
Dedicated unit tests with mock PIDs, temp lock files, signal handlers
Model failover and auth profile cooldown
Good
E2E tests with mock runners testing all error classification paths
Config loading pipeline
Good
Covers env substitution, includes, defaults, profile resolution
Channel webhook signature verification
Partial
Cannot be stubbed — must use real signatures in E2E tests; gaps exist
iMessage (macOS-only)
Partial
Requires real macOS device; simulators cannot test iMessage
WhatsApp Web (Selenium)
Partial
Fragile to WhatsApp UI changes; browser element selectors break silently
Concurrent session writes
Partial
Lock unit tests exist but stress-test coverage for race conditions is sparse
Plugin load/unload cycles
Gap
Plugin HTTP route collision handling not stress-tested
Windows file I/O timing
Gap
180s timeout accommodates Windows but race conditions under heavy load untested



11. Extension Guide — How to Add Something New
Adding a New CLI Command
Register the command in  src/cli/program/command-registry.ts :
const coreEntries: CoreCliEntry[] = [
  // ... existing entries ...
  {
    commands: [{ name: 'mycommand', description: 'My command', hasSubcommands: false }],
    register: async ({ program }) => {
      const mod = await import('../mycommand-cli.js');
      mod.registerMyCommandCli(program);
    },
  },
];

Implement the handler in  src/cli/mycommand-cli.ts :
import type { Command } from 'commander';

export function registerMyCommandCli(program: Command) {
  program
    .command('mycommand')
    .description('My new command')
    .option('--flag', 'A flag')
    .action(async (options) => {
      // implementation
    });
}

Load config if needed: import loadValidatedConfigForPluginRegistration() from src/program/register.subclis.js
Write tests colocated as  mycommand-cli.test.ts 

Adding a New Channel Plugin
Create the extension package: mkdir extensions/myplugin && create package.json with platform SDK deps only
Implement the register function: extensions/myplugin/src/index.ts
import type { OpenClawPluginApi } from 'openclaw/plugin-sdk';

export async function register(api: OpenClawPluginApi) {
  api.registerChannel('myplugin', {
    meta: { id: 'myplugin', label: 'My Plugin', docsPath: '/channels/myplugin', blurb: '...' },
    capabilities: { chatTypes: ['direct', 'group'] },
    config: {
      listAccountIds: (cfg) => Object.keys(cfg.channels?.myplugin?.accounts ?? {}),
      resolveAccount: (cfg, accountId) => cfg.channels.myplugin.accounts[accountId ?? 'default'],
      isConfigured: async (account) => Boolean(account?.token),
    },
    outbound: {
      deliveryMode: 'direct',
      sendText: async ({ deps, to, text }) => {
        // Call your platform API
        return { channel: 'myplugin', messageId: '...' };
      },
      sendMedia: async ({ deps, to, text, mediaUrl }) => { /* ... */ },
    },
  });
}

Add webhook handler if the channel pushes inbound messages: implement api.registerChannel's inbound adapter
Update labeler: add entry to .github/labeler.yml
Create docs: docs/channels/myplugin.md

Adding a New Agent
Add to openclaw.json: agents.list[] with a unique id, workspace dir, and model config
Configure routing: either add a routing rule (match channel/chatId → route agentId) or bind a thread via ACP
Optional sandbox: set agents.defaults.sandbox.mode: 'non-main' to run non-main sessions in Docker


12. Known Risks & Technical Debt
Most Fragile Parts
Area
Risk Level
Why It's Fragile
Mitigation
WhatsApp Web (Selenium)
High
No official API; uses headless browser automation; breaks when WhatsApp updates its web UI
Tab lifecycle management; consider WhatsApp Business API migration
iMessage (macOS AppleScript)
High
macOS-only; requires real device; echo-loop required multiple hardening iterations
Test only on real macOS; never assume simulator coverage
Session write lock reentrance
Medium-High
Forgetting to release lock leaves it held until watchdog cleanup (up to 2.5 min)
Always use updateSessionStore() — never call acquireSessionWriteLock() directly
Plugin trust boundary
Medium
Plugins run in-process with gateway privileges; malicious plugin = compromised gateway
Audit plugins before install; plugins.allow list pins trusted IDs
Config schema serialization
Medium
High-cardinality plugin metadata triggers RangeError: Invalid string length
Fixed via incremental hashing (#36603); re-test after new plugins with large schemas
Subagent completion announces
Medium
Late subagent-complete events after kill marker silently dropped; routing to wrong channel
Hard to test; monitor logs for completion delivery failures
Windows atomic write
Medium
Atomics.wait(50ms) × 3 = up to 150ms synchronous event-loop block on high contention
Avoid network shares for ~/.openclaw; longer CI timeouts on Windows
Markdown parser in Control UI
Low-Medium
marked.parse() crashes on malformed recursive structures; now has fallback, but brittle
Test with edge-case content from channels


Known Technical Debt
Platform-specific branches: ~20+ platform-specific code paths (macOS iMessage, Windows file locking, Linux systemd, Android SMS). Every refactor risks platform-specific regressions.
Model provider parity: 20+ LLM providers with different tool calling conventions, streaming semantics, and error formats. Adding a new provider touches auth, models.json, tool calling, streaming, cost tracking.
Webhook signature per channel: 30+ channels, each with a unique signing scheme. Cannot stub in integration tests — must use real signatures. Any regression here = spoofed webhook attack surface.
Compaction + rotation race: Session store compaction (message pruning) runs concurrent with file rotation. No lock held during LLM call; file could be renamed while compaction reads it.

Files to Edit with Extra Care
File
Why Dangerous
src/agents/session-write-lock.ts
Core concurrency primitive. Bugs here cause session corruption or forever deadlocks.
src/routing/resolve-route.ts
Wrong routing = messages going to wrong agent/session. Bugs are silent — no crash.
src/config/env-substitution.ts
Substitution bugs can expose literal ${VAR} placeholders as credentials or silently skip keys.
src/config/includes.ts
Path traversal prevention and circular detection. Security boundary for config includes.
src/plugins/loader.ts
Plugin loading failure mode is degraded start (no crash). Bugs here create silent missing capabilities.
extensions/*/src/index.ts (each channel)
Webhook signature verification code. Bugs here create spoofing vulnerability.
src/agents/model-fallback.ts
Incorrect error classification can set wrong cooldown durations, causing 1-hour outages on billing errors.


Known Workarounds & TODOs
WhatsApp Web Selenium: session cleanup must explicitly close tracked browser tabs — left open = unbounded memory growth (#36666)
Slack sends both app_mention and message events for the same user mention — deduplication on ts timestamp prevents double-replies
Telegram socket stale-restart guard required to prevent misclassification of reconnect events (#38464)
iMessage echo-loop: internal gateway messages must be filtered to prevent the bot replying to its own sends — requires cache text retention (#33295)
xAI/Grok returns HTML-entity-encoded tool call arguments — must decode before parsing (#35276)
Config schema merging uses incremental hashing after RangeError crash with high-cardinality metadata (#36603)


13. Glossary
Term
Definition
A2UI
Agent-to-UI — protocol for agents to control the Live Canvas (canvas.push, canvas.reset, canvas.eval)
ACP
Agent Control Protocol — runtime sandbox for tool execution; also used for thread bindings that persist agent routing
ACP Binding
A persisted per-thread agent routing override stored in ~/.openclaw/acp-bindings.json. Takes precedence over all routing rules.
Auth Profile
A set of LLM provider credentials with usage stats and cooldown state. Multiple profiles per provider enable failover.
Baileys
Open-source Node.js WhatsApp Web API library used for the WhatsApp channel (no official WhatsApp API)
ChannelPlugin
The interface every channel adapter implements: config adapter + outbound adapter + optional inbound adapter
CDP
Chrome DevTools Protocol — used for headless browser control in the browser tool
ClawHub
Centralized skills registry for managed skills (installable via agent or CLI)
CliDeps
The dependency injection factory type (CliDeps) that carries channel send functions into CLI commands — enables testing without real channel connections
Compaction
The process of summarizing old session turns to keep session size under 30M chars without losing context
DEFAULT_AGENT_ID
The string 'main' — used as agent ID when no agent is configured as default. Null Object pattern.
DEFAULT_ACCOUNT_ID
The string 'default' — used as account ID when no specific account is specified in a channel config
Delivery Mode
'direct' (gateway REST calls) or 'gateway' (forwards to iOS/Android node for local send)
DM Pairing
Security feature: unknown DM senders receive a pairing code before their messages are processed
Extensions
The 33+ optional channel plugins in extensions/; each is an independent npm package with isolated dependencies
Gateway
The central WebSocket/HTTP server (ws://127.0.0.1:18789) that routes all messages, manages sessions, and runs tools
Group Session
A session isolated to a group/channel context (vs. main session which is 1:1 direct chat)
jiti
JavaScript/TypeScript interpreter used for lazy-loading extension plugins without a compile step
Keyhole Async Queue
Per-session message queue ensuring ordered processing — same session key = same queue = sequential processing
Layer (1–5)
The strict dependency layers in OpenClaw's architecture. Higher numbers can import from lower; never the reverse.
Main Session
The primary 1:1 direct-chat session with the assistant (agent:main:user:{id})
Model Alias
Short names for models: 'opus' → claude-opus-4-6, 'gpt' → gpt-5.4, 'gemini' → gemini-3.1-pro-preview
Node
A companion device (macOS, iOS, Android) paired to the gateway, exposing local hardware capabilities
Null Object Pattern
Using DEFAULT_AGENT_ID and DEFAULT_ACCOUNT_ID instead of null, avoiding null checks throughout routing code
Pi Agent
The embedded LLM agent runtime that executes inside the same process as the gateway (vs. external subprocess)
Plugin Registry
The runtime catalog of all loaded plugins: channels, CLI commands, hooks, tools, HTTP routes
Profile (CLI)
A named environment configuration (--profile=dev) with its own state directory, config file, and port
Secret Ref
A config value format $ref:source:provider:id that resolves credentials at runtime from ENV, FILE, EXEC, or VAULT
Session
One conversation context between a user (identified by sender+peer) and an agent. Persisted as a JSON file.
Session Key
Composite identifier: agent:{agentId}:{scope}:{peerId}[:{extra}]. Uniquely identifies one conversation.
Session Write Lock
An OS-level reentrant file lock (.json.lock) preventing concurrent writes to the same session file
Skills
Bundled sets of tools, prompts, and behaviors. Three types: bundled (pre-installed), managed (ClawHub), workspace (custom)
Tailscale Serve/Funnel
Tailscale modes for exposing the gateway: Serve = tailnet-only HTTPS, Funnel = public HTTPS
Template Method Pattern
The consistent channel flow: parse → verify signature → normalize → route → format → send, implemented identically across all 40+ channels
Watchdog
Background task running every 60s that force-releases write locks held longer than maxHoldMs (~2.5 min)
Workspace
The directory for an agent's persistent state: ~/.openclaw/agents/{agentId}/ containing sessions, auth profiles, and tools



<!--                                                              -->
<!-- Use it as structural inspiration for:                        -->
<!--   - Hexagonal (Ports & Adapters) core isolation              -->
<!--   - Strict 5-layer dependency hierarchy                      -->
<!--   - Plugin lazy-loading with isolated dependency graphs      -->
<!--   - File-backed session state with reentrant write locks     -->
<!--   - Model failover with per-profile cooldown classification  -->
<!--   - Watchdog cleanup for stale resource holders              -->
<!--   - Template Method pattern across all adapters              -->
<!--   - Null Object fallbacks to avoid null propagation          -->
<!--                                                              -->
<!-- Adapt intelligently — do not copy. OpenClaw is TypeScript /  -->
<!-- multi-channel messaging. callflow-tracer is Python /         -->
<!-- execution tracing. The PATTERNS transfer; the code does not. -->
<!-- ============================================================ -->

---

## Implementation Prompt

**Role:** You are a senior software architect, Python internals expert, and agent framework
engineer. Your job is to execute the following implementation brief exactly as written.
Be specific, technical, and opinionated. Every decision must be justified. Flag breaking
changes. Produce working Python code, not pseudocode.

---

### Context: What callflow-tracer Is Today

`callflow-tracer` is a production Python library (PyPI: `callflow-tracer`) that instruments
function call graphs via `sys.settrace`. Current capabilities:

| Layer | Modules | Status |
|---|---|---|
| Core tracing | `core/tracer.py`, `core/async_tracer.py` | Solid; minimal deps |
| Auto-instrumentation | `core/auto_instrumentation.py` | Works; no abstraction |
| Plugin system | `core/plugin_system.py` | Exists; underused |
| Visualization | `visualization/` (flamegraph, comparison, jupyter, exporter) | Good |
| Analysis | `analysis/` (code_quality, code_churn, anomaly_detection, predictive_analysis) | Good |
| Observability | `observability/` (OTel export, custom_metrics, SLO/SLI) | Partial |
| AI modules | `ai/` (23 files: LLM providers, root cause, summarizer, etc.) | Feature-rich, fragmented |
| Integrations | `integrations/` (FastAPI, Flask, Django, SQLAlchemy, psycopg2) | Works; no common base |
| CLI | `command_line/main.py` (1464 lines, monolithic) | Functional; too large |
| Benchmark | `benchmark/` | Isolated; good |
| Funnel | `funnel/` | Isolated; good |

**Public API entry point:** `callflow_tracer/__init__.py` re-exports from all domain packages.

**Core data flow (existing):**
```
@trace decorator / trace_scope() context manager
  → CallTracer.start() → sys.settrace(tracer._trace_calls)
  → Python fires (frame, "call", arg) on each function entry
  → _trace_calls extracts caller/callee from frame stack
  → on "return": duration recorded
  → record_traced_call() → CallGraph.add_node() + .add_edge() + CallNode.add_call()
  → CallGraph.to_dict() → export_html() / export_json() / OTel export
```

**Key classes:**
- `CallNode` — per-function metadata (call_count, total_time, avg_time, args_sample)
- `CallEdge` — directed caller→callee relationship with call count
- `CallGraph` — DAG of nodes + edges; `to_dict()` is the serialization boundary
- `CallTracer` — `sys.settrace` lifecycle manager; thread-local + module-global fallback

---

### Phase 1 — Codebase Analysis

Before writing any new code, perform a full audit. For every module in the repository, produce
a table with these columns:

| Module path | Single responsibility | Inputs | Outputs | Patterns in use | Coupling problems |
|---|---|---|---|---|---|

Then produce three additional artifacts:

**1a. Data flow walkthrough (step-by-step)**
Trace a single decorated function call from `@trace` application through `sys.settrace` hook
firing, through `CallNode` update, through `CallGraph.to_dict()`, through `export_html()`.
Name the exact file and line number for each transition. This is not a summary — it is a
precise execution trace for a senior engineer who needs to know exactly where state lives.

**1b. Module dependency graph (textual)**
Show which modules import which, using `→` for "imports from". Highlight any cycles.
Flag any case where a lower layer imports from a higher layer (this is a bug).

Current known issues to flag:
- `funnel/` uses relative import `..tracer` instead of `..core.tracer` (path fragility)
- `analysis/__init__.py` may import from `visualization` (potential cycle)
- `ai/` 23 files each independently import `llm_provider` (no shared base)
- `command_line/main.py` at 1464 lines imports from every domain (layer violation)

**1c. Strengths / Limitations table**

| Dimension | Rating (1–5) | Notes |
|---|---|---|
| Extensibility | | |
| Testability | | |
| Async-readiness | | |
| Production-readiness | | |
| Observability | | |
| Agent runtime readiness | | |

---

### Phase 2 — Gap Analysis Against an Agent Runtime

Evaluate against the capability requirements of an agent execution framework. For each
capability, state: **present / partial / missing** and explain the gap precisely.

| Capability | Status | Existing code to reuse | Gap / cost to close |
|---|---|---|---|
| Tool abstraction | | | |
| Task orchestration | | | |
| Memory / state persistence | | | |
| Event-driven execution | | | |
| Async workflow support | | | |
| Streaming outputs | | | |
| Agent execution loop | | | |
| Plugin / middleware system | | | |
| Model provider abstraction | | | |
| Error classification + retry | | | |
| Execution context propagation | | | |
| Rate limiting / deduplication | | | |

Then answer explicitly:

**Which existing callflow-tracer components map directly to the new runtime layers?**

| New runtime layer | Existing component to reuse | What needs to change |
|---|---|---|
| Native observability / tracing | `core/tracer.py`, `core/async_tracer.py` | |
| Tool-call debugger | `ai/visual_debugger.py` | |
| Analysis pipeline | `analysis/` + `ai/` modules | |
| OTel export | `observability/opentelemetry_exporter.py` | |
| Plugin registry | `core/plugin_system.py` | |
| Framework adapters | `integrations/` | |

---

### Phase 3 — Target Architecture Design

#### 3a. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CODE / FRAMEWORKS                        │
│  FastAPI · Flask · Django · SQLAlchemy · raw Python functions   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ @trace / trace_scope / AutoInstrumentor
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               EXECUTION ENGINE  (Layer 4 — Business Logic)      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AgentRunner                                               │  │
│  │  resolve_agent() → load_context() → run_tool_loop()      │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │ ToolRegistry (lazy-loaded, isolated per agent)            │  │
│  │  register() → resolve() → execute() → emit_event()       │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │ EventBus (Observer pattern)                               │  │
│  │  before_tool_call · after_tool_call · on_trace_complete   │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │ MemoryModule                                              │  │
│  │  load_session() → append_turn() → compact() → persist()  │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │ WorkflowGraph                                             │  │
│  │  plan() → schedule() → track_dependencies()              │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │ TracingLayer  (evolved from core/tracer.py)               │  │
│  │  TraceNode (unified: function trace + tool-call trace)    │  │
│  │  ExecutionContext (trace_id, call_stack, metadata)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴──────────────────┐
          ▼                                    ▼
┌──────────────────────┐          ┌───────────────────────────┐
│  ADAPTERS (Layer 3)  │          │  EXPORT / OBSERVABILITY    │
│  integrations/       │          │  OTel · HTML · JSON · SVG  │
│  InstrumentationBase │          │  Prometheus · Jaeger       │
│  FrameworkAdapter    │          └───────────────────────────┘
└──────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────┐
│  UTILITIES (Layer 2)                                          │
│  config/ · logging · plugin registry · session store         │
└─────────┬────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────┐
│  FOUNDATION (Layer 1)                                         │
│  core/tracer.py · CallGraph · CallNode · CallEdge             │
│  stdlib only — zero third-party imports                       │
└──────────────────────────────────────────────────────────────┘
```

#### 3b. The 5 Dependency Layers

This hierarchy is **enforced**, not suggested. Higher layers may import from lower; never reverse.

| Layer | Path | Responsibility | Imports From |
|---|---|---|---|
| 5 — CLI & API | `command_line/`, `callflow_tracer/__init__.py` | User interface, entry points | Layer 4 |
| 4 — Business Logic | `agent/`, `engine/`, `workflow/`, `memory/` | Agent execution, tool orchestration, session mgmt | Layers 1–3 |
| 3 — Adapters | `integrations/`, `visualization/`, `observability/` | Framework adapters, exporters, OTel | Platform SDKs, Layers 1–2 |
| 2 — Utilities | `config/`, `events/`, `core/plugin_system.py` | Config, EventBus, plugin registry | Layer 1 only |
| 1 — Foundation | `core/tracer.py`, `core/async_tracer.py` | CallGraph, CallNode, sys.settrace | stdlib only |

**Critical import rules:**
- `core/tracer.py` MUST NOT import from `analysis/`, `ai/`, `visualization/`, or `integrations/`
- `integrations/` MUST NOT import from `agent/` or `engine/`
- `command_line/` MUST NOT be imported by any other module
- `ai/` imports only from `core/` and `observability/` — never from `agent/` (to stay testable)
- `visualization/` imports only `core/tracer.CallGraph` — never from `analysis/` or `ai/`

#### 3c. Component Specifications

---

**`Agent`** — `callflow_tracer/agent/agent.py`

Responsibility: Stateful execution unit with its own tool registry, memory, and trace context.

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from callflow_tracer.engine.context import ExecutionContext
from callflow_tracer.memory.module import MemoryModule
from callflow_tracer.tools.registry import ToolRegistry

class Agent(ABC):
    """
    Base class for all agent implementations.

    Design: Template Method — subclasses override plan() and act(); run() is the fixed skeleton.
    The agent owns one MemoryModule (session state), one ToolRegistry (available tools),
    and one active ExecutionContext per invocation.

    Breaking change: This is new — no existing public API is modified.
    """
    def __init__(
        self,
        agent_id: str,
        tool_registry: ToolRegistry,
        memory: MemoryModule,
    ) -> None:
        self.agent_id = agent_id
        self.tools = tool_registry
        self.memory = memory

    async def run(self, prompt: str, context: ExecutionContext) -> AsyncIterator[str]:
        """
        Fixed execution skeleton: plan → act loop → persist.
        Subclasses override plan() and act(), not run().
        """
        plan = await self.plan(prompt, context)
        async for delta in self.act(plan, context):
            yield delta
        await self.memory.append_turn(context.trace_id, prompt, "".join(...))

    @abstractmethod
    async def plan(self, prompt: str, context: ExecutionContext) -> list[str]:
        """Return ordered list of tool names / sub-tasks."""
        ...

    @abstractmethod
    async def act(
        self, plan: list[str], context: ExecutionContext
    ) -> AsyncIterator[str]:
        """Execute the plan, yielding streaming output tokens."""
        ...
```

**Why:** Template Method enforces the plan→act→persist contract without coupling the base class
to any LLM provider. Streaming output (AsyncIterator) is non-negotiable — synchronous agents
block the event loop and cannot be tested with real LLMs efficiently.

---

**`ToolRegistry`** — `callflow_tracer/tools/registry.py`

Responsibility: Lazy-load, register, and execute tools with full tracing of every tool call.

```python
from typing import Callable, Any
from callflow_tracer.tools.base import Tool
from callflow_tracer.events.bus import EventBus

class ToolRegistry:
    """
    Lazy-loading tool catalog. Tools are registered by name and loaded on first call.

    Design: Factory (lazy instantiation) + Strategy (any Tool impl can be registered).
    EventBus integration ensures every tool execution emits before/after events,
    which the TracingLayer listens to for transparent call graph augmentation.

    Thread-safe: uses asyncio.Lock per tool name to prevent double-init races.
    """
    def __init__(self, event_bus: EventBus) -> None:
        self._registry: dict[str, type[Tool] | Callable] = {}
        self._instances: dict[str, Tool] = {}
        self._bus = event_bus

    def register(self, name: str, tool_cls: type[Tool]) -> None:
        """Register a tool class. Instantiated lazily on first resolve()."""
        if name in self._registry:
            raise ValueError(f"Tool '{name}' already registered")
        self._registry[name] = tool_cls

    def resolve(self, name: str) -> Tool:
        """Lazily instantiate and return tool. Raises ToolNotFoundError if unknown."""
        if name not in self._instances:
            if name not in self._registry:
                raise ToolNotFoundError(name)
            self._instances[name] = self._registry[name]()
        return self._instances[name]

    async def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute tool by name; emits before/after events for tracing."""
        tool = self.resolve(name)
        await self._bus.emit("before_tool_call", tool=tool, kwargs=kwargs)
        try:
            result = await tool.execute(**kwargs)
        except Exception as exc:
            await self._bus.emit("tool_call_error", tool=tool, error=exc)
            raise
        await self._bus.emit("after_tool_call", tool=tool, result=result)
        return result
```

**Why:** Lazy loading prevents import-time SDK initialization (same reason OpenClaw uses jiti).
EventBus integration makes tool-call tracing transparent — the TracingLayer subscribes to events
without ToolRegistry knowing about it. No circular dependency.

---

**`ExecutionContext`** — `callflow_tracer/engine/context.py`

Responsibility: Immutable per-invocation context carrier, propagated through the entire call stack.

```python
from dataclasses import dataclass, field
from typing import Any
import uuid
import time

@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable context for one agent invocation.

    Design: Value Object — frozen dataclass prevents accidental mutation across async boundaries.
    Passed by reference through every component that needs trace/session identity.
    Use .fork() to create child contexts for sub-tasks (preserves parent_trace_id chain).

    This is the callflow-tracer equivalent of OpenClaw's session key — the spine
    of the entire execution trace.
    """
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_trace_id: str | None = None
    agent_id: str = "default"
    session_key: str = ""          # format: agent:{agent_id}:session:{hash}
    call_stack: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.monotonic)
    sampling_rate: float = 1.0    # 0.0–1.0; inherited by child contexts

    def fork(self, **overrides) -> "ExecutionContext":
        """Create a child context for a sub-task, preserving lineage."""
        return ExecutionContext(
            parent_trace_id=self.trace_id,
            agent_id=self.agent_id,
            session_key=self.session_key,
            metadata={**self.metadata},
            sampling_rate=self.sampling_rate,
            **overrides,
        )
```

**Why frozen:** Async code that mutates shared context creates race conditions that are
nearly impossible to debug. An immutable value object passed through coroutines is safe by
construction. `fork()` for sub-tasks gives lineage without mutation.

---

**`TraceNode`** — `callflow_tracer/core/nodes.py`

Responsibility: Unified node model for both function-level traces (existing) and tool-call
traces (new). Replaces the split between `CallNode` (function) and tool call dicts (AI layer).

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class NodeKind(str, Enum):
    FUNCTION = "function"     # existing sys.settrace-captured call
    TOOL_CALL = "tool_call"   # agent tool execution
    LLM_CALL = "llm_call"     # LLM provider invocation
    MIDDLEWARE = "middleware"  # middleware chain step

@dataclass
class TraceNode:
    """
    Unified trace node. Replaces CallNode for new code; CallNode stays for backwards compat.

    BREAKING CHANGE WARNING: CallNode.to_dict() format is stable public API.
    TraceNode introduces a superset format. Old consumers reading CallNode JSON are unaffected.
    New consumers should use TraceNode. Provide a migration helper: TraceNode.from_call_node().

    Design: Adapter pattern — from_call_node() wraps legacy CallNode data without modifying it.
    """
    node_id: str
    kind: NodeKind
    name: str                          # function name, tool name, model name
    module: str = ""
    call_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    # For TOOL_CALL / LLM_CALL
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    # For FUNCTION
    args_sample: str = ""
    children: list["TraceNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialization format — stable, versioned."""
        return {
            "v": 2,  # version bump from CallNode's implicit v1
            "id": self.node_id,
            "kind": self.kind.value,
            "name": self.name,
            "module": self.module,
            "call_count": self.call_count,
            "total_time_ms": self.total_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "error_count": self.error_count,
            "metadata": self.metadata,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
        }

    @classmethod
    def from_call_node(cls, node) -> "TraceNode":
        """Adapter: convert legacy CallNode to TraceNode without modifying CallNode."""
        return cls(
            node_id=node.full_name,
            kind=NodeKind.FUNCTION,
            name=node.function_name,
            module=node.module_name,
            call_count=node.call_count,
            total_time_ms=node.total_time * 1000,
            avg_time_ms=node.avg_time * 1000,
            args_sample=node.args_sample or "",
        )
```

**Why:** Tool calls, LLM calls, and function calls are all the same thing: named operations
with duration, error rate, and cost. Splitting them into three different data models forces
consumers to handle three different formats. One unified node model enables a single
visualization, a single OTel exporter, and a single cost analyzer.

---

**`Tool`** — `callflow_tracer/tools/base.py`

Responsibility: Abstract interface every tool must implement. The callflow-tracer equivalent
of OpenClaw's `ChannelPlugin` — pluggable, isolated, discoverable.

```python
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

class ToolSchema(BaseModel):
    """JSON Schema for tool inputs — validated before execution."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema object

class Tool(ABC):
    """
    Base class for all tools registered in ToolRegistry.

    Design contract:
    - name: stable identifier, used as registry key
    - description: shown to LLMs for tool selection
    - schema(): input validation spec
    - execute(): async; receives validated kwargs; returns serializable result

    Tools MUST be stateless or manage their own state thread-safely.
    Tools MUST NOT import from agent/, engine/, or command_line/.
    Tools MAY import from observability/ for self-reporting metrics.

    Tracing note: ToolRegistry wraps execute() with EventBus calls, so tools
    do NOT need to instrument themselves — tracing is injected transparently.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def schema(self) -> ToolSchema: ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any: ...
```

---

**`EventBus`** — `callflow_tracer/events/bus.py`

Responsibility: Observer pattern hub. Decouples tracing, logging, metrics, and alerting from
execution logic. No component needs to know who is listening.

```python
import asyncio
from collections import defaultdict
from typing import Callable, Awaitable, Any

EventHandler = Callable[..., Awaitable[None]]

class EventBus:
    """
    Async observer hub. Handlers subscribed to an event are called concurrently.

    Events emitted by ToolRegistry: before_tool_call, after_tool_call, tool_call_error
    Events emitted by AgentRunner: agent_start, agent_complete, agent_error
    Events emitted by TracingLayer: trace_start, trace_complete, trace_node_recorded

    Design: Observer. TracingLayer subscribes to tool/agent events without ToolRegistry
    or AgentRunner importing TracingLayer. EventBus is in Layer 2 (Utilities) — all higher
    layers may use it; it imports from nothing above Layer 1.

    Error policy: A failing handler does NOT abort the emitting component. Failures are
    logged and re-emitted as 'handler_error' events. This matches OpenClaw's degraded-start
    philosophy: one broken observer must not crash the agent execution.
    """
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        self._handlers[event] = [h for h in self._handlers[event] if h is not handler]

    async def emit(self, event: str, **payload: Any) -> None:
        handlers = self._handlers.get(event, [])
        results = await asyncio.gather(
            *(h(**payload) for h in handlers),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                # Log but do not re-raise — degraded mode, not crash
                import logging
                logging.getLogger(__name__).warning(
                    "EventBus handler failed for event=%s: %s", event, result
                )
```

---

**`MemoryModule`** — `callflow_tracer/memory/module.py`

Responsibility: File-backed session state with atomic writes and TTL cache. The callflow-tracer
equivalent of OpenClaw's `SessionStore` + `SessionWriteLock`.

```python
import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

class MemoryModule:
    """
    Per-agent session persistence with two-layer state management:
      in-memory dict → disk JSON (atomic write pattern).

    Write pattern (mirrors OpenClaw's backup-verify-restore):
      1. Write to {session_key}.json.tmp
      2. Rename to {session_key}.json  (atomic on POSIX)
      3. Verify file is readable        (detect FS corruption)
      4. On failure: restore from .bak  (if present)

    Cache: in-memory per session_key, invalidated when file mtime changes.
    Use append_turn() to mutate — never write the file directly.

    IMPORTANT: Always use the async context manager or append_turn().
    Acquiring the lock manually risks permanent hold on exception — same
    gotcha as OpenClaw's acquireSessionWriteLock() anti-pattern.
    """
    def __init__(self, state_dir: Path, ttl_seconds: int = 45) -> None:
        self._state_dir = state_dir
        self._cache: dict[str, dict] = {}
        self._cache_mtime: dict[str, float] = {}
        self._ttl = ttl_seconds
        self._locks: dict[str, asyncio.Lock] = {}

    def _session_path(self, session_key: str) -> Path:
        safe = session_key.replace(":", "_").replace("/", "_")
        return self._state_dir / f"{safe}.json"

    async def load(self, session_key: str) -> dict[str, Any]:
        path = self._session_path(session_key)
        if path.exists():
            mtime = path.stat().st_mtime
            if (
                session_key in self._cache
                and self._cache_mtime.get(session_key) == mtime
            ):
                return self._cache[session_key]
            data = json.loads(path.read_text())
            self._cache[session_key] = data
            self._cache_mtime[session_key] = mtime
            return data
        return {"turns": [], "metadata": {}}

    async def append_turn(
        self,
        session_key: str,
        user_input: str,
        assistant_output: str,
        metadata: dict | None = None,
    ) -> None:
        if session_key not in self._locks:
            self._locks[session_key] = asyncio.Lock()
        async with self._locks[session_key]:
            session = await self.load(session_key)
            session["turns"].append({
                "user": user_input,
                "assistant": assistant_output,
                "ts": time.time(),
                **(metadata or {}),
            })
            await self._atomic_write(session_key, session)

    async def _atomic_write(self, session_key: str, data: dict) -> None:
        path = self._session_path(session_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        bak = path.with_suffix(".json.bak")
        try:
            tmp.write_text(json.dumps(data, indent=2))
            if path.exists():
                path.replace(bak)
            tmp.replace(path)
            # Verify
            json.loads(path.read_text())
            bak.unlink(missing_ok=True)
        except Exception:
            if bak.exists():
                bak.replace(path)
            raise
        self._cache[session_key] = data
        self._cache_mtime[session_key] = path.stat().st_mtime
```

---

**`InstrumentationAdapter`** — `callflow_tracer/core/instrumentation.py`

Responsibility: Abstract base for all auto-instrumentation patches. Fixes the missing
abstraction in `core/auto_instrumentation.py` where patch logic is hardcoded per library.

```python
from abc import ABC, abstractmethod
from typing import Any

class InstrumentationAdapter(ABC):
    """
    Abstract base for library-specific monkey-patching.

    BREAKING CHANGE: Existing HTTPInstrumentor, RedisInstrumentor, Boto3Instrumentor
    in core/auto_instrumentation.py should be refactored to extend this class.
    The public API (AutoInstrumentationManager) is unchanged.

    Design: Template Method — _patch_methods() / _unpatch_methods() are the extension
    points. enable() / disable() are the fixed lifecycle methods.
    """
    _originals: dict[tuple, Any]

    def __init__(self) -> None:
        self._originals = {}
        self._enabled = False

    @abstractmethod
    def _patch_methods(self) -> None:
        """Apply monkey-patches. Store originals in self._originals."""
        ...

    @abstractmethod
    def _unpatch_methods(self) -> None:
        """Restore all methods stored in self._originals."""
        ...

    @property
    @abstractmethod
    def library_name(self) -> str:
        """Human-readable name, e.g. 'requests', 'redis'."""
        ...

    def enable(self) -> None:
        if not self._enabled:
            self._patch_methods()
            self._enabled = True

    def disable(self) -> None:
        if self._enabled:
            self._unpatch_methods()
            self._enabled = False

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, *_):
        self.disable()
```

---

**`AnalyzerBase`** — `callflow_tracer/ai/base.py`

Responsibility: Missing shared base for all 23 AI analysis modules. Removes the duplicated
`llm_provider` import and `generate()` call pattern repeated in every file.

```python
from abc import ABC, abstractmethod
from typing import Any
from callflow_tracer.ai.llm_provider import LLMProvider

class AnalyzerBase(ABC):
    """
    Shared base for all LLM-powered analysis modules.

    BREAKING CHANGE: Existing ai/ modules can extend this as a non-breaking
    refactor (call super().__init__(provider) in their __init__).

    Design: Strategy — provider is injected, not hardcoded. Tests pass a MockProvider.
    """
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or LLMProvider.from_env()

    async def generate(self, prompt: str, system: str = "") -> str:
        return await self._provider.generate(prompt, system_prompt=system)

    @abstractmethod
    async def analyze(self, graph: dict, **kwargs: Any) -> dict:
        """
        Analyze a CallGraph.to_dict() result and return structured findings.
        Graphs are passed as dicts (not CallGraph objects) to keep AI modules
        independent of core/tracer.py — pure data, no tracer dependency.
        """
        ...
```

---

#### 3d. Proposed Folder Structure

```
callflow_tracer/
├── core/                          ← Layer 1: Foundation — stdlib only
│   ├── tracer.py                  # CallTracer, sys.settrace lifecycle (unchanged)
│   ├── async_tracer.py            # Async-aware tracer (unchanged)
│   ├── nodes.py                   # TraceNode (new unified node model)
│   ├── auto_instrumentation.py    # Refactored: uses InstrumentationAdapter
│   ├── instrumentation.py         # NEW: InstrumentationAdapter ABC
│   └── plugin_system.py           # PluginManager (unchanged)
│
├── events/                        ← Layer 2: Utilities
│   ├── bus.py                     # EventBus (new)
│   └── __init__.py
│
├── memory/                        ← Layer 2: Utilities
│   ├── module.py                  # MemoryModule (new, replaces session-level dicts)
│   └── __init__.py
│
├── tools/                         ← Layer 4: Business Logic
│   ├── base.py                    # Tool ABC + ToolSchema
│   ├── registry.py                # ToolRegistry
│   ├── builtin/                   # Built-in tools
│   │   ├── memory_search.py       # Search agent memory
│   │   ├── code_exec.py           # Sandboxed code execution
│   │   └── web_fetch.py           # HTTP fetch tool
│   └── __init__.py
│
├── agent/                         ← Layer 4: Business Logic
│   ├── agent.py                   # Agent ABC
│   ├── llm_agent.py               # LLM-backed agent implementation
│   └── __init__.py
│
├── engine/                        ← Layer 4: Business Logic
│   ├── context.py                 # ExecutionContext (frozen dataclass)
│   ├── runner.py                  # AgentRunner (run loop, middleware)
│   ├── middleware.py              # Middleware chain: rate limit, dedup, auth
│   └── __init__.py
│
├── workflow/                      ← Layer 4: Business Logic
│   ├── graph.py                   # WorkflowGraph: plan, schedule, track dependencies
│   └── __init__.py
│
├── ai/                            ← Layer 4 (analysis only; no agent coupling)
│   ├── base.py                    # NEW: AnalyzerBase ABC
│   ├── llm_provider.py            # LLMProvider (unchanged)
│   └── [23 existing modules]      # Refactored to extend AnalyzerBase
│
├── analysis/                      ← Layer 3: Adapters (pure data analysis)
│   ├── code_quality.py            # (unchanged)
│   ├── code_churn.py              # (unchanged)
│   ├── anomaly_detection.py       # (unchanged)
│   ├── predictive_analysis.py     # (unchanged)
│   └── __init__.py
│
├── observability/                 ← Layer 3: Adapters
│   ├── opentelemetry_exporter.py  # (unchanged; adapt to TraceNode input)
│   ├── otel_config.py             # (unchanged)
│   └── custom_metrics.py          # (unchanged)
│
├── visualization/                 ← Layer 3: Adapters
│   ├── flamegraph.py              # (unchanged)
│   ├── exporter.py                # (unchanged; add TraceNode → HTML path)
│   ├── comparison.py              # (unchanged)
│   └── jupyter.py                 # (unchanged)
│
├── integrations/                  ← Layer 3: Adapters
│   ├── base.py                    # NEW: FrameworkAdapter ABC
│   ├── fastapi_integration.py     # Refactored to extend FrameworkAdapter
│   ├── flask_integration.py       # Refactored to extend FrameworkAdapter
│   ├── django_integration.py      # Refactored to extend FrameworkAdapter
│   └── [db integrations]
│
├── config/                        ← Layer 2: Utilities
│   ├── loader.py                  # NEW: Config loading with env substitution
│   └── __init__.py
│
├── performance/                   ← Layer 3: Adapters
│   └── [unchanged]
│
├── benchmark/                     ← Layer 3: Adapters
│   └── [unchanged]
│
├── funnel/                        ← Layer 3: Adapters (fix relative import)
│   └── [fix: change ..tracer → ..core.tracer]
│
├── command_line/                  ← Layer 5: CLI
│   ├── main.py                    # Refactored: split into subcommand modules
│   ├── cmd_trace.py               # `trace` subcommand
│   ├── cmd_agent.py               # `agent` subcommand (new)
│   ├── cmd_analyze.py             # Analysis commands
│   └── __init__.py
│
└── __init__.py                    # Public API facade (unchanged surface)
```

---

### Phase 4 — Refactor Roadmap

#### Phase 4.1 — Stabilize & Modularize Tracer Core

**Goal:** Establish the strict 5-layer dependency boundary before any new code is added.

**Tasks (GitHub-issue granularity):**
- [ ] Fix `funnel/` relative import: `..tracer` → `..core.tracer`
- [ ] Audit `analysis/__init__.py` for visualization imports; break any cycle
- [ ] Split `command_line/main.py` (1464 lines) into subcommand files: `cmd_trace.py`,
  `cmd_analyze.py`, `cmd_quality.py`, `cmd_otel.py`, `cmd_funnel.py`
- [ ] Add `InstrumentationAdapter` ABC; refactor `HTTPInstrumentor`, `RedisInstrumentor`,
  `Boto3Instrumentor` to extend it
- [ ] Add `AnalyzerBase` ABC; refactor the 5 most-used AI modules to extend it
  (summarizer, root_cause_analyzer, anomaly_detector, regression_detector, trend_analyzer)
- [ ] Enforce import boundaries via `ruff` rules or a custom `import-linter` config
- [ ] Add `pyproject.toml` extras: `[ai]`, `[agent]`, `[benchmark]`
- [ ] Establish test isolation: every test file uses a temp directory, never reads `~/.callflow`

**Definition of done:** `ruff check` passes with import boundary rules. No circular imports.
`command_line/main.py` < 200 lines. All 5 refactored AI modules pass existing tests.

**Risk:** Splitting `command_line/main.py` may break CLI integration tests. Run the full
CLI test suite after every file split, not just at the end.

---

#### Phase 4.2 — Tool Abstraction Layer

**Goal:** Introduce `Tool` ABC and `ToolRegistry` so agent tools are pluggable, traced, and testable.

**Tasks:**
- [ ] Create `callflow_tracer/tools/base.py` with `Tool` ABC and `ToolSchema`
- [ ] Create `callflow_tracer/tools/registry.py` with `ToolRegistry`
- [ ] Create `callflow_tracer/events/bus.py` with `EventBus`
- [ ] Implement built-in tools: `MemorySearchTool`, `CodeExecTool` (sandboxed), `WebFetchTool`
- [ ] Wire EventBus into ToolRegistry: emit `before_tool_call` / `after_tool_call` events
- [ ] Subscribe TracingLayer to those events: every tool call auto-creates a `TraceNode`
- [ ] Add `TraceNode` to `callflow_tracer/core/nodes.py` with `from_call_node()` adapter
- [ ] Update OTel exporter to accept both `CallGraph` (legacy) and `list[TraceNode]` (new)
- [ ] Add `ToolSchema` validation via `pydantic`; add pydantic as a core dependency
  **Breaking change flag:** pydantic becomes a required (not optional) dependency.

**Definition of done:** A custom `Tool` subclass can be registered, executed, and its call
appears in the trace graph without any manual instrumentation. OTel export works with `TraceNode`.

**Risk:** `pydantic` as a hard dependency adds ~10MB to install size. Mitigate: gate on
`callflow-tracer[agent]` extra, not the base install. This is a breaking change only for
users who install the base package and expect zero new required deps.

---

#### Phase 4.3 — Agent Execution Loop

**Goal:** Build the `Agent` ABC, `AgentRunner`, and `ExecutionContext` so a complete agent
invocation is traceable end-to-end.

**Tasks:**
- [ ] Create `callflow_tracer/engine/context.py` with `ExecutionContext` frozen dataclass
- [ ] Create `callflow_tracer/agent/agent.py` with `Agent` ABC
- [ ] Create `callflow_tracer/agent/llm_agent.py` with first concrete implementation
  (supports OpenAI + Anthropic via existing `ai/llm_provider.py`)
- [ ] Create `callflow_tracer/engine/runner.py` with `AgentRunner` (middleware chain)
- [ ] Create `callflow_tracer/engine/middleware.py`: rate limiter, dedup (by input hash),
  context injector
- [ ] Create `callflow_tracer/memory/module.py` with `MemoryModule` (atomic writes, TTL cache)
- [ ] Wire `MemoryModule` into `Agent.run()` — session persistence is transparent to callers
- [ ] Add `cmd_agent.py` CLI command: `callflow-tracer agent run --agent-id main "your prompt"`
- [ ] Write integration test: full agent invocation with mock LLM, verify TraceNode graph produced

**Definition of done:** `callflow-tracer agent run "hello"` produces a response and writes a
`TraceNode` graph to disk. `MemoryModule` persists turns across invocations. Tests pass with
mock LLM (no real API key required).

**Risk:** `Agent.run()` is async; existing CLI uses synchronous `main()`. The runner must
bridge async → sync for the CLI entry point via `asyncio.run()`. Do not use `asyncio.get_event_loop().run_until_complete()` — deprecated and unsafe.

---

#### Phase 4.4 — Deep Tracing Integration

**Goal:** Every agent action (tool call, LLM call, middleware step) automatically produces
a `TraceNode` — no manual instrumentation required.

**Tasks:**
- [ ] TracingLayer subscribes to all EventBus events from Phases 4.2 and 4.3
- [ ] `ExecutionContext` is propagated via `contextvars.ContextVar` (not thread-local) —
  async-safe across task boundaries
- [ ] `AgentRunner` emits `agent_start` / `agent_complete` / `agent_error` events
- [ ] LLM calls emit `llm_call_start` / `llm_call_complete` with token counts + cost
- [ ] All `TraceNode`s from one invocation are assembled into a `WorkflowGraph`
- [ ] `WorkflowGraph.to_dict()` is compatible with existing `export_html()` — reuse the vis.js
  visualization without changes
- [ ] OTel exporter converts `WorkflowGraph` to spans; parent/child relationship is preserved
- [ ] Add cost reporting: `WorkflowGraph.total_cost_usd()`, shown in flamegraph stats panel
- [ ] Update `analysis/anomaly_detection.py` to accept `WorkflowGraph` (not just `CallGraph`)

**Definition of done:** Run a multi-step agent; open the HTML output; see tool calls, LLM calls,
and function calls in one unified graph with cost annotations. OTel export produces valid spans
with parent/child linkage.

**Risk:** `contextvars.ContextVar` propagation breaks if code uses `asyncio.create_task()`
without copying context. Use `asyncio.create_task(coro, context=copy_context())` throughout
the engine. Flag this pattern for contributors in `CLAUDE.md`.

---

#### Phase 4.5 — Async Execution, Streaming, Plugin System

**Goal:** Full async-first agent execution with streaming output, plugin isolation, and
a first-class extension API.

**Tasks:**
- [ ] `AgentRunner.run_stream()` yields string deltas (streaming) — used by CLI and API
- [ ] Plugin discovery: scan `~/.callflow/plugins/*/`, `./callflow_plugins/*/`, and
  `config.plugins[]` paths — lazy-load via `importlib.import_module`
- [ ] Plugin API: `register(api: CallflowPluginApi) → None` — same pattern as OpenClaw
- [ ] Plugin isolation: each plugin's `register()` runs in a try/except; failure = degraded
  mode (warn + skip), not crash
- [ ] `CallflowPluginApi` exposes: `register_tool()`, `register_analyzer()`,
  `register_exporter()`, `subscribe_event()`
- [ ] `WorkflowGraph` supports parallel task execution: `graph.run_parallel([task1, task2])`
- [ ] Async context manager for agent invocations: `async with agent.session() as ctx:`
- [ ] Streaming CLI: `callflow-tracer agent run --stream "your prompt"` pipes deltas to stdout
- [ ] Write plugin developer guide in `docs/plugins.md`
- [ ] Achieve 70% line coverage across `agent/`, `engine/`, `tools/`, `memory/` modules

**Definition of done:** A third-party tool plugin installed at `~/.callflow/plugins/my-tool/`
is automatically discovered and usable in agent invocations. Streaming works end-to-end in CLI.
`pip install callflow-tracer[agent]` installs a fully functional agent runtime.

**Risk:** Plugin isolation via try/except is weaker than OpenClaw's jiti-based npm graph
isolation. Python plugins share the same process and can import anything. Mitigate with a
plugin allowlist config and documentation warning. Full process-level isolation (subprocess per
plugin) is a future milestone — too much overhead for Phase 4.5.

---

### Phase 5 — Design Patterns: Placement Map

| Pattern | Where | Why |
|---|---|---|
| **Observer** | `events/bus.py` → ToolRegistry, AgentRunner | Decouples tracing from execution; TracingLayer is just a subscriber, not wired into business logic |
| **Factory** | `tools/registry.py` (lazy instantiation), `agent/llm_agent.py` (provider selection) | Defers SDK import until first use; avoids startup overhead from heavy ML deps |
| **Strategy** | `ai/llm_provider.py` (OpenAI/Anthropic/Gemini), `engine/middleware.py` (pluggable middleware) | Provider is injected; tests use MockProvider; middleware chain is configurable per deployment |
| **Middleware / Chain of Responsibility** | `engine/runner.py` middleware stack | Rate limiter → dedup → auth → context injection → agent; each step decides to pass or halt |
| **Template Method** | `agent/agent.py` (plan→act→persist), `core/instrumentation.py` (enable→patch→disable) | Fixed skeleton with extension points; subclasses cannot break the lifecycle |
| **Repository** | `memory/module.py` | Session persistence abstracted behind `load()` / `append_turn()`; callers never touch JSON files |
| **Adapter** | `core/nodes.py` `TraceNode.from_call_node()` | Legacy `CallNode` API preserved while new `TraceNode` is introduced |
| **Null Object** | `DEFAULT_AGENT_ID = "default"` in `engine/context.py` | No None checks in routing; consistent session key formation |

---

### Phase 6 — Differentiation & Positioning

**1. vs LangChain callbacks/tracing**

LangChain's callback system is LangChain-specific. It instruments LangChain objects (Chains,
LLMs, Tools). If your code calls a function outside LangChain — a database, a custom library, a
subprocess — LangChain's callbacks don't see it. callflow-tracer instruments at the Python
interpreter level (`sys.settrace`) — it sees *everything*, including third-party libraries,
stdlib calls, and async coroutines. Unified visibility is the core differentiator.

**2. vs raw OpenTelemetry**

OTel requires manual instrumentation: you add spans with `with tracer.start_as_current_span(...)`.
Every function you want to trace needs a code change. callflow-tracer's `sys.settrace` hook
captures call graphs automatically, with zero code changes in the traced code. OTel is a great
*export format* (and callflow-tracer supports it), but it's not a tracing *method*.

**3. vs py-spy / cProfile**

Statistical profilers (py-spy) and deterministic profilers (cProfile) answer "what took the
most time?" They produce flat profiles: call counts and durations. They do not produce *graphs*
(caller→callee relationships), do not track tool calls, do not integrate with LLMs, and cannot
be queried programmatically. callflow-tracer produces a structured, queryable call graph that
feeds directly into AI analysis, OTel export, and now agent orchestration.

**4. vs rolling your own logging**

Custom logging captures what you remember to log. callflow-tracer captures everything, including
calls you forgot existed. The call graph is auto-generated; cost analysis is automatic; anomaly
detection runs without writing a single log statement. The cost of "rolling your own" is
proportional to what you want to know. callflow-tracer's cost is fixed at install time.

---

**Positioning statement:**

> callflow-tracer is the only Python execution runtime that unifies function-level call graph
> tracing, LLM cost tracking, and agent tool orchestration in a single production-ready library
> — with zero code changes required in the traced application.

**Value proposition (README bullets):**

- **See everything, instrument nothing:** `sys.settrace` captures your entire call graph
  automatically — functions, tools, LLM calls, framework middleware — in one unified trace.
- **Agent-native observability:** Every agent tool execution, LLM call, and workflow step is
  automatically a `TraceNode` with duration, token count, and cost — no manual spans required.
- **OTel-first, vendor-neutral:** Export to Jaeger, Prometheus, or any OTLP backend with one
  function call. Bring your own observability stack; callflow-tracer provides the data.

**Suggested project name:**

**`traceflow`** — if the agent runtime scope warrants a rename.

Rationale: "callflow-tracer" implies a passive observer. The evolved library is an active agent
runtime with native observability. "traceflow" preserves the tracing identity while
communicating the flow/orchestration capability. Migration path: publish `traceflow` as a new
package; keep `callflow-tracer` as a pinned alias for backwards compatibility.

Alternative if you want to keep the brand: **`callflow`** (drop "tracer" — the library is no
longer just a tracer).

---

### Output Requirements Checklist

Before marking any phase complete, verify:

- [ ] All new modules have type annotations (`from __future__ import annotations` at top)
- [ ] All new public APIs have docstrings explaining *why*, not just *what*
- [ ] Breaking changes are flagged with `# BREAKING CHANGE:` comments and in `CHANGELOG.md`
- [ ] Every new module has a corresponding `test_*.py` file with at minimum: happy path,
  error path, and a mock-based isolation test
- [ ] No new module imports from a higher layer than itself (enforced by `ruff` / `import-linter`)
- [ ] `async` functions are never called with `loop.run_until_complete()` — always `asyncio.run()`
- [ ] `MemoryModule` atomic write is tested with a simulated crash (write to tmp, assert bak restores)
- [ ] OTel export is tested with `opentelemetry-sdk` in-memory exporter (no real backend required)
- [ ] Streaming output test verifies deltas arrive incrementally (use `asyncio.Queue` in mock LLM)
- [ ] Plugin load failure test verifies gateway continues in degraded mode (does not crash)

---

*Provide the callflow-tracer repository source when executing this prompt.
The OpenClaw reference architecture is in the [REFERENCE ARCHITECTURE] section above —
adapt its structural patterns to Python and execution tracing; do not copy its TypeScript code.*
