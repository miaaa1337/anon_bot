# 👥 AnonBot

An asynchronous, production-oriented Telegram bot engineered for local internet communities, featuring custom moderation layers and in-memory rate limiting.

---

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **Framework:** aiogram 3 (Fully Asynchronous Architecture)
* **Database:** PostgreSQL
* **Database Driver:** asyncpg (Asynchronous Connection Pooling)
* **Configuration:** python-dotenv (Strict Environment Isolation)
* **Deployment:** ## The bot was deployed on an Ubuntu VPS and run as a persistent systemd service. Docker and Docker Compose are also included for reproducible local setup.

---

## 🚀 Key Architectural Features

1. **In-Memory Rate Limiting (Throttling):** Tracks recent message timestamps in memory to prevent spam and message flooding.
2. **Automated Content Moderation:** Built a custom bad-words filtration mechanism utilizing in-memory caching to instantly intercept restricted content before message forwarding occurs.
3. **Relational Data Persistence:** Designed a reliable database schema in PostgreSQL to manage user states, route anonymous conversations, and maintain security logs securely.
4. **Production Deployment:** Runs as a long-lived service on Ubuntu using systemd, with configuration stored in environment variables.

## 📦 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/miaaa1337/anon_bot.git
cd anon_bot
```

### 2. Configure Environment Variables
Copy the example configuration file and fill in your actual credentials (tokens, database credentials, etc.):
```bash
cp .env.example .env
```
*Note*: The .env file contains sensitive data and is completely excluded from Git tracking via .gitignore.

## 💡 Choose Your Deployment Method:

### 🐳 Option A: Fast Run with Docker & Docker Compose (Recommended)
```bash
docker-compose up --build -d
```

### 🐍 Option B: Manual Setup (Local Virtual Environment)
### Initialize Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```
