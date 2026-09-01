# 👥 AnonBot

An asynchronous Telegram bot for local communities with anonymous messaging, automated moderation, rate limiting, and PostgreSQL persistence.

## 🛠 Tech Stack

- Python 3.11+
- aiogram 3
- PostgreSQL
- asyncpg
- python-dotenv
- Docker / Docker Compose
- Ubuntu Linux / systemd

## 🚀 Key Features

1. **In-Memory Rate Limiting**  
   Tracks recent message timestamps in memory to prevent spam and message flooding.

2. **Automated Content Moderation**  
   Filters restricted words and content before messages are forwarded.

3. **PostgreSQL Persistence**  
   Stores user state, anonymous conversation routing data, and moderation-related records.

4. **Production Deployment**  
   Deployed on an Ubuntu VPS and run as a persistent systemd service.

## 📦 Installation & Local Setup

### Clone the Repository

```
git clone https://github.com/miaaa1337/anon_bot.git
cd anon_bot
```

### Configure Environment Variables

```
cp .env.example .env
```

Fill in the required bot token and database credentials.

### Run with Docker

```
docker-compose up --build -d
```

### Manual Local Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Deployment

The bot was deployed on an Ubuntu VPS and run as a persistent systemd service.

Docker and Docker Compose are included for reproducible local setup.
