from flask import Flask, jsonify, redirect
from threading import Thread
import time
import os
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Track bot status
bot_start_time = time.time()
bot_status = {
    "status": "starting",
    "uptime": 0,
    "last_check": time.time(),
    "version": "2.0.0"
}

# Redirect root ke dashboard utama
@app.route('/')
def home():
    return redirect("http://0.0.0.0:5000/")  # arahkan ke dashboard.py

@app.route('/health')
def health():
    """Health check endpoint for monitoring services"""
    current_time = time.time()
    uptime = current_time - bot_start_time

    health_status = {
        "status": "healthy",
        "timestamp": current_time,
        "uptime_seconds": round(uptime, 2),
        "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        "version": "2.0.0",
        "environment": {
            "bot_token_configured": bool(os.getenv("BOT_TOKEN")),
            "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
            "owner_id_configured": bool(os.getenv("OWNER_ID"))
        },
        "services": {
            "telegram_bot": "running",
            "gemini_ai": "connected" if os.getenv("GEMINI_API_KEY") else "not_configured",
            "database": "active",
            "web_dashboard": "running"
        }
    }

    # Update global status
    bot_status.update({
        "status": "online",
        "uptime": uptime,
        "uptime_human": health_status["uptime_human"],
        "last_check": current_time
    })

    return jsonify(health_status)

@app.route('/status')
def status():
    """Detailed status endpoint"""
    current_time = time.time()
    uptime = current_time - bot_start_time

    detailed_status = {
        "service": "NexoBot Telegram Bot",
        "status": "operational",
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m",
        "environment": "production",
        "last_restart": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(bot_start_time)),
        "current_time": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(current_time)),
        "configuration": {
            "bot_token": "✅ Configured" if os.getenv("BOT_TOKEN") else "❌ Missing",
            "gemini_api": "✅ Configured" if os.getenv("GEMINI_API_KEY") else "❌ Missing",
            "owner_id": "✅ Configured" if os.getenv("OWNER_ID") else "❌ Missing"
        }
    }

    return jsonify(detailed_status)

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({
        "message": "pong",
        "timestamp": time.time(),
        "status": "ok"
    })

@app.route('/metrics')
def metrics():
    """Basic metrics endpoint"""
    current_time = time.time()
    uptime = current_time - bot_start_time

    try:
        from db import get_all_users, get_all_jobs
        users_count = len(get_all_users())
        jobs_count = len(get_all_jobs())
    except:
        users_count = 0
        jobs_count = 0

    metrics = {
        "uptime_seconds": round(uptime, 2),
        "total_users": users_count,
        "total_jobs": jobs_count,
        "memory_usage": "N/A",  # Bisa pakai psutil kalau mau lebih detail
        "last_updated": current_time
    }

    return jsonify(metrics)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/status", "/ping", "/metrics"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong on our end",
        "status": "error"
    }), 500

def run():
    """Run the Flask keep-alive server"""
    try:
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Keep-alive server failed to start: {e}")

def keep_alive():
    """Start the keep-alive server in a daemon thread"""
    try:
        t = Thread(target=run, daemon=True)
        t.start()

        logger.info("Keep-alive server started successfully")
        print("🌐 Keep-alive server started on http://0.0.0.0:8080")
        print("📊 Health check available at: /health")
        print("📈 Status endpoint available at: /status") 
        print("🏓 Ping endpoint available at: /ping")
        print("📊 Metrics available at: /metrics")

    except Exception as e:
        logger.error(f"Failed to start keep-alive server: {e}")
        print(f"❌ Failed to start keep-alive server: {e}")
