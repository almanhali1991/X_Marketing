# HANDOFF — Marketing Operating System (MOS)
## Complete Implementation Specification for the Coding Agent — v2.0 (Local-First, NVIDIA NIM, Telegram Dashboard)

> **Purpose:** This document is the authoritative handoff for an AI coding agent. Build the complete system from scratch based on this specification. Do not reinterpret the project as a generic social-media bot. Preserve the architectural decisions, constraints, scope, and separation rules below.
>
> **What changed in v2.0 (vs. v1.0):**
> 1. **No X/Twitter integration.** All X API code, OAuth flows, trend endpoints, watchlist retrieval from X, and X publishing paths have been removed. The system no longer publishes to X and no longer consumes any X API.
> 2. **Publishing is performed by the user only.** The system produces content and reviews it through a Telegram bot dashboard. The user copies/approves and publishes manually on any platform they choose (or keeps content for internal use). The system does not call any external publishing API.
> 3. **AI provider switched to NVIDIA NIM (OpenAI-compatible endpoint).** NVIDIA hosts several strong free and paid models via NIM (e.g. `meta/llama-3.3-70b-instruct`, `meta/llama-3.1-405b-instruct`, `mistralai/mixtral-8x7b-instruct-v0.1`, `nvidia/llama-3.1-nemotron-70b-instruct`, `deepseek-ai/deepseek-r1`, `qwen/qwen2.5-7b-instruct`, etc.). The provider layer is OpenAI-compatible so swapping models is a one-line config change.
> 4. **Telegram bot replaces the web dashboard.** The dashboard is delivered entirely inside Telegram using inline keyboards (buttons) — no text-command parsing. It uses the latest `aiogram 3.x` library (async, modern router architecture, native FSM, callback queries).
> 5. **100% local database.** SQLite only. No Redis, no Celery, no Postgres, no external broker, no paid cloud DB add-ons. The system must run entirely on the local machine with zero external services except NVIDIA NIM and Telegram.
> 6. **Trend/watchlist sources replaced.** Since X API is gone, trends come from configurable public RSS/News APIs (e.g. Google News RSS, Al-Riya, Saudi Press Agency, etc.) and from local user-curated watchlist URLs. All sources are pluggable.

---

# 1. PROJECT IDENTITY

**Project name:** Marketing Operating System
**Short name:** MOS
**Primary goal:** Operate as an AI-assisted marketing and content system focused on organic audience growth, original content, Saudi/Gulf trend relevance, selective competitor/watchlist intelligence, scheduled content preparation, and continuous strategy improvement. The system prepares and reviews content; the user is the only one who publishes.

This is **not**:
- a spam bot
- a mass-engagement bot
- an auto-reply bot
- a DM bot
- an affiliate auto-poster
- a browser automation system
- an X/Twitter publishing tool
- a system that calls any social platform's publishing API

The system must behave as a controlled marketing operating system:

```text
Observe
   ↓
 Filter
   ↓
 Understand
   ↓
 Strategize
   ↓
 Create
   ↓
 Validate
   ↓
 Schedule
   ↓
 Notify (via Telegram)
   ↓
 User publishes manually
   ↓
 Measure (manual input)
   ↓
 Learn
```

---

# 2. NON-NEGOTIABLE BUSINESS MODEL

There are two completely separate content paths.

## PATH A — AI ORGANIC CONTENT (System-Prepared)

The system is responsible for:
- Saudi/Gulf trend intelligence (from RSS/News/local sources, **not** X)
- watchlist intelligence (from configurable URL/RSS feeds)
- strategy
- original organic post drafts
- original thread drafts
- content validation
- scheduling **preparation** (the system decides *when* the user should publish)
- notifying the user via Telegram with full content + buttons
- selective performance analysis (based on metrics the user enters manually after publishing)
- weekly/monthly strategy improvement

Flow:

```text
RSS / News / Watchlist Sources
            ↓
      Marketing Agent
            ↓
        NVIDIA NIM API
            ↓
     Content + Strategy
            ↓
       Quality Gates
            ↓
          Scheduler
            ↓
      Telegram Bot (buttons)
            ↓
          User
            ↓
   Manual Publish (anywhere)
```

## PATH B — USER COMMERCIAL CONTENT

The user personally publishes commercial content on whatever platform they choose:

- affiliate links
- coupons
- discounts
- product offers
- sponsored posts
- commercial announcements

Flow:

```text
User
 ↓
Native platform (manual)
↓
Audience
```

### Absolute rule

