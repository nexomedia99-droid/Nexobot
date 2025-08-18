
from flask import Flask, jsonify
from threading import Thread
import time
import os

app = Flask('')

# Track bot status
bot_start_time = time.time()
bot_status = {
    "status": "starting",
    "uptime": 0,
    "last_check": time.time()
}

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!"

@app.route('/health')
def health():
    """Health check endpoint for UptimeRobot"""
    current_time = time.time()
    uptime = current_time - bot_start_time
    
    bot_status.update({
        "status": "online",
        "uptime": round(uptime, 2),
        "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
        "last_check": current_time,
        "bot_token_configured": bool(os.getenv("BOT_TOKEN")),
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY"))
    })
    
    return jsonify(bot_status)

@app.route('/status')
def status():
    """Detailed status endpoint"""
    return jsonify({
        "bot_name": "Telegram Bot",
        "status": "healthy",
        "uptime_seconds": round(time.time() - bot_start_time, 2),
        "environment": "production",
        "services": {
            "telegram_bot": "running",
            "gemini_ai": "connected" if os.getenv("GEMINI_API_KEY") else "not_configured",
            "database": "active"
        }
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong"

def run():
    app.run(host="0.0.0.0", port=8080, debug=False)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
    print("🌐 Keep-alive server started on http://0.0.0.0:8080")
    print("📊 Health check available at: /health")
    print("📈 Status endpoint available at: /status")
    print("🏓 Ping endpoint available at: /ping")
