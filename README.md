# 🕷️ Scrapy - Event-Driven Market Research Scraper

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-green.svg)](https://playwright.dev/python/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![Docker Support](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated, event-driven web intelligence and market research tool. Built with **Playwright**, **Python**, and **Telegram Bot API**, it scrapes discussions and posts from targeted Facebook Groups or online forums, prepares structured summaries, and dispatches real-time intelligence reports directly to your Telegram chat.

Designed to be executed locally, inside **Docker**, or serverlessly on **GitHub Actions** via webhook triggers or manual dispatch.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture & Workflow](#-architecture--workflow)
- [Key Features](#-key-features)
- [Security Notice](#-security-notice)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [1. Running Locally](#1-running-locally)
  - [2. Running via Docker](#2-running-via-docker)
  - [3. Running on GitHub Actions](#3-running-on-github-actions)
- [Project Structure](#-project-structure)
- [Upcoming Roadmap](#-upcoming-roadmap)
- [Contributing & License](#-contributing--license)

---

## 🎯 Overview

Market researchers, community managers, and founders often need to monitor key discussions across social groups and niche forums. **Scrapy** automates this by:
1. Emulating authentic browser interactions (including session restoration and human-like scrolling).
2. Extracting the latest relevant posts from protected or public feeds.
3. Formatting and sending actionable intelligence summaries instantly to Telegram.

---

## 🔄 Architecture & Workflow

```
┌──────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  Trigger Source  │ ----> │  Playwright Browser  │ ----> │  Parser & Analysis   │
│ (Action/Webhook) │       │ (Session & Human Sim)│       │ (Extract Posts & AI) │
└──────────────────┘       └──────────────────────┘       └──────────┬───────────┘
                                                                     │
                                                                     ▼
                                                          ┌──────────────────────┐
                                                          │ Telegram Bot API     │
                                                          │ (Instant Report)     │
                                                          └──────────────────────┘
```

1. **Trigger**: Execution is initiated locally, via Docker, or via GitHub Actions (`workflow_dispatch` / `repository_dispatch`).
2. **Session Injection**: Injects saved authentication cookies (`cookies.json` or base64/JSON environment secrets) to bypass login walls.
3. **Extraction**: Headless Chromium navigates to the target group, simulates realistic human scrolling to trigger lazy-loaded feeds, and captures post elements.
4. **Analysis & Dispatch**: Formats post summaries and dispatches an alert report to your Telegram chat.

---

## ✨ Key Features

- **Headless Browser Automation**: Powered by [Playwright](https://playwright.dev/python/) for reliable rendering of dynamic single-page applications (SPAs).
- **Session Cookie Management**: Supports loading cookies from local `cookies.json` or encrypted environment variables (`COOKIES_JSON` / `FACEBOOK_COOKIES`), with automatic Base64 decoding support.
- **Human Behavioral Emulation**: Implements randomized scrolling intervals to simulate organic human reading and avoid anti-bot triggers.
- **Direct Telegram Integration**: Asynchronously dispatches formatted Markdown alerts using lightweight HTTP calls (`httpx`).
- **Cloud & CI/CD Ready**: Includes a pre-configured `Dockerfile` and a GitHub Actions workflow for scheduled or event-driven serverless runs.

---

## ⚠️ Security Notice

> [!IMPORTANT]
> **Never commit your active session cookies (`cookies.json`) to a public repository!**
> Anyone with access to your cookies can hijack your account session. Ensure `cookies.json` is listed in your `.gitignore` and pass cookies exclusively via GitHub Secrets or local `.env` files.

---

## 📦 Prerequisites

- **Python**: Version 3.10 or higher
- **Telegram Account**: A bot token from [@BotFather](https://t.me/BotFather) and your target `CHAT_ID`
- **Chromium / Playwright**: System dependencies (installed automatically via Playwright CLI)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/MohamedElmutasim/scrapy.git
cd scrapy
```

### 2. Create and Activate a Virtual Environment

```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory by copying the template below:

```ini
# Telegram Configuration
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
TELEGRAM_CHAT_ID="123456789"

# Scraper Target
TARGET_URL="https://www.facebook.com/groups/your_target_group_id/"

# Optional: Inline or Base64 Encoded Cookies (overrides local cookies.json)
# COOKIES_JSON='[{"name":"c_user","value":"...","domain":".facebook.com","path":"/"}]'
```

### Cookie Export Guide

To authenticate with target groups:
1. Log into your account in your browser.
2. Export your session cookies in JSON format using a browser extension (such as *EditThisCookie* or *Cookie-Editor*).
3. Save the exported JSON array into a local file named `cookies.json` (ensure it is ignored by git), or set it as the `COOKIES_JSON` environment variable.

---

## 🖥️ Usage

### 1. Running Locally

Once `.env` and `cookies.json` are set up:

```bash
python app.py
```

You will receive a notification in Telegram confirming that the scraper has started, followed by the summarized report of the latest posts.

---

### 2. Running via Docker

Build and run the container locally:

```bash
# Build the Docker image
docker build -t market-scraper .

# Run the container with environment variables
docker run --rm --env-file .env market-scraper
```

---

### 3. Running on GitHub Actions

You can trigger the scraper without running your own servers:

1. Move the workflow file into `.github/workflows/`:
   ```bash
   mkdir -p .github/workflows
   mv scrape.yml .github/workflows/scrape.yml
   ```
2. Navigate to your repository on GitHub: **Settings** > **Secrets and variables** > **Actions**.
3. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot API token.
   - `TELEGRAM_CHAT_ID`: Your personal or group chat ID.
   - `COOKIES_JSON`: Your exported Facebook cookies in JSON or Base64 format.
   - `TARGET_URL`: Default target group or forum URL.
4. Go to the **Actions** tab on GitHub, select **Event-Driven Market Research Scraper**, and click **Run workflow**.

---

## 📂 Project Structure

```
scrapy/
├── .github/
│   └── workflows/
│       └── scrape.yml        # GitHub Actions workflow (dispatch & webhook)
├── Dockerfile                # Jammy Ubuntu container with Playwright pre-installed
├── app.py                    # Core scraper, humanizer, and Telegram reporter
├── cookies.example.json      # Sample cookie schema template (sanitized)
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules (protects credentials & logs)
└── README.md                 # Project documentation
```

---

## 🗺️ Upcoming Roadmap

- [ ] **AI-Powered Deep Summarization**: Connect DeepSeek / OpenAI to generate semantic market insights, sentiment analysis, and pain-point extraction.
- [ ] **Message Splitting for Telegram**: Handle long responses exceeding Telegram's 4,096-character limit automatically.
- [ ] **Multi-Target Support**: Accept an array of URLs to scrape multiple groups sequentially or in parallel.
- [ ] **Health-Check Server**: Implement a lightweight FastAPI / aiohttp status endpoint on port 10000 for cloud PaaS deployments (Render, Koyeb).

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
