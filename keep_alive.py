from flask import Flask, jsonify, render_template_string
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

@app.route('/')
def home():
    """Main status page"""
    current_time = time.time()
    uptime = current_time - bot_start_time
    
    bot_status.update({
        "status": "online",
        "uptime": round(uptime, 2),
        "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
        "last_check": current_time
    })
    
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NexoBot Status</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            .status-card {
                background: rgba(255,255,255,0.15);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                border-left: 5px solid #4CAF50;
            }
            .status-online { border-left-color: #4CAF50; }
            .status-offline { border-left-color: #f44336; }
            .status-badge {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
                margin-left: 10px;
            }
            .badge-online { background: #4CAF50; }
            .badge-offline { background: #f44336; }
            h1 { text-align: center; margin-bottom: 30px; }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .info-item {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .info-value { font-size: 1.5em; font-weight: bold; margin-top: 5px; }
            .refresh-btn {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                margin: 10px 5px;
                transition: background 0.3s;
            }
            .refresh-btn:hover { background: #45a049; }
            .footer { text-align: center; margin-top: 30px; opacity: 0.8; }
        </style>
        <script>
            function refreshStatus() {
                location.reload();
            }
            
            // Auto refresh every 30 seconds
            setInterval(refreshStatus, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🤖 NexoBot Status Monitor</h1>
            
            <div class="status-card status-{{ 'online' if bot_status['status'] == 'online' else 'offline' }}">
                <h2>
                    Bot Status 
                    <span class="status-badge badge-{{ 'online' if bot_status['status'] == 'online' else 'offline' }}">
                        {{ bot_status['status'].upper() }}
                    </span>
                </h2>
                <p><strong>Uptime:</strong> {{ bot_status['uptime_human'] }}</p>
                <p><strong>Last Check:</strong> {{ last_check_time }}</p>
                <p><strong>Version:</strong> {{ bot_status['version'] }}</p>
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <div>⏱️ Uptime (seconds)</div>
                    <div class="info-value">{{ bot_status['uptime'] }}</div>
                </div>
                <div class="info-item">
                    <div>🔑 Bot Token</div>
                    <div class="info-value">{{ '✅ OK' if bot_token else '❌ Missing' }}</div>
                </div>
                <div class="info-item">
                    <div>🧠 Gemini API</div>
                    <div class="info-value">{{ '✅ OK' if gemini_api else '❌ Missing' }}</div>
                </div>
                <div class="info-item">
                    <div>👑 Owner ID</div>
                    <div class="info-value">{{ '✅ OK' if owner_id else '❌ Missing' }}</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <button class="refresh-btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                <button class="refresh-btn" onclick="window.open('/health', '_blank')">📊 Health Check</button>
                <button class="refresh-btn" onclick="window.open('/ping', '_blank')">🏓 Ping Test</button>
            </div>
            
            <div class="footer">
                <p>NexoBuzz Telegram Bot | Keep-Alive Server</p>
                <p>Monitoring uptime and health status</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(
        template, 
        bot_status=bot_status,
        last_check_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bot_status['last_check'])),
        bot_token=bool(os.getenv("BOT_TOKEN")),
        gemini_api=bool(os.getenv("GEMINI_API_KEY")),
        owner_id=bool(os.getenv("OWNER_ID"))
    )

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
        },
        "features": {
            "member_registration": "active",
            "job_system": "active", 
            "ai_assistant": "active",
            "admin_panel": "active",
            "dashboard": "active",
            "referral_system": "active",
            "badge_system": "active"
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
        "memory_usage": "N/A",  # Could implement with psutil if needed
        "last_updated": current_time
    }
    
    return jsonify(metrics)

@app.errorhandler(404)
def not_found(error):
    """Custom 404 page"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/status", "/ping", "/metrics"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 page"""
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