Commercial/manual posts must **not** be sent through:
- NVIDIA NIM
- the system's content queue
- the system scheduler
- Telegram publishing (the bot never publishes on the user's behalf)

Therefore those posts consume:

```text
NIM usage = 0
Telegram outbound = 0
System processing for publishing = 0
```

The AI builds the audience. The user performs commercial monetization.

```text
AI → Audience / Reach / Authority / Engagement
User → Affiliate / Coupons / Offers / Revenue
```

Do not implement an affiliate auto-publishing feature in the first version.

---

# 3. PRIMARY SCOPE

Build the complete working system as a **local-first** application that runs on the user's own machine (Linux/macOS/Windows). The user controls everything from a Telegram bot.

The system must support:

1. NVIDIA NIM (OpenAI-compatible) API integration.
2. Telegram bot using `aiogram 3.x` with inline keyboards (buttons) — no text-command parsing.
3. Saudi/Gulf trend collection from configurable public sources (RSS, News, government feeds).
4. Monitoring 5–10 user-selected watchlist sources (URLs/RSS feeds).
5. Priority-based watchlist scanning.
6. Trend relevance scoring.
7. Content opportunity generation.
8. Content strategy memory.
9. Original post generation.
10. Original thread generation.
11. Repetition prevention.
12. Content quality gates.
13. Approval/rejection/editing workflow via Telegram inline buttons.
14. Scheduling **preparation** (notify user at the right time).
15. Telegram notification with content + action buttons.
16. Manual metrics input from the user (impressions, likes, replies, etc.).
17. Daily summaries.
18. Weekly strategy generation.
19. Monthly strategy generation.
20. Cost/usage limits (NIM token budget).
21. SQLite local persistence (zero external DB dependencies).
22. Operation on a lightweight VPS (~1 GB RAM) or the user's local machine.
23. 100% local execution — no cloud services, no paid add-ons, no SaaS dependencies.

---

# 4. OUT OF SCOPE FOR MVP

Do not implement:

- **any X/Twitter API calls** (no OAuth, no posting, no trends, no watchlist retrieval from X)
- **any other social platform publishing API** (no Threads, no LinkedIn, no Mastodon publishing)
- automated replies on any platform
- DM handling on any platform
- automated likes
- automated follows
- mass engagement
- bulk replies
- full timeline crawling
- browser automation as an API replacement
- scraping that violates platform rules
- multiple AI providers in MVP (only NVIDIA NIM, but the provider layer must remain swappable)
- Redis
- Celery
- PostgreSQL
- Elasticsearch
- vector database
- heavy microservice architecture
- Docker stack (a single `docker-compose.yml` is allowed for convenience but **not required**)
- any paid SaaS dependency (Make, Zapier, n8n Cloud, Supabase, Firebase, etc.)

Do not add these merely because they are common in social-media systems.

---

# 5. TECHNOLOGY CONSTRAINTS

## Required implementation direction

Use a lightweight Python architecture suitable for a 1 GB VPS or the user's local machine.

Required stack:

```text
Python 3.11+
FastAPI            # only for the optional local webhook + health endpoint
SQLite             # local file DB, no external services
SQLAlchemy 2.x     # ORM + Async support (use sync for SQLite to keep deps minimal)
APScheduler 3.x    # in-process scheduler
httpx              # async HTTP client for NIM and source feeds
Pydantic v2        # settings + schemas
aiogram 3.x        # Telegram bot framework (latest, async, native inline keyboards)
feedparser         # RSS/Atom parsing
beautifulsoup4     # HTML extraction from watchlist URLs
python-dotenv      # .env loading
loguru             # structured logging (lightweight)
typer              # CLI commands (migrate, seed, run-bot, run-scheduler, run-web)
```

Optional (for convenience only):

```text
uvicorn             # ASGI server for FastAPI
jinja2              # only if a tiny local HTML status page is needed
```

Use official SDKs only where appropriate and actively maintained. Avoid unnecessary dependencies.

### Database — 100% local, no add-ons

Use:

```text
SQLite
```

Configure:
- WAL mode (write-ahead logging) for concurrent read + write safety
- Foreign keys enabled (`PRAGMA foreign_keys = ON`)
- Migrations via **Alembic** (included as a dev dependency, runs locally against the local SQLite file)
- Indexes for frequent queries

**Forbidden:**
- Redis, Memcached, or any caching broker
- Celery, RQ, Dramatiq, or any task queue
- PostgreSQL, MySQL, or any remote DB
- Supabase, Firebase, or any DBaaS
- Vector DBs (Pinecone, Weaviate, Chroma, etc.)

The SQLite file lives at `./data/mos.db` (configurable). Back it up by copying the file (see §41).

### No Redis

Use SQLite-backed persistence and in-process scheduling suitable for the current scope.

### No Celery

APScheduler + a single Python process (with separate `run-bot` and `run-scheduler` CLI commands) are sufficient for MVP.

### No cloud services

The system must run with **only two** external endpoints:

```text
1. NVIDIA NIM API (https://integrate.api.nvidia.com/v1)
2. Telegram Bot API (https://api.telegram.org/bot<token>/...)
```

Everything else is local.

---

# 6. EXTERNAL SERVICES

The architecture depends on **only**:

```text
1. NVIDIA NIM API  (OpenAI-compatible, https://integrate.api.nvidia.com/v1)
2. Telegram Bot API
```

Do not require:
- Make
- Zapier
- n8n Cloud
- Supabase
- Firebase
- a second AI provider
- any cloud DB
- any cloud message broker

Use environment variables (`.env`) for all secrets.

### NVIDIA NIM API (free + paid models)

NVIDIA hosts many strong models on NIM at `https://integrate.api.nvidia.com/v1`. The endpoint is **OpenAI-compatible**, so the standard `openai` Python SDK or plain `httpx` calls work with `base_url` pointed at NVIDIA.

Example free / strong models available on NIM (verify at https://build.nvidia.com before finalizing config):

```text
meta/llama-3.3-70b-instruct
meta/llama-3.1-405b-instruct
meta/llama-3.1-70b-instruct
meta/llama-3.1-8b-instruct
mistralai/mixtral-8x7b-instruct-v0.1
mistralai/mistral-nemo-12b-instruct
nvidia/llama-3.1-nemotron-70b-instruct
nvidia/nemotron-4-340b-instruct
deepseek-ai/deepseek-r1
deepseek-ai/deepseek-v3
qwen/qwen2.5-7b-instruct
qwen/qwen2.5-coder-32b-instruct
google/gemma-2-9b-it
google/gemma-2-27b-it
microsoft/phi-3-medium-4k-instruct
```

The free tier typically provides **1,000 credits** per model per month. The system must rotate models when a quota is hit, **or** (simpler MVP) stick to one primary model and stop noncritical AI tasks when the monthly token budget is exhausted. MVP: pick one default model (recommended: `meta/llama-3.3-70b-instruct` for general content / `deepseek-ai/deepseek-r1` for strategy reasoning) and allow override via `.env`.

### Telegram Bot API

Use `aiogram 3.x` (current major version, async, native FSM, callback queries, inline keyboards, webhooks or long-polling). Long-polling is the default for MVP (no public URL needed — fully local). Webhook mode is optional and only configured if the user explicitly provides a public HTTPS endpoint.

---

# 7. AI MODEL — NVIDIA NIM

The current design uses:

```text
Provider:  NVIDIA NIM (OpenAI-compatible)
Endpoint:  https://integrate.api.nvidia.com/v1
Models:    configurable, default meta/llama-3.3-70b-instruct
           strategy model: deepseek-ai/deepseek-r1 (or nvidia/llama-3.1-nemotron-70b-instruct)
```

Important implementation rule:

Do not hardcode model-specific logic throughout the codebase.

Create an AI provider abstraction:

```text
AIProvider (abstract)
    generate(messages, schema=None, effort=STANDARD) -> str | dict
    analyze(prompt, context) -> str
    structured_output(messages, schema) -> dict
    estimate_cost(usage) -> float
```

Then configure the active model from settings/environment.

Only one concrete provider is required for MVP:

```text
NVIDIAProvider   (OpenAI-compatible HTTP client targeting NIM)
```

This keeps future model replacement possible without adding multiple providers now. Because NIM is OpenAI-compatible, swapping models is just changing `NIM_MODEL` in `.env`.

### NIM call example (httpx)

```python
async def generate(messages, model, max_tokens=2048, temperature=0.7):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{settings.NIM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.NIM_API_KEY}"},
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            },
        )
        r.raise_for_status()
        return r.json()
```

### NIM structured output

NIM supports `response_format={"type": "json_object"}` for many models. For models without JSON mode, prompt-engineer the model to return a fenced JSON block and parse defensively. Always validate against a Pydantic schema; on failure, retry once with a stricter prompt, then fall back to `REJECTED`.

---

# 8. AGENT DESIGN

Use one primary orchestration agent:

```text
MarketingAgent
```

Do not create many autonomous agents unless there is a clear technical need.

The agent orchestrates deterministic services/tools:

```text
MarketingAgent
├── SourceService        (RSS / News / URL watchlist collection — replaces X trend endpoint)
├── WatchlistService
├── TrendService
├── ContentService
├── ThreadService
├── QualityGateService
├── SchedulerService
├── NotificationService (Telegram bot)
├── AnalyticsService
├── StrategyService
└── CostGuardService
```

AI reasoning must not directly execute unrestricted actions.

Actions should be mediated by application services.

Example:

```text
AI proposes content
   ↓
 deterministic validator (QualityGate)
   ↓
 database queue (content_items)
   ↓
 approval policy (Telegram inline button → APPROVED/REJECTED/EDITED)
   ↓
 scheduler (decides the recommended publish time, notifies the user)
   ↓
 NotificationService (sends Telegram message with content + buttons)
   ↓
 User publishes manually (outside the system)
   ↓
 User enters metrics back into Telegram (button-driven form)
```

---

# 9. MARKET AND TREND PRIORITIES

Primary geographic relevance:

```text
Priority 1: Saudi Arabia
Priority 2: Gulf region
    - UAE
    - Kuwait
    - Qatar
    - Bahrain
    - Oman
Priority 3: Global topics only when strongly relevant to Saudi/Gulf audience
```

Never prepare content about a global trend merely because it is popular.

A trend must be evaluated for audience relevance.

---

# 10. TREND ENGINE — Source-based (No X)

The Trend Engine processes collected RSS/news/feed data into content opportunities. **There is no X API integration.** Trends come from configurable public sources.

### Built-in source adapters

```text
RSSAdapter         # generic RSS/Atom via feedparser
GoogleNewsAdapter  # https://news.google.com/rss/search?q=<query>&hl=ar&gl=SA&ceid=SA:ar
SaudiPressAgencyAdapter  # https://www.spa.gov.sa/rss.xml (and section feeds)
AlRiyadhAdapter     # https://www.alriyadh.com/rss (or similar)
UserURLAdapter      # arbitrary user-provided URL (HTML scraped with BeautifulSoup)
```

Each adapter must:
- normalize items to a common `RawItem` shape: `{source, external_id, title, summary, url, published_at, language, region_hint}`
- deduplicate by `external_id` (URL hash)
- skip items older than `MAX_TREND_AGE_HOURS` (default 48h)

### Pipeline

```text
Collect (adapters run on schedule)
   ↓
 Normalize (RawItem shape)
   ↓
 Deduplicate (by external_id hash)
   ↓
 Classify (Saudi / Gulf / Global via keyword + region_hint)
   ↓
 Score relevance (deterministic + optional NIM-assisted)
   ↓
 Assess freshness (delta from published_at)
   ↓
 Generate possible angle (NIM, optional)
   ↓
 Approve / Monitor / Ignore
```

## Trend score

Implement configurable scoring:

```text
Saudi Relevance       0–30
Gulf Relevance        0–20
Audience Relevance    0–20
Timing/Freshness      0–15
Content Potential     0–15
--------------------------------
Total                 0–100
```

Suggested interpretation:

```text
85–100 = Immediate Opportunity
70–84  = Potential Opportunity
50–69  = Monitor
0–49   = Ignore
```

These values must be configurable, not scattered magic numbers. Store them in the `settings` table (key/value rows) so the user can edit them via Telegram buttons.

### Trend record (SQLite schema)

Store at minimum:

```text
id
source                 -- RSS adapter name
external_id            -- URL hash
title
summary
url
region
first_seen_at
last_seen_at
freshness_score
saudi_score
gulf_score
audience_score
timing_score
content_potential_score
total_score
status                 -- NEW / MONITORING / USED / IGNORED
suggested_angle
metadata_json
created_at
updated_at
```

### Important behavior

A trend is not automatically content.

The system must reason:

```text
Why is this relevant?
Does it matter to our audience?
Is there a useful original angle?
Is information sufficiently reliable?
Should we prepare a post, create a thread, monitor, or ignore?
```

---

# 11. WATCHLIST (Source-based, not X)

Support:

```text
Minimum initial use: 5 sources
Maximum MVP target: 10 sources
```

The user configures the sources via Telegram buttons (each source is a URL + adapter type + priority).

Each source has a priority:

```text
TIER_1 = high
TIER_2 = medium
TIER_3 = low
```

Suggested scan frequency:

```text
Tier 1: 3 times/day
Tier 2: 2 times/day
Tier 3: 1 time/day
```

Make scan frequencies configurable via settings.

## Watchlist purpose

The watchlist is for intelligence only:
- new topics
- relevant news
- recurring content themes
- useful ideas
- market shifts
- content opportunities

It must not:
- copy content verbatim (use only as inspiration; original drafts only)
- automatically reply on any platform
- like, follow, DM, or interact with any account on any platform

Use incremental retrieval — track the latest seen `external_id` per source to avoid reprocessing the same items.

Store:

```text
watchlist_sources        -- id, name, url, adapter, tier, enabled, latest_seen_id, ...
watchlist_scans          -- id, source_id, started_at, finished_at, items_new, status, error
watchlist_items          -- id, source_id, external_id, title, summary, url, published_at, raw_json
watchlist_insights       -- id, source_id, insight_type, summary, created_at
```

---

# 12. CONTENT STRATEGY

The system must support configurable content pillars.

Do not hardcode a niche.

Example placeholders:

```text
Pillar A
Pillar B
Pillar C
Pillar D
Pillar E
```

The actual pillars, audience, brand voice, vocabulary, and strategy must be editable through the `settings` table (key/value rows, editable via Telegram buttons).

## Content formats

Support at least:

```text
POST
THREAD
```

Content categories should be configurable, for example:

```text
Educational
Trend
Opinion
Conversation
Authority
News Analysis
```

Commercial is not an AI publishing category (and not a system category at all — commercial content lives entirely outside the system).

---

# 13. DAILY CONTENT LIMITS

Default policy:

```text
Maximum AI posts/day = 5
Minimum target is not mandatory
Maximum AI threads/day = 2
```

Suggested operating range:

```text
3–5 posts/day
0–2 threads/day
```

### Critical rule

Do not prepare content simply to satisfy a quota.

```text
No valuable content = no notification
```

The system should be able to produce fewer than the maximum when opportunities are weak.

---

# 14. CONTENT GENERATION PIPELINE

For each candidate:

```text
Opportunity (from Trend Engine or Watchlist)
   ↓
 Topic
   ↓
 Angle
   ↓
 Audience relevance
   ↓
 Hook
   ↓
 Draft (NIM call)
   ↓
 Originality/repetition check (deterministic first, NIM-assisted only when ambiguous)
   ↓
 Quality validation (QualityGate)
   ↓
 Queue (content_items, status=DRAFT)
   ↓
 Review policy (Telegram inline button → APPROVED / REJECTED / EDITED)
   ↓
 Schedule (recommended publish time)
   ↓
 Notify user via Telegram at scheduled time
   ↓
 User publishes manually + enters metrics
```

Store content as structured records.

Suggested fields:

```text
id
type                  -- POST | THREAD
topic
angle
pillar
category
source_type            -- TREND | WATCHLIST | EVERGREEN
source_reference       -- trend_id or watchlist_item_id
hook
body
thread_items_json
score
status                 -- IDEA | DRAFT | REVIEW | REWRITE_REQUIRED | APPROVED | SCHEDULED | NOTIFIED | PUBLISHED_EXTERNALLY | FAILED | REJECTED | CANCELLED
recommended_publish_at
notified_at
user_published_at      -- entered by user via Telegram button
metrics_json           -- user-entered: impressions, likes, replies, etc.
validation_json
created_at
updated_at
```

Note: there is no `x_post_id` (no X integration). The user manually enters when they have published and the metrics they observed.

---

# 15. THREAD GENERATION

Threads must not be generated merely to increase output.

Before generating a thread, evaluate:

```text
Topic Depth
Audience Value
Timeliness
Original Insight
Narrative Potential
```

Store the evaluation.

Suggested thread structure:

```text
1. Hook
2. Context
3. Main point(s)
4. Analysis
5. Practical value or conclusion
```

Thread length must depend on the subject.

---

# 16. ORIGINALITY AND REPETITION PREVENTION

Store content history with:

```text
topic
angle
hook
format
pillar
user_published_at
performance metrics
```

Before approval:

```text
Candidate
   ↓
 Compare with recent history
   ↓
 Same topic?
 Same angle?
 Same hook pattern?
 Too soon?
   ↓
 Similarity result
   ↓
 Approve / Rewrite / Reject
```

Implement deterministic checks first:
- normalized exact duplicates
- repeated topic windows
- repeated hooks
- repeated source references

AI-assisted similarity assessment may be used selectively, but do not send the entire history unnecessarily.

---

# 17. QUALITY GATE

Every AI-generated item must pass validation before being queued for review.

Validate:

```text
Originality
Relevance
Clarity
Accuracy / uncertainty handling
Audience value
Hook strength
Brand voice
Repetition
Spam risk
Platform-policy compliance (generic — no platform-specific publishing, so this is "is this safe to publish anywhere?")
```

Possible outcomes:

```text
APPROVED
REWRITE_REQUIRED
REJECTED
```

Do not silently queue failed content.

---

# 18. APPROVAL POLICY

Implement configurable modes:

```text
MANUAL_APPROVAL                 -- every item waits for a Telegram button click
AUTO_APPROVE_HIGH_CONFIDENCE    -- items with score >= threshold auto-queue for notification
```

For MVP, default to:

```text
MANUAL_APPROVAL
```

The user (via Telegram inline buttons) should be able to:
- approve
- reject
- edit (the bot opens an inline edit flow — button-driven, see §32)
- reschedule (pick a new recommended time from a button list)
- notify now (send the content immediately as a Telegram message)
- cancel

The system must retain audit information about manual changes (`audit_logs` table).

---

# 19. CONTENT QUEUE STATE MACHINE

Implement explicit states:

```text
IDEA
DRAFT
REVIEW
REWRITE_REQUIRED
APPROVED
SCHEDULED
NOTIFIED               -- Telegram message has been sent to the user with content + buttons
PUBLISHED_EXTERNALLY   -- user clicked "I published this" in Telegram
FAILED                 -- e.g., NIM call failed, notification failed
REJECTED
CANCELLED
```

Note: there is no `PUBLISHED` state tied to an API call, because the system never publishes. `PUBLISHED_EXTERNALLY` is set when the user confirms manual publishing.

Do not use ambiguous boolean flags.

Every state transition should be validated and audited.

---

# 20. SCHEDULING (Preparation + Notification — No Publishing)

Use APScheduler (in-process).

Do not assume fixed posting times are optimal.

Start with configurable default windows. The system computes a **recommended** publish time, and at that time sends the user a Telegram notification containing the prepared content + action buttons.

Example concept:

```text
Morning       08:00–10:00  (Asia/Riyadh)
Midday        12:00–14:00
Afternoon     16:00–18:00
Evening       19:00–21:00
Late Evening  22:00–23:30
```

The final times must be configurable via the `settings` table (editable in Telegram).

The analytics system should later recommend improved time windows based on user-entered metrics.

---

# 21. NOTIFICATION (Telegram) — Replaces "Publishing"

The system **never** publishes content on the user's behalf on any platform. Instead, at the recommended publish time, it sends a Telegram message to the user containing:

```text
- Content type (POST / THREAD)
- Topic + angle + pillar
- Full body text (and thread items if THREAD)
- Source URL (trend or watchlist origin)
- Validation score + QualityGate verdict
- Inline keyboard buttons:
   [ ✅ Notify me only — I'll publish manually ]
   [ ✏️ Edit ]
   [ 🔁 Reschedule ]
   [ 🗑️ Reject ]
   [ 📊 Enter metrics (after publishing) ]
```

### Notification service requirements

- idempotency: a content item is notified at most once unless the user requests re-notify
- persistent notification records (`notifications` table)
- retry policy for Telegram API errors (exponential backoff, max 3 attempts)
- duplicate prevention (check `notified_at` is null before sending)
- API error logging (Telegram error code + description, no secrets)
- rate/usage awareness (Telegram has a per-chat message limit; space notifications ≥ 1s apart)

If a network failure occurs after a send request:

```text
Do not blindly retry.
```

First check whether the message was delivered using `getUpdates` / message_id tracking before retrying.

---

# 22. TELEGRAM BOT ADAPTER (Replaces X Client)

Use `aiogram 3.x` (current major version, async, native inline keyboards and FSM).

Create an abstraction:

```text
TelegramBot
├── send_content_notification(content_item) -> message_id
├── send_daily_summary(summary)
├── send_weekly_strategy(strategy)
├── send_alert(text)
├── edit_message_text(...)
├── answer_callback_query(...)
└── register_routers()
```

The bot must be **button-first**. Avoid parsing free text except where the user explicitly types into an FSM edit flow.

### Routers (aiogram 3.x pattern)

```text
routers/
├── root.py                # /start, /help, main menu button
├── dashboard.py           # "Today" overview button
├── content_queue.py       # list DRAFT/REVIEW items, inline buttons per item
├── content_detail.py      # full content + action buttons (Approve/Edit/Reschedule/Reject/Notify)
├── content_edit.py        # FSM-based inline editor (field-by-field, button-driven)
├── trends.py              # list top trends with buttons
├── watchlist.py           # list sources, add/edit/delete via buttons
├── analytics.py           # enter metrics manually (button-driven numeric picker)
├── strategy.py            # show current strategy, edit pillars via buttons
├── settings.py            # all configurable thresholds + budget
├── usage.py               # NIM token usage this month + remaining budget
└── jobs.py                # trigger a job now (run trend_scan, daily_planning, etc.)
```

### Inline keyboard layout (example for a content item)

```text
┌──────────────────────────────────────┐
│  POST • Pillar A • Trend            │
│  Topic: ...                          │
│  ─────────────────────────────────  │
│  <full body text>                    │
│  ─────────────────────────────────  │
│  Score: 82  •  QualityGate: APPROVED│
│  Source: https://...                 │
└──────────────────────────────────────┘

[ ✅ Approve & Schedule ]
[ ✏️ Edit ]
[ 🔁 Reschedule ]
[ 📢 Notify me now ]
[ 🗑️ Reject ]
[ 📊 Enter metrics ]
```

### Main menu (sent on `/start`)

```text
┌────────────────────────────────────┐
│  MOS Dashboard                      │
└────────────────────────────────────┘

[ 🏠 Today ]
[ 📋 Content Queue ]
[ 📈 Trends ]
[ 👁️ Watchlist ]
[ 📊 Analytics ]
[ 🧠 Strategy ]
[ 🗂️ History ]
[ 💰 Usage & Budget ]
[ ⚙️ Settings ]
[ ⚡ Run a Job ]
```

Every subsequent screen is reached by buttons only. Text input is permitted only in inline edit flows (with a "cancel" button always available).

### Long-polling vs. webhook

MVP: long-polling (default `aiogram` mode). Runs locally with no public URL.

Optional: webhook mode if the user provides `TELEGRAM_WEBHOOK_URL` in `.env` (e.g., when running on a VPS with a domain + Nginx).

---

# 23. ANALYTICS PHILOSOPHY (User-Entered Metrics)

The system does **not** fetch metrics from any platform API (X is gone; no other platform is integrated). Instead, the user enters metrics manually via Telegram buttons after publishing content on their chosen platform.

## Daily

Collect enough data to identify:

```text
Best post (by user-entered metrics)
Weakest post
Top topic
Format performance
Immediate observation
```

## Weekly

Analyze:

```text
Top topics
Weak topics
Top hooks
Top formats
Best time windows
Trend conversion
Thread performance
Content fatigue
Recommended changes
```

## Monthly

Analyze:

```text
Audience growth (user-entered follower count delta)
Content growth
Topic evolution
Best formats
Best themes
Strategic direction
```

---

# 24. LOCAL AGGREGATION BEFORE AI

Calculate simple statistics locally before sending summaries to NIM.

Examples:

```text
engagement rate
averages
medians
top/bottom performers
performance by topic
performance by format
performance by time window
trend opportunity performance
```

Do not send large raw datasets when a compact summary is sufficient.

Example AI context:

```text
Top 10 content items
Bottom 10 content items
Topic aggregates
Format aggregates
Time aggregates
Trend aggregates
Previous strategy
Current strategic questions
```

---

# 25. STRATEGY LEARNING LOOP

Implement:

```text
User publishes manually
   ↓
User enters metrics (Telegram)
   ↓
 Aggregate (local)
   ↓
 Analyze (NIM, weekly)
   ↓
 Store strategy insight
   ↓
 Update next planning cycle
```

This is not model training.

The system learns operationally through:
- database history
- analytics
- stored strategy decisions
- retrieved context

---

# 26. MEMORY DESIGN

Use SQLite as the primary memory.

Suggested tables:

```text
brand_profiles
brand_rules
audience_profiles
content_pillars
content_items
content_versions
content_history
content_validations
trends
trend_assessments
watchlist_sources
watchlist_scans
watchlist_items
watchlist_insights
strategies
strategy_insights
analytics_snapshots
notifications            -- replaces publish_attempts (Telegram-side)
metrics_entries          -- user-entered per content item
api_usage               -- NIM token usage
system_jobs
audit_logs
settings                -- key/value config store, editable via Telegram
nim_models              -- available NIM models with metadata + last-known quota
```

Do not use a vector database in MVP.

Use focused SQL queries and curated context.

---

# 27. BRAND MEMORY

Store configurable:

```text
Brand Voice
Tone
Audience
Content Pillars
Preferred Vocabulary
Forbidden Vocabulary
Writing Rules
CTA Rules
Approved Examples
Rejected Examples
```

When generating content, retrieve only relevant context.

Do not place the entire database history into every prompt.

---

# 28. AI REASONING / COST POLICY

Use model effort intelligently.

Simple tasks:
- classification
- filtering
- extraction
- normalization
- deterministic decisions

should use minimal AI or no AI.

Reserve stronger AI reasoning for:
- strategy
- trend interpretation
- difficult content planning
- original content generation
- weekly/monthly analysis

Create an internal task profile:

```text
LOW        -- small model (e.g., qwen/qwen2.5-7b-instruct) or no AI
STANDARD   -- default model (meta/llama-3.3-70b-instruct)
HIGH       -- strategy model (deepseek-ai/deepseek-r1 or nvidia/llama-3.1-nemotron-70b-instruct)
```

Map provider parameters in one adapter layer (the `NVIDIAProvider` picks the right NIM model based on the task profile).

---

# 29. CONTEXT EFFICIENCY

Separate:

```text
STATIC CONTEXT
```

from:

```text
DYNAMIC CONTEXT
```

Static examples:

```text
brand
audience
voice
rules
content pillars
```

Dynamic examples:

```text
current trends
new watchlist insights
recent performance
current strategy
```

Only send the required context for each task.

---

# 30. COST GUARDS

Implement application-level limits.

Suggested settings (all stored in the `settings` table, editable via Telegram):

```text
MAX_AI_POSTS_PER_DAY = 5
MAX_AI_THREADS_PER_DAY = 2
MAX_TREND_SCANS_PER_DAY = 3
MAX_WATCHLIST_SOURCES = 10
MAX_MONTHLY_NIM_TOKENS = configurable (default 1_000_000)
MAX_MONTHLY_TELEGRAM_MESSAGES = configurable (default 1_000)
```

Track actual NIM token usage from API response `usage` field.

When budget threshold is reached (80% warning, 100% hard stop):

```text
PAUSE_NONCRITICAL_AI_TASKS         # at 80%
PAUSE_ALL_AI_TASKS                 # at 100%
```

Never silently continue spending beyond configured hard limits.

Telegram dashboard should show:
- current NIM token usage this month
- configured budget
- remaining budget
- estimated cost in USD (if NIM provides pricing; otherwise tokens only)

---

# 31. SECURITY

Never store:
- platform passwords
- API keys in source code
- secrets in frontend JavaScript (no frontend in MVP — Telegram bot only)

Use:
- environment variables (`.env`) for service secrets (`NIM_API_KEY`, `TELEGRAM_BOT_TOKEN`)
- secure file permissions on `.env` (chmod 600)
- Telegram `chat_id` allowlist (only the configured user/chat can interact with the bot)

Log redaction is mandatory for:
- API keys
- Telegram bot tokens
- Authorization headers
- user-entered personal data

Add a `.env.example`, never commit `.env`.

---

# 32. TELEGRAM DASHBOARD — UX SPECIFICATION (Buttons, not Commands)

The dashboard is delivered entirely inside Telegram using inline keyboards.

### Main menu (sent on `/start`)

```text
[ 🏠 Today ]
[ 📋 Content Queue ]
[ 📈 Trends ]
[ 👁️ Watchlist ]
[ 📊 Analytics ]
[ 🧠 Strategy ]
[ 🗂️ History ]
[ 💰 Usage & Budget ]
[ ⚙️ Settings ]
[ ⚡ Run a Job ]
```

### Today screen

```text
Today's strategy: <one-liner>
AI posts planned: 3/5
AI threads planned: 1/2
Top trend opportunity: <title>
Top watchlist insight: <one-liner>
Next scheduled notification: 16:00
Recent performance: avg engagement 4.2%
NIM budget: 124k / 1M tokens (12%)

[ Open Content Queue ]
[ View Top Trend ]
[ View Strategy ]
```

### Content Queue screen

Lists items in DRAFT / REVIEW / APPROVED / SCHEDULED states with one button per item:

```text
📋 Content Queue

[1] POST • "Topic A" • DRAFT • score 81
[2] POST • "Topic B" • REVIEW • score 76
[3] THREAD • "Topic C" • APPROVED • 16:00
[4] POST • "Topic D" • SCHEDULED • 19:30

[ ← Back ]   [ Filter: All ]
```

Tapping an item opens the Content Detail screen with full body + action buttons (see §22).

### Content Edit flow (FSM, button-driven)

The bot enters an FSM state and presents field choices as buttons:

```text
Edit: which field?

[ Hook ]
[ Body ]
[ Topic ]
[ Angle ]
[ Pillar ]
[ Category ]
[ Schedule time ]
[ Cancel ]
```

For text fields, the bot asks the user to send a single message with the new value (this is the only place free text is accepted), then immediately returns to the field-picker. A "Cancel" button is always visible.

For Schedule time, present a button grid of preset windows (Morning/Midday/Afternoon/Evening/Late Evening) plus a custom-time picker.

### Watchlist screen

```text
👁️ Watchlist Sources

[1] SPA RSS • TIER_1 • last scan 2h ago
[2] Google News "السعودية" • TIER_1 • last scan 1h ago
[3] Al Riyadh • TIER_2 • last scan 4h ago
[4] Custom URL • TIER_3 • last scan 8h ago

[ ➕ Add Source ]
[ ← Back ]
```

"Add Source" opens a button-driven wizard: choose adapter → enter URL (free text in FSM) → choose tier → confirm.

### Analytics screen

```text
📊 Analytics

Last 7 days:
  Posts published: 18
  Avg engagement: 4.6%
  Top topic: <topic>
  Top format: POST

[ Enter metrics for a content item ]
[ View weekly summary ]
[ View monthly summary ]
[ ← Back ]
```

"Enter metrics for a content item" → button list of recent items → for each metric (impressions, likes, replies, reposts, profile visits) show a numeric picker (`-100 -10 -1 +1 +10 +100` style buttons) or accept free text in FSM.

### Settings screen

```text
⚙️ Settings

[ Brand profile ]
[ Content pillars ]
[ Daily limits ]
[ NIM model ]
[ NIM budget ]
[ Posting time windows ]
[ Trend scoring weights ]
[ Telegram chat allowlist ]
[ ← Back ]
```

Each button opens a sub-screen with editable values (button-driven, with "Reset to default" always available).

### Run a Job screen

```text
⚡ Run a Job Now

[ Trend scan ]
[ Watchlist scan (all tiers) ]
[ Daily planning ]
[ Generate content now ]
[ Daily summary ]
[ Weekly strategy ]
[ Monthly strategy ]
[ Backup database ]
[ ← Back ]
```

Each button triggers the corresponding APScheduler job immediately and replies with a status message.

---

# 33. DATABASE DESIGN

Use SQLAlchemy 2.x models and Alembic migrations.

At minimum, ensure indexes for:

```text
content_items.status
content_items.recommended_publish_at
content_items.user_published_at
trends.status
trends.total_score
watchlist_items.source_id + external_id
notifications.content_item_id
metrics_entries.content_item_id
analytics_snapshots.created_at
system_jobs.next_run_at
api_usage.created_at
```

Use UTC internally. Convert to configured display timezone in Telegram messages.

Default operational timezone:

```text
Asia/Riyadh (UTC+3)
```

Configurable via the `settings` table.

---

# 34. JOBS

Use persistent job execution records (`system_jobs` table).

Suggested recurring jobs:

```text
source_scan_tier_1            -- every 8h
source_scan_tier_2            -- every 12h
source_scan_tier_3            -- every 24h
trend_normalize_and_score     -- every 1h
daily_planning                -- 07:00 Asia/Riyadh
content_generation            -- 07:30, 12:30, 17:30 (staggered)
content_validation            -- 30 min after each generation
notification_dispatch          -- every 5 min (picks SCHEDULED items whose time has come)
metrics_reminder              -- 22:00 (asks user to enter metrics for items published today)
daily_summary                 -- 23:00
weekly_strategy               -- Sunday 08:00
monthly_strategy              -- 1st of month 08:00
usage_reconciliation          -- every 6h
cleanup                       -- daily 03:00 (purge old raw items)
backup                        -- daily 02:00 (copy SQLite file)
```

Do not schedule all jobs simultaneously on a 1 GB VPS.

Stagger them (offsets shown above).

---

# 35. ERROR HANDLING

Every external operation must use:
- timeouts
- structured exceptions
- retries only when safe
- backoff
- persistent failure records

Differentiate:
- validation errors
- authentication errors (NIM 401, Telegram 401)
- rate-limit errors (NIM 429, Telegram 429)
- provider outages (NIM 5xx, Telegram 5xx)
- network errors
- duplicate risks (re-notifying the same content item)
- database errors

Do not swallow exceptions. Surface them to the user via Telegram alert messages (with redaction of secrets).

---

# 36. LOGGING AND AUDIT

Use structured application logs (loguru).

Store relevant audit events in `audit_logs`:

```text
content created
content edited
content approved
content rejected
content notified
content marked published externally
strategy changed
watchlist changed
settings changed
nim token refresh failed (N/A — NIM uses static API key)
budget threshold reached
job failed
job retried
backup completed
backup failed
```

Do not store secrets in logs.

---

# 37. PROJECT STRUCTURE

Use a clean modular structure:

```text
mos/
├── app/
│   ├── main.py                    # FastAPI entry (health endpoint only, optional)
│   ├── core/
│   │   ├── config.py              # Pydantic settings from .env
│   │   ├── security.py            # .env loading, chat_id allowlist
│   │   ├── logging.py             # loguru setup + redaction filter
│   │   └── database.py            # SQLAlchemy engine + session factory
│   ├── models/                    # SQLAlchemy ORM models (one file per table group)
│   ├── schemas/                   # Pydantic v2 DTOs
│   ├── repositories/              # thin DB access layer
│   ├── services/
│   │   ├── ai/
│   │   │   ├── base.py            # AIProvider abstract
│   │   │   └── nvidia.py          # NVIDIAProvider (NIM, OpenAI-compatible)
│   │   ├── sources/               # RSSAdapter, GoogleNewsAdapter, UserURLAdapter, etc.
│   │   ├── trends/
│   │   ├── watchlist/
│   │   ├── content/
│   │   ├── analytics/
│   │   ├── strategy/
│   │   ├── scheduler/
│   │   ├── notifications/
│   │   │   └── telegram.py        # TelegramBot wrapper around aiogram 3.x
│   │   └── costs/
│   ├── agents/
│   │   └── marketing_agent.py
│   ├── prompts/
│   │   ├── strategy.py
│   │   ├── content.py
│   │   ├── trend.py
│   │   └── analytics.py
│   ├── bot/                       # aiogram 3.x application
│   │   ├── app.py                 # Bot, Dispatcher, router registration
│   │   ├── middlewares.py         # chat_id allowlist + usage logging
│   │   ├── keyboards.py           # inline keyboard builders
│   │   ├── states.py              # FSM states for edit flows
│   │   └── routers/
│   │       ├── root.py
│   │       ├── dashboard.py
│   │       ├── content_queue.py
│   │       ├── content_detail.py
│   │       ├── content_edit.py
│   │       ├── trends.py
│   │       ├── watchlist.py
│   │       ├── analytics.py
│   │       ├── strategy.py
│   │       ├── settings.py
│   │       ├── usage.py
│   │       └── jobs.py
│   ├── api/                      # optional FastAPI health/metrics only
│   │   └── routes.py
│   └── jobs/
│       └── definitions.py        # APScheduler job registration
├── migrations/                    # Alembic migrations
│   ├── env.py
│   └── versions/
├── data/
│   ├── mos.db                    # SQLite file (auto-created)
│   └── backups/                  # daily SQLite copies
├── tests/
├── scripts/
│   ├── seed.py                   # seed default settings + brand profile
│   └── backup_db.py
├── pyproject.toml                # dependencies (preferred over requirements.txt)
├── .env.example
├── README.md
└── systemd/
    ├── mos-bot.service
    ├── mos-scheduler.service
    └── mos-web.service           # optional
```

The exact structure may improve, but preserve clear separation between:
- bot UI (aiogram routers)
- domain/business logic (services)
- persistence (models + repositories)
- AI provider
- source adapters (RSS, news, URLs)
- jobs
- notifications

---

# 38. IMPLEMENTATION ORDER

Build in this order.

## Phase 1 — Foundation

1. Initialize project (`pyproject.toml`, `.env.example`, folder structure).
2. Configuration management (Pydantic settings).
3. Logging (loguru + redaction filter).
4. SQLite + SQLAlchemy 2.x engine + session factory (WAL mode, FK on).
5. Alembic migrations skeleton.
6. Core models (`settings`, `audit_logs`, `api_usage`, `system_jobs`).
7. Optional FastAPI health endpoint (`/healthz`).
8. Chat-id allowlist middleware (security).
9. CLI commands via `typer`: `migrate`, `seed`, `run-bot`, `run-scheduler`, `run-web`, `backup`.

## Phase 2 — AI Integration (NVIDIA NIM)

1. `AIProvider` abstraction.
2. `NVIDIAProvider` (OpenAI-compatible HTTP client targeting `https://integrate.api.nvidia.com/v1`).
3. Structured response schema (JSON mode + Pydantic validation).
4. Prompt templates (`prompts/`).
5. Cost/usage tracking (`api_usage` table — tokens in, tokens out, model, cost estimate).
6. Failure handling (429/5xx backoff, JSON parse retry).
7. Task profile mapping (LOW/STANDARD/HIGH → NIM model).

## Phase 3 — Source Adapters (Replaces X Trend/Watchlist)

1. `SourceAdapter` abstract + `RawItem` shape.
2. `RSSAdapter` (feedparser).
3. `GoogleNewsAdapter` (Arabic Saudi query).
4. `SaudiPressAgencyAdapter`.
5. `AlRiyadhAdapter` (or similar Saudi news feed).
6. `UserURLAdapter` (BeautifulSoup extraction).
7. Watchlist source CRUD via Telegram buttons.
8. Incremental retrieval (track `latest_seen_id` per source).

## Phase 4 — Intelligence

1. Trend normalization + dedup.
2. Trend scoring (deterministic weights from `settings`).
3. Trend classification (Saudi / Gulf / Global).
4. Optional NIM-assisted angle generation for high-score trends.
5. Watchlist priority scanning + insight extraction.

## Phase 5 — Content

1. Content opportunity model.
2. Strategy context retrieval (focused SQL, not full history).
3. Post generation (NIM `STANDARD` profile).
4. Thread generation (NIM `HIGH` profile).
5. Duplicate checks (deterministic first).
6. Quality gate (rule-based + NIM-assisted where ambiguous).
7. Queue state machine.
8. Telegram inline-button approval workflow.

## Phase 6 — Notification & Scheduling (Replaces Publishing)

1. APScheduler setup (in-process, persistent `system_jobs` records).
2. `notification_dispatch` job (every 5 min, picks SCHEDULED items past their time).
3. Idempotency (check `notified_at` is null before sending).
4. Telegram message builder (content + inline keyboard).
5. Safe retry on Telegram API errors (with `message_id` tracking to avoid duplicates).
6. "I published this" button → state → `PUBLISHED_EXTERNALLY`.

## Phase 7 — Analytics (User-Entered Metrics)

1. Metrics entry flow (Telegram button-driven numeric picker or FSM text input).
2. Local aggregation (daily/weekly/monthly).
3. Daily summary message.
4. Weekly NIM analysis.
5. Monthly NIM analysis.
6. Strategy persistence (`strategies` + `strategy_insights`).

## Phase 8 — Operations

1. Cost guard (NIM token budget thresholds).
2. Job monitoring (`system_jobs` health shown in Telegram "Run a Job" screen).
3. Audit logs viewable in Telegram (admin only).
4. Backup script (`scripts/backup_db.py` — copy SQLite file with timestamp, retention 14 days).
5. systemd service files (bot, scheduler, optional web).
6. README.md with local setup steps.
7. Documentation of NIM model list and how to add new models.

---

# 39. TESTING REQUIREMENTS

Add tests for critical logic.

At minimum:

```text
trend scoring
content state transitions
daily limits
thread limits
duplicate prevention
commercial-path exclusion (no API publishing ever)
budget guards (NIM token limit enforcement)
notification idempotency (no double-send)
notification retry safety (no duplicate Telegram messages on transient failure)
metrics entry flow
quality gate outcomes
watchlist priority scheduling
RSS adapter normalization
Google News adapter dedup
settings edit via Telegram (button callback handlers)
chat_id allowlist enforcement
```

Mock all external APIs (NIM and Telegram) in unit tests using `respx` (httpx mock) and `aiogram` test utilities.

No real API calls during ordinary tests.

---

# 40. DEPLOYMENT — Local-First

Target:

```text
User's local machine (Linux / macOS / Windows)
OR a lightweight Ubuntu VPS ~1 GB RAM
```

Provide:
- `.env.example` template (all keys + comments).
- `alembic upgrade head` migration command.
- Application startup commands:
  - `python -m mos run-bot` (Telegram long-polling, blocks)
  - `python -m mos run-scheduler` (APScheduler, blocks)
  - `python -m mos run-web` (optional FastAPI health endpoint, blocks)
- systemd service files (for VPS deployment).
- Backup procedure for SQLite (`scripts/backup_db.py`).
- Restore procedure (copy backup file back to `./data/mos.db` while services are stopped).

For local development, the user can run both `run-bot` and `run-scheduler` in two terminal windows. No public URL needed (Telegram long-polling).

---

# 41. SQLITE BACKUP

Provide a simple automated backup process.

Requirements:
- consistent SQLite backup (use `VACUUM INTO` or sqlite3 `.backup` API — never copy a file mid-write)
- timestamped files in `./data/backups/`
- retention policy (default 14 days, configurable)
- documented restore command in README

Suggested implementation:

```python
# scripts/backup_db.py
import sqlite3, datetime, pathlib
src = pathlib.Path("data/mos.db")
dst = pathlib.Path(f"data/backups/mos-{datetime.datetime.utcnow():%Y%m%d-%H%M%S}.db")
dst.parent.mkdir(parents=True, exist_ok=True)
con = sqlite3.connect(src)
con.backup(sqlite3.connect(dst))   # safe online backup
con.close()
# prune older than 14 days
```

Do not overengineer cloud backup in MVP unless explicitly configured.

---

# 42. RESOURCE DISCIPLINE

The VPS is lightweight.

Avoid:
- loading large ML models locally (NIM hosts them — calls are HTTP)
- background workers that remain idle with large memory footprints
- excessive concurrent API requests
- large in-memory datasets
- full social graph storage
- high-frequency polling

Use:
- incremental retrieval (track latest_seen_id per source)
- database indexes
- compact AI context
- staggered jobs
- HTTP connection reuse (one `httpx.AsyncClient` shared across the app)

---

# 43. MANUAL COMMERCIAL CONTENT EXCLUSION TEST

This is a mandatory design rule.

There must be no route or scheduled process that automatically converts commercial content into AI generation, Telegram publishing, or any external API call.

The application should not require the user to enter affiliate posts at all.

If the user publishes manually on their chosen platform, the system remains independent.

Therefore:

```text
Manual platform post
≠ AI Content Item
≠ Scheduled Notification Item
≠ Telegram outbound (except the user's own messages to the bot)
```

Do not violate this separation in future code without an explicit requirements change.

---

# 44. SAFETY AND PLATFORM COMPLIANCE

The system calls only two external services: NVIDIA NIM and Telegram Bot API.

Both are official, supported, public APIs. Use them per their terms.

Do not implement features intended to create artificial engagement on any platform.

Explicitly exclude:
- engagement farming
- automated mass replies on any platform
- mass likes / follows / DMs on any platform
- artificial traffic
- spam posting
- scraping that violates any source's terms (respect `robots.txt` for `UserURLAdapter`)

The system's automation must focus on **content preparation** and **strategy analytics**, not on-platform automation.

---

# 45. ACCEPTANCE CRITERIA

The MVP is complete only when all of the following work:

## Core
- [ ] Application starts reliably locally (`run-bot` + `run-scheduler`).
- [ ] SQLite database migrates correctly (`alembic upgrade head`).
- [ ] Telegram bot responds to `/start` with the main menu keyboard.
- [ ] Configuration is environment-based (`.env`).
- [ ] Only the allowlisted `chat_id` can interact with the bot.

## AI (NVIDIA NIM)
- [ ] NIM integration works (test call to `meta/llama-3.3-70b-instruct`).
- [ ] Structured generation is validated against Pydantic schemas.
- [ ] NIM provider failures (429, 5xx) are handled with backoff.
- [ ] Token usage is recorded per call (`api_usage` table).
- [ ] Model is swappable by editing `.env` (`NIM_MODEL=...`).

## Sources (Replaces X)
- [ ] RSS adapter fetches and normalizes items.
- [ ] Google News Saudi Arabic feed works.
- [ ] User can add a custom URL source via Telegram buttons.
- [ ] Incremental retrieval works (no reprocessing of seen items).
- [ ] Trend scoring produces sensible values.

## Intelligence
- [ ] Trends can be collected from at least 3 source types.
- [ ] Trend scoring works.
- [ ] 5–10 watchlist sources are supported.
- [ ] Priority scanning works (Tier 1/2/3 frequencies).

## Content
- [ ] Posts can be generated via NIM.
- [ ] Threads can be generated via NIM.
- [ ] Repetition checks work.
- [ ] Quality gate works (APPROVED / REWRITE_REQUIRED / REJECTED).
- [ ] Approval workflow works (Telegram inline buttons → state transitions).
- [ ] Daily limits work.

## Scheduling & Notification
- [ ] Approved content can be scheduled (recommended time computed).
- [ ] Scheduled content triggers a Telegram notification at the correct time.
- [ ] Notification idempotency works (no double-send).
- [ ] Retry logic is safe (no duplicate Telegram messages on transient failure).
- [ ] "I published this" button transitions state to `PUBLISHED_EXTERNALLY`.

## Analytics
- [ ] User can enter metrics for a content item via Telegram buttons.
- [ ] Daily summaries work.
- [ ] Weekly strategy analysis works.
- [ ] Historical insights influence future planning.

## Cost
- [ ] NIM token budget limits work (80% warning, 100% pause).
- [ ] Noncritical AI jobs pause when hard limit is reached.
- [ ] Usage screen in Telegram shows accurate numbers.

## Separation Rule
- [ ] No affiliate/coupon/product/sponsored content is auto-notified.
- [ ] Manual publishing on any platform remains outside the system.
- [ ] Such manual publishing does not consume system AI or Telegram operations.
- [ ] No X/Twitter API call exists anywhere in the codebase (grep-verified).

---

# 46. FINAL ARCHITECTURE

```text
                    ┌─────────────────────────────────────┐
                    │        USER (Telegram chat)          │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   Telegram Bot       │
                          │   (aiogram 3.x)      │
                          │   inline keyboards   │
                          └──────────┬──────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │                                      │
                  ▼                                      ▼
        AI ORGANIC SYSTEM                       USER MANUAL
        (prepares content)                      COMMERCIAL POSTS
                  │                                      │
                  ▼                                      ▼
           Marketing Agent                          Any platform
                  │                                 (manual)
        ┌─────────┼─────────┬─────────────┐
        ▼         ▼         ▼             ▼
   Sources    Watchlist  Strategy      Analytics
   (RSS/News) (RSS/URL)                (user-entered)
        │         │         │             │
        └─────────┴────┬────┴─────────────┘
                       ▼
                 NVIDIA NIM API
              (integrate.api.nvidia.com)
                       │
                       ▼
              Content / Threads / Plan
                       │
                       ▼
                  Quality Gate
                       │
                       ▼
                  Content Queue
                       │
                       ▼
                    Scheduler
                       │
                       ▼
              Telegram Notification
              (sent to user with buttons)
                       │
                       ▼
                    USER
                       │
                       ▼
            Manual publish (anywhere)
                       │
                       ▼
            User enters metrics → Analytics
```

---

# 47. FINAL IMPLEMENTATION PRINCIPLES

1. Build a marketing operating system, not a posting bot.
2. Keep AI content preparation separate from manual commercial publishing.
3. Use one AI provider in MVP (NVIDIA NIM) — keep the layer swappable.
4. Keep the architecture compatible with a 1 GB VPS or the user's local machine.
5. Prefer deterministic logic where AI is unnecessary.
6. Use AI for judgment, strategy, and original content.
7. Do not prepare content simply to meet quotas.
8. Store enough history to avoid repetition and improve strategy.
9. Aggregate data locally before expensive AI analysis.
10. Put hard limits around AI and Telegram spending.
11. Use official Telegram integration (aiogram 3.x). Do not substitute scraping for Telegram features.
12. Keep the MVP narrow and working before adding advanced features.
13. Do not invent unsupported NIM API capabilities. Verify current official documentation at https://build.nvidia.com during implementation.
14. Isolate external-provider details behind adapters because APIs, models, endpoints, and pricing can change.
15. The system never publishes anywhere. It only prepares content and notifies the user via Telegram.
16. 100% local database (SQLite). Zero cloud DB dependencies.

---

# 48. CONFIGURATION TEMPLATE (.env.example)

```bash
# ──────────────────────────────────────────────────────────────
# MOS — Marketing Operating System (local-first)
# Copy to .env and fill in real values. Never commit .env.
# ──────────────────────────────────────────────────────────────

# ── App ──
APP_ENV=development                       # development | production
APP_TIMEZONE=Asia/Riyadh
APP_LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR
APP_DB_PATH=./data/mos.db
APP_BACKUP_DIR=./data/backups
APP_BACKUP_RETENTION_DAYS=14
APP_USE_WEBHOOK=false                     # true only on VPS with public HTTPS

# ── Security ──
TELEGRAM_ALLOWED_CHAT_IDS=123456789       # comma-separated; only these chats can use the bot

# ── NVIDIA NIM (AI provider) ──
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NIM_MODEL_STANDARD=meta/llama-3.3-70b-instruct
NIM_MODEL_LOW=qwen/qwen2.5-7b-instruct
NIM_MODEL_HIGH=deepseek-ai/deepseek-r1
NIM_TIMEOUT_SECONDS=60
NIM_MAX_RETRIES=3

# ── Telegram Bot ──
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_URL=                     # leave empty for long-polling (default)

# ── Source adapters (defaults; editable in-app) ──
SOURCE_GOOGLE_NEWS_QUERY=السعودية
SOURCE_GOOGLE_NEWS_REGION=SA
SOURCE_GOOGLE_NEWS_LANG=ar
SOURCE_SPA_FEED_URL=https://www.spa.gov.sa/rss.xml
SOURCE_MAX_TREND_AGE_HOURS=48

# ── Limits / budget ──
MAX_AI_POSTS_PER_DAY=5
MAX_AI_THREADS_PER_DAY=2
MAX_TREND_SCANS_PER_DAY=3
MAX_WATCHLIST_SOURCES=10
MAX_MONTHLY_NIM_TOKENS=1000000
MAX_MONTHLY_TELEGRAM_MESSAGES=1000
NIM_BUDGET_WARNING_PCT=80
NIM_BUDGET_HARD_STOP_PCT=100

# ── Scheduler (cron-style defaults) ──
SCHED_TIER1_CR=*/8 * * * *
SCHED_TIER2_CR=*/12 * * * *
SCHED_TIER3_CR=0 0 * * *
SCHED_DAILY_PLANNING_CR=0 7 * * *
SCHED_NOTIFICATION_DISPATCH_CR=*/5 * * * *
SCHED_DAILY_SUMMARY_CR=0 23 * * *
SCHED_WEEKLY_STRATEGY_CR=0 8 * * 0
SCHED_MONTHLY_STRATEGY_CR=0 8 1 * *
SCHED_BACKUP_CR=0 2 * * *
```

---

# 49. REQUIRED FIRST DELIVERABLES

Before writing the entire system, produce:

1. Final repository tree (per §37).
2. `pyproject.toml` with the dependency list from §5.
3. `.env.example` (per §48).
4. Database schema/model plan (per §26, §33).
5. Alembic migration plan (initial migration creates all tables; later migrations are additive).
6. Configuration design (Pydantic settings class loading §48 keys).
7. NVIDIA NIM integration verification against current official documentation at https://build.nvidia.com (confirm available models, JSON mode support, rate limits).
8. Telegram Bot integration verification against `aiogram 3.x` docs and the Bot API (confirm callback_query limits, inline keyboard layout limits, FSM availability).
9. Implementation checklist mapped to the phases in §38.
10. Then begin implementation.

---

# 50. CODING AGENT EXECUTION RULES

When implementing:

- Start with the repository structure and architecture.
- Create the database schema and migrations before feature code.
- Implement features in the stated phases.
- Keep code, comments, identifiers, and technical documentation in English.
- Make Telegram UI text in **Arabic** (with optional English fallback) since the target user is Saudi/Gulf.
- Do not use placeholder implementations for critical paths.
- Do not claim an external API capability exists without verifying current official documentation (NIM: https://build.nvidia.com; Telegram: https://core.telegram.org/bots/api).
- Do not silently broaden the scope.
- If a NIM capability required by this specification is unavailable under the selected model, implement a clear capability check and document the limitation rather than replacing it with scraping or browser automation.
- Test each phase before proceeding.
- Preserve the separation between AI content preparation and manual commercial publishing.
- Prefer simple, maintainable code over speculative abstractions.
- **Never** add X/Twitter API code in any form. If a future requirement reintroduces X, it must come with an explicit requirements change and a new handoff document.
- **Never** publish content on the user's behalf on any platform. The Telegram bot only notifies and collects user input.
- **Never** require a cloud database, Redis, Celery, or any paid SaaS. The system runs 100% locally with SQLite.

---

# END OF HANDOFF (v2.0)
