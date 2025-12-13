#!/usr/bin/env python3
"""
Enhanced Demo Application for PipeGuard
Shows real-time pipeline monitoring with live sample data
"""

from flask import Flask, render_template, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os
import secrets
import logging
from datetime import datetime, timedelta
import random
from demo_data_generator import DemoDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['DEMO_MODE'] = True

# CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)
limiter.init_app(app)

# Initialize demo data generator
demo_generator = DemoDataGenerator()

# Generate initial demo data
demo_runs = demo_generator.generate_runs(25)
demo_anomalies = demo_generator.detect_anomalies(demo_runs)
demo_insights = demo_generator.generate_ai_insights(demo_runs, demo_anomalies)

@app.after_request
def add_security_headers(response):
    """Add security headers to responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    """Render the main dashboard"""
    logger.info("Dashboard accessed")
    
    # Get latest runs for display
    runs = sorted(demo_runs, key=lambda x: x['id'], reverse=True)[:20]
    
    # Calculate statistics
    total_runs = len(demo_runs)
    success_count = sum(1 for run in demo_runs if run['status'] == 'success')
    success_rate = (success_count / total_runs * 100) if total_runs > 0 else 0
    avg_duration = sum(run['duration'] for run in demo_runs) / total_runs if total_runs > 0 else 0
    
    return render_template('demo_dashboard.html',
                         runs=runs,
                         anomalies=demo_anomalies[:5],
                         insights=demo_insights,
                         stats={
                             'total_runs': total_runs,
                             'success_rate': success_rate,
                             'avg_duration': avg_duration,
                             'active_alerts': len(demo_anomalies)
                         },
                         demo_mode=True)

@app.route('/api/live-update')
@limiter.limit("60 per minute")
def live_update():
    """Get live update for real-time dashboard"""
    # Generate new run with some probability
    if random.random() < 0.3:  # 30% chance of new run
        new_run = demo_generator.generate_run()
        demo_runs.append(new_run)
        
        # Keep only recent runs
        if len(demo_runs) > 50:
            demo_runs.pop(0)
        
        # Update anomalies
        global demo_anomalies, demo_insights
        demo_anomalies = demo_generator.detect_anomalies(demo_runs[-20:])
        demo_insights = demo_generator.generate_ai_insights(demo_runs[-20:], demo_anomalies)
    
    # Get current metrics
    metrics = demo_generator.generate_real_time_metrics()
    
    # Calculate current statistics
    recent_runs = demo_runs[-20:]
    total_runs = len(demo_runs)
    success_count = sum(1 for run in recent_runs if run['status'] == 'success')
    success_rate = (success_count / len(recent_runs) * 100) if recent_runs else 0
    avg_duration = sum(run['duration'] for run in recent_runs) / len(recent_runs) if recent_runs else 0
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'stats': {
            'total_runs': total_runs,
            'success_rate': round(success_rate, 1),
            'avg_duration': round(avg_duration, 1),
            'active_alerts': len(demo_anomalies)
        },
        'latest_run': demo_runs[-1] if demo_runs else None,
        'metrics': metrics,
        'anomaly_count': len(demo_anomalies)
    })

@app.route('/api/runs')
@limiter.limit("30 per minute")
def get_runs():
    """Get all pipeline runs"""
    limit = request.args.get('limit', 20, type=int)
    runs = sorted(demo_runs, key=lambda x: x['id'], reverse=True)[:limit]
    
    return jsonify({
        'success': True,
        'runs': runs,
        'total': len(demo_runs)
    })

@app.route('/api/anomalies')
@limiter.limit("30 per minute")
def get_anomalies():
    """Get detected anomalies"""
    return jsonify({
        'success': True,
        'anomalies': demo_anomalies,
        'total': len(demo_anomalies)
    })

@app.route('/api/insights')
@limiter.limit("30 per minute")
def get_insights():
    """Get AI-powered insights"""
    return jsonify({
        'success': True,
        'insights': demo_insights
    })

@app.route('/api/metrics')
@limiter.limit("60 per minute")
def get_metrics():
    """Get current system metrics"""
    metrics = demo_generator.generate_real_time_metrics()
    
    return jsonify({
        'success': True,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/add-demo-run')
@limiter.limit("10 per minute")
def add_demo_run():
    """Manually add a demo run (for demonstration purposes)"""
    status = request.args.get('status', None)
    new_run = demo_generator.generate_run(status)
    demo_runs.append(new_run)
    
    # Update anomalies
    global demo_anomalies, demo_insights
    demo_anomalies = demo_generator.detect_anomalies(demo_runs[-20:])
    demo_insights = demo_generator.generate_ai_insights(demo_runs[-20:], demo_anomalies)
    
    return jsonify({
        'success': True,
        'run': new_run,
        'message': 'Demo run added successfully'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'demo_mode': True,
        'timestamp': datetime.now().isoformat(),
        'runs_count': len(demo_runs)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting PipeGuard Demo Application")
    print("=" * 60)
    print("📊 Demo Mode: Enabled")
    print(f"📈 Initial runs generated: {len(demo_runs)}")
    print(f"⚠️  Anomalies detected: {len(demo_anomalies)}")
    print(f"🤖 AI insights available: {len(demo_insights['recommendations'])}")
    print("=" * 60)
    print("🌐 Access the dashboard at: http://localhost:8080")
    print("📡 API endpoints available at: http://localhost:8080/api/*")
    print("=" * 60)
    print("\n✨ Press Ctrl+C to stop\n")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )
