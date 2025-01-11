# ChickptNotify  System

A FastAPI-based backend service that scrapes newest job from chickpt.com and sends notifications to users based on their keyword subscriptions.

## System Architecture

### 1. Job Scraping (AWS Lambda)
- Periodic web scraping from chickpt.com using BeautifulSoup
- Job data extraction and normalization
- Redis pub/sub for real-time job notifications

### 2. Notification System
- Multi-channel notification support:
  - Email notifications via Gmail SMTP
  - Discord webhook integration (TODO)
  - Telegram bot integration (TODO)
- User-specific notification preferences
- Notification history tracking

### 3. Subscription Management
- Keyword-based job matching
- Redis-based keyword popularity ranking
- Case-insensitive keyword matching
- Duplicate subscription prevention

## Features

### Job Scraping
- AWS Lambda-based periodic job scraping from chickpt.com
- Automatic job detail extraction including title, salary, location, and work time

### Real-time Notification System
- Multi-channel notification support:
  - Email (Gmail SMTP)
  - Discord webhook (Todo)
  - Telegram bot (Todo)
- Redis pub/sub for real-time job notifications
- User-specific notification preferences

### Keyword Subscription
- Case-insensitive keyword matching
- Redis-based keyword popularity ranking

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Cache & Pub/Sub**: Redis
- **Cloud Service**: AWS
- **Authentication**: JWT
- **Containerization**: Docker
- **Python Version**: 3.10

## Project Structure

### Root Directory

### Key Directories and Files

#### `/app`
Main application directory containing:
- `models/` - SQLAlchemy database models
- `services/` - Business logic and core services
- `routers/` - FastAPI route handlers
- `schemas/` - Pydantic data models
- `dependencies/` - FastAPI dependencies
- `db/` - Database configuration

### `/alembic`
Database migration configuration

#### `lambda_function`
AWS Lambda function package for job scraping


Docker-related configurations:
- `Dockerfile` - Container build instructions
- `docker-compose.yml` - Multi-container setup for:
  - FastAPI application
  - PostgreSQL database
  - Redis Server

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Du411/chicknotify.git
cd chicknotify
```

### 2. Environment Setup

```bash
cp .env.example .env
```
and configure the environment variables

### 3. Build and start containers

```bash
docker compose up -d
```

API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
## TODO List
- [ ] Add Discord webhook integration
- [ ] Add Telegram bot integration
- [ ] Add Test
- [ ] Add CI/CD pipeline
- [ ] Add more features and improvements
