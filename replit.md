# NexoBot

## Overview

NexoBot is a comprehensive Telegram bot designed for the NexoBuzz community platform. The system facilitates job applications for buzzer and influencer opportunities, manages user registrations, provides AI-powered assistance, and maintains a community leaderboard with gamification features. The bot enables users to earn points through various activities and apply for paid social media promotion jobs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Python Telegram Bot**: Built using python-telegram-bot library with conversation handlers for multi-step user interactions
- **Command-based Architecture**: Modular command handlers organized by functionality (admin, jobs, AI, registration)
- **State Management**: Uses conversation handlers to manage multi-step processes like user registration and job posting

### Database Layer
- **SQLite Database**: Local database storage with context managers for connection handling
- **User Management**: Stores user profiles, payment information, referral relationships, and point systems
- **Job System**: Manages job postings, applications, and applicant tracking
- **Badge/Achievement System**: Tracks user badges and achievements for gamification

### AI Integration
- **Google Gemini API**: Integrated AI assistant with conversational capabilities
- **Session Management**: Tracks individual AI chat sessions with context preservation
- **Group Message Processing**: Stores and analyzes group conversations for summaries

### Web Dashboard
- **Flask Application**: Real-time web dashboard for monitoring bot statistics
- **Live Metrics**: Tracks user registrations, AI requests, job applications, and system uptime
- **Theme Support**: Dark/light theme toggle with persistent user preferences
- **Chart Visualization**: Interactive charts for data visualization using Chart.js

### Access Control
- **Decorator-based Authorization**: Admin-only and registered-user-only command restrictions
- **Owner Privileges**: Special privileges for bot owner defined by environment variables
- **Privacy Protection**: Registration restricted to private chats for data security

### External Integrations
- **Telegram Groups**: Automated posting to specific group topics (Buzzer/Influencer/Payment)
- **Keep-alive Service**: Health monitoring endpoint for uptime services
- **Environment Configuration**: Secure configuration through environment variables

## External Dependencies

### APIs and Services
- **Telegram Bot API**: Core bot functionality and message handling
- **Google Gemini API**: AI-powered conversational assistant
- **UptimeRobot Integration**: Health check endpoints for monitoring

### Database
- **SQLite**: Embedded database for user data, jobs, applications, and achievements

### Third-party Libraries
- **python-telegram-bot**: Telegram bot framework
- **Flask**: Web dashboard framework
- **Chart.js**: Frontend data visualization
- **Bootstrap**: UI framework for responsive dashboard design

### Environment Variables
- `BOT_TOKEN`: Telegram bot authentication token
- `GEMINI_API_KEY`: Google Gemini API access key
- `OWNER_ID`: Bot owner's Telegram user ID for admin privileges
- `GEMINI_MODEL`: AI model configuration (defaults to gemini-2.5-flash)