from flask import Flask, render_template, jsonify, request
from threading import Thread
import time
import os
import sqlite3
from datetime import datetime, timedelta
from db import get_all_users, get_all_jobs, get_conn
import json
import logging

logger = logging.getLogger(__name__)

dashboard_app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure static and template directories exist
import os
if not os.path.exists('static'):
    os.makedirs('static')
if not os.path.exists('templates'):
    os.makedirs('templates')

# Global variables for tracking
dashboard_stats = {
    "bot_start_time": time.time(),
    "total_messages": 0,
    "ai_requests": 0,
    "registrations": 0,
    "errors": 0,
    "job_applications": 0,
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
    elif action_type == "job_apply":
        dashboard_stats["job_applications"] += 1

@dashboard_app.route('/')
def dashboard_home():
    """Main dashboard page"""
    return render_template('dashboard.html')

@dashboard_app.route('/api/stats')
def api_stats():
    """API endpoint for real-time statistics"""
    try:
        # Get database stats
        users = get_all_users()
        jobs = get_all_jobs()
        
        # Calculate uptime
        uptime_seconds = time.time() - dashboard_stats["bot_start_time"]
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        # Get recent activities
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Ensure activity_logs table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT,
                    user_id TEXT,
                    description TEXT
                )
            """)
            
            # Get recent activities (last 20)
            cur.execute("""
                SELECT timestamp, action_type, description, user_id
                FROM activity_logs 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            recent_activities = cur.fetchall()
        
        # Calculate job statistics
        active_jobs = len([job for job in jobs if job.get('status') == 'aktif'])
        closed_jobs = len([job for job in jobs if job.get('status') == 'close'])
        paid_jobs = len([job for job in jobs if job.get('status') == 'cair'])
        
        # Calculate user statistics
        total_points = sum(user.get('points', 0) for user in users)
        top_user = max(users, key=lambda x: x.get('points', 0)) if users else None
        
        # Environment status
        env_status = {
            "bot_token": "✅ Configured" if os.getenv("BOT_TOKEN") else "❌ Missing",
            "gemini_api": "✅ Configured" if os.getenv("GEMINI_API_KEY") else "❌ Missing",
            "owner_id": "✅ Configured" if os.getenv("OWNER_ID") else "❌ Missing"
        }
        
        # Performance metrics
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM promotions")
            total_promotions = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM promotions WHERE created_at >= date('now', '-7 days')")
            weekly_promotions = cur.fetchone()[0]

        stats = {
            "bot_status": "online",
            "uptime": f"{uptime_hours}h {uptime_minutes}m",
            "uptime_seconds": uptime_seconds,
            "total_users": len(users),
            "total_jobs": len(jobs),
            "active_jobs": active_jobs,
            "closed_jobs": closed_jobs,
            "paid_jobs": paid_jobs,
            "total_points": total_points,
            "total_promotions": total_promotions,
            "weekly_promotions": weekly_promotions,
            "total_messages": dashboard_stats["total_messages"],
            "ai_requests": dashboard_stats["ai_requests"],
            "registrations": dashboard_stats["registrations"],
            "job_applications": dashboard_stats["job_applications"],
            "errors": dashboard_stats["errors"],
            "avg_points_per_user": total_points / len(users) if users else 0,
            "last_activity": datetime.fromtimestamp(dashboard_stats["last_activity"]).strftime('%Y-%m-%d %H:%M:%S'),
            "environment_vars": env_status,
            "top_user": {
                "username": top_user['username'] if top_user else "N/A",
                "points": top_user.get('points', 0) if top_user else 0
            },
            "recent_activities": [
                {
                    "timestamp": activity[0],
                    "type": activity[1],
                    "description": activity[2],
                    "user_id": activity[3]
                } for activity in recent_activities
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/api/users')
def api_users():
    """API endpoint for user data"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '').strip()
        
        users = get_all_users()
        
        # Filter users by search term
        if search:
            users = [
                user for user in users 
                if search.lower() in user['username'].lower()
            ]
        
        # Paginate
        total = len(users)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_users = users[start_idx:end_idx]
        
        # Add additional stats for each user
        for user in paginated_users:
            from db import get_badges, get_total_applies, get_referrals_by_username
            user['badges'] = get_badges(user['user_id'])
            user['total_applies'] = get_total_applies(user['user_id'])
            user['referrals'] = len(get_referrals_by_username(user['username']))
        
        return jsonify({
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "users": paginated_users
        })
        
    except Exception as e:
        logger.error(f"Dashboard users error: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/api/jobs')
def api_jobs():
    """API endpoint for job data"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status', '')
        
        jobs = get_all_jobs()
        
        # Filter by status
        if status_filter:
            jobs = [job for job in jobs if job['status'] == status_filter]
        
        # Add applicant count for each job
        for job in jobs:
            from db import get_applicants_by_job
            applicants = get_applicants_by_job(job['id'])
            job['applicant_count'] = len(applicants)
        
        # Paginate
        total = len(jobs)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_jobs = jobs[start_idx:end_idx]
        
        return jsonify({
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "jobs": paginated_jobs
        })
        
    except Exception as e:
        logger.error(f"Dashboard jobs error: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/debug')
def debug_info():
    """Debug information endpoint"""
    try:
        import sys
        import platform
        
        debug_data = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": os.getcwd(),
            "static_folder": dashboard_app.static_folder,
            "template_folder": dashboard_app.template_folder,
            "static_folder_exists": os.path.exists('static'),
            "template_folder_exists": os.path.exists('templates'),
            "dashboard_html_exists": os.path.exists('templates/dashboard.html'),
            "dashboard_css_exists": os.path.exists('static/dashboard.css'),
            "dashboard_js_exists": os.path.exists('static/dashboard.js'),
            "port_info": "Running on 0.0.0.0:5000"
        }
        
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    try:
        # Get activity logs for the last 7 days
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Daily activity counts for the last 7 days
            cur.execute("""
                SELECT DATE(timestamp) as date, action_type, COUNT(*) as count
                FROM activity_logs 
                WHERE timestamp >= date('now', '-7 days')
                GROUP BY DATE(timestamp), action_type
                ORDER BY date DESC
            """)
            daily_activities = cur.fetchall()
            
            # User registration over time
            cur.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            registration_trend = cur.fetchall()
            
            # Job status distribution
            jobs = get_all_jobs()
            job_status_counts = {}
            for job in jobs:
                status = job['status']
                job_status_counts[status] = job_status_counts.get(status, 0) + 1
        
        # Prepare chart data
        chart_data = {
            "daily_activities": [
                {"date": row[0], "type": row[1], "count": row[2]}
                for row in daily_activities
            ],
            "registration_trend": [
                {"date": row[0], "count": row[1]}
                for row in registration_trend
            ],
            "job_status_distribution": job_status_counts
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        return jsonify({"error": str(e)}), 500

def log_activity(action_type, user_id=None, description=""):
    """Log activity to database"""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO activity_logs (action_type, user_id, description)
                VALUES (?, ?, ?)
            """, (action_type, user_id, description))
            conn.commit()
            
        # Update stats
        update_stats(action_type)
        
    except Exception as e:
        logger.error(f"Error logging activity: {e}")

def run_dashboard():
    """Run the dashboard Flask app"""
    try:
        # Ensure port 5000 is available
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            logger.warning("Port 5000 already in use, trying port 5001")
            dashboard_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False, threaded=True)
        else:
            dashboard_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"Dashboard server failed to start: {e}")
        print(f"❌ Dashboard error: {e}")

def start_dashboard():
    """Start the dashboard in a daemon thread"""
    try:
        t = Thread(target=run_dashboard, daemon=True)
        t.start()
        
        logger.info("Dashboard server started successfully")
        print("🌐 Dashboard started on http://0.0.0.0:5000")
        print("📊 Dashboard available at: /")
        print("📈 API Stats available at: /api/stats")
        print("👥 Users API available at: /api/users")
        print("💼 Jobs API available at: /api/jobs")
        print("📊 Analytics API available at: /api/analytics")
        
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        print(f"❌ Failed to start dashboard: {e}")
