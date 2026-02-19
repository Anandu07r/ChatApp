# Real-Time Chat Application

A production-ready real-time private chat application built with Django, Django Channels, and WebSocket.

## Features
- **Real-Time Messaging**: Instant message delivery using WebSockets.
- **Private Chat**: 1-on-1 secure chat rooms.
- **User Status**: Real-time online/offline indicators.
- **Message History**: Persistent chat history stored in SQLite.
- **Read Receipts**: Visual indicators for sent and read messages.
- **Secure Auth**: Custom user model with robust authentication.

## Tech Stack
- **Backend**: Python, Django, Django Channels (Daphne)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Real-Time**: WebSocket, Redis (optional, InMemory used by default)

## Setup Instructions

### 1. Clone & Env Setup
```bash
git clone <repo_url>
cd chat_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Migrations
I have manually created the migration files. Run this to create the tables:
```bash
python manage.py migrate
```
If you still see "no such table", try:
```bash
python manage.py migrate users
python manage.py migrate
```

### 4. Run Server (ASGI)
This app uses ASGI for WebSocket support.
```bash
python manage.py runserver
```
or for production-like run:
```bash
daphne -p 8000 chat_app.asgi:application
```

## Structure
- `chat_app/`: Project settings & configuration.
- `users/`: Authentication & User models.
- `chat/`: Chat views, WebSocket consumers, and models.
- `templates/`: HTML templates.
