
from flask import Flask, render_template, jsonify, request
from threading import Thread
import time
import os
import sqlite3
from datetime import datetime, timedelta
from db import get_all_users, get_all_jobs, get_conn
import json

dashboard_app = Flask(__name__, template_folder='templates')

# Global variables untuk tracking
dashboard_stats = {
    "bot_start_time": time.time(),
    "total_messages": 0,
    "ai_requests": 0,
    "registrations": 0,
    "errors": 0,
    "last_activity": time.time()
}

def update_stats(action_type):
    """Update statistics for dashboard"""
    global dashboard_stats
    dashboard_stats["last_activity"] = time.time()
    
    if action_type == "message":
        dashboard_stats["total_messages"] += 1
    elif action_type == "ai_request":
        dashboard_stats["ai_requests"] += 1
    elif action_type == "registration":
        dashboard_stats["registrations"] += 1
    elif action_type == "error":
        dashboard_stats["errors"] += 1

@dashboard_app.route('/')
def dashboard_home():
    return render_template('dashboard.html')

@dashboard_app.route('/api/stats')
def api_stats():
    """API endpoint untuk mendapatkan statistik real-time"""
    try:
        # Database stats
        users = get_all_users()
        jobs = get_all_jobs()
        
        # Calculate uptime
        uptime_seconds = time.time() - dashboard_stats["bot_start_time"]
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        # Get recent activity
        with get_conn() as conn:
            cur = conn.cursor()
            # Create activity log table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT,
                    user_id TEXT,
                    description TEXT
                )
            """)
            
            # Get recent activities
            cur.execute("""
                SELECT timestamp, action_type, description 
                FROM activity_logs 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            recent_activities = cur.fetchall()
        
        stats = {
            "bot_status": "online",
            "uptime": f"{uptime_hours}h {uptime_minutes}m",
            "uptime_seconds": uptime_seconds,
            "total_users": len(users),
            "total_jobs": len(jobs),
            "active_jobs": len([job for job in jobs if job.get('status') == 'aktif']),
            "total_messages": dashboard_stats["total_messages"],
            "ai_requests": dashboard_stats["ai_requests"],
            "errors": dashboard_stats["errors"],
            "last_activity": datetime.fromtimestamp(dashboard_stats["last_activity"]).strftime('%Y-%m-%d %H:%M:%S'),
            "environment_vars": {
                "bot_token": "✅ Configured" if os.getenv("BOT_TOKEN") else "❌ Missing",
                "gemini_api": "✅ Configured" if os.getenv("GEMINI_API_KEY") else "❌ Missing",
                "owner_id": "✅ Configured" if os.getenv("OWNER_ID") else "❌ Missing"
            },
            "recent_activities": [
                {
                    "timestamp": activity[0],
                    "type": activity[1],
                    "description": activity[2]
                } for activity in recent_activities
            ]
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/api/users')
def api_users():
    """API endpoint untuk data pengguna"""
    try:
        users = get_all_users()
        return jsonify({
            "total": len(users),
            "users": users[:20]  # Limit to 20 untuk performance
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/api/jobs')
def api_jobs():
    """API endpoint untuk data pekerjaan"""
    try:
        jobs = get_all_jobs()
        return jsonify({
            "total": len(jobs),
            "jobs": jobs[:20]  # Limit to 20 untuk performance
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_activity(action_type, user_id=None, description=""):
    """Log aktivitas ke database"""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO activity_logs (action_type, user_id, description)
                VALUES (?, ?, ?)
            """, (action_type, user_id, description))
            conn.commit()
        update_stats(action_type)
    except Exception as e:
        print(f"Error logging activity: {e}")

def run_dashboard():
    dashboard_app.run(host="0.0.0.0", port=5000, debug=False)

def start_dashboard():
    t = Thread(target=run_dashboard, daemon=True)
    t.start()
    print("🌐 Dashboard started on http://0.0.0.0:5000")
    print("📊 Dashboard available at: /")
    print("📈 API Stats available at: /api/stats")
