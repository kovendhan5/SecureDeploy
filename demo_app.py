#!/usr/bin/env python3
"""
Enhanced Demo Application for PipeGuard
Provides a believable real-time monitoring showcase backed by a live data feeder.
"""

import atexit
import logging
import random
import secrets
import threading
from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
app.config['JSON_SORT_KEYS'] = False  # Preserve ordering for the UI payloads

# CORS configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)
limiter.init_app(app)

# Demo state -----------------------------------------------------------------
demo_generator = DemoDataGenerator()
data_lock = threading.Lock()
stop_event = threading.Event()
data_thread: threading.Thread | None = None

MAX_RUN_HISTORY = 200
RECENT_SAMPLE_SIZE = 40
DEFAULT_RECENT_WINDOW = 20

# Shared mutable state (must always be accessed with data_lock held)
demo_runs: List[Dict] = []
demo_anomalies: List[Dict] = []
demo_insights: Dict = {'patterns': [], 'predictions': [], 'recommendations': [], 'optimizations': []}


def _recalculate_state_locked() -> None:
    """Refresh anomalies and insights. Caller must hold data_lock."""
    global demo_anomalies, demo_insights

    if not demo_runs:
        demo_anomalies = []
        demo_insights = {'patterns': [], 'predictions': [], 'recommendations': [], 'optimizations': []}
        return

    recent_slice = demo_runs[-RECENT_SAMPLE_SIZE:] if len(demo_runs) > RECENT_SAMPLE_SIZE else list(demo_runs)
    demo_anomalies = demo_generator.detect_anomalies(recent_slice)
    demo_insights = demo_generator.generate_ai_insights(recent_slice, demo_anomalies)


def _append_run_locked(run: dict) -> None:
    """Append a pipeline run, trim history, and recompute derived data."""
    demo_runs.append(run)

    if len(demo_runs) > MAX_RUN_HISTORY:
        demo_runs.pop(0)

    _recalculate_state_locked()


def _build_stats_locked() -> Dict[str, float]:
    """Compile statistics used by the dashboard widgets."""
    total_runs = len(demo_runs)
    recent_runs = demo_runs[-DEFAULT_RECENT_WINDOW:]

    if recent_runs:
        success_count = sum(1 for run in recent_runs if run['status'] == 'success')
        success_rate = round((success_count / len(recent_runs)) * 100, 1)
        avg_duration = round(sum(run['duration'] for run in recent_runs) / len(recent_runs), 1)
    else:
        success_rate = 0.0
        avg_duration = 0.0

    return {
        'total_runs': total_runs,
        'success_rate': success_rate,
        'avg_duration': avg_duration,
        'active_alerts': len(demo_anomalies)
    }


def _initialize_demo_state() -> None:
    """Populate the in-memory store with an initial history."""
    with data_lock:
        demo_runs.extend(demo_generator.generate_runs(30))
        _recalculate_state_locked()


def _data_feeder_loop() -> None:
    """Background thread that continuously generates fresh runs."""
    logger.info("Demo data feeder thread started")

    while not stop_event.is_set():
        delay = random.uniform(6, 12)
        if stop_event.wait(delay):
            break

        with data_lock:
            new_run = demo_generator.generate_run()
            _append_run_locked(new_run)

        logger.debug("Generated demo run %s (%s)", new_run['run_id'], new_run['status'])

    logger.info("Demo data feeder thread stopped")


def _start_data_feeder_if_needed() -> None:
    """Launch the feeder thread once traffic hits the app."""
    global data_thread

    if data_thread and data_thread.is_alive():
        return

    data_thread = threading.Thread(
        target=_data_feeder_loop,
        name="pipeguard-demo-feeder",
        daemon=True
    )
    data_thread.start()


def _shutdown_background_tasks() -> None:
    """Stop background tasks gracefully on process exit."""
    stop_event.set()

    if data_thread and data_thread.is_alive():
        data_thread.join(timeout=5)


_initialize_demo_state()
atexit.register(_shutdown_background_tasks)


# Flask hooks ----------------------------------------------------------------
@app.before_request
def _on_each_request() -> None:
    """Ensure data feeder is running for every incoming request."""
    _start_data_feeder_if_needed()


@app.after_request
def add_security_headers(response):
    """Attach security headers to each response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# Routes ---------------------------------------------------------------------
@app.route('/')
def index():
    """Render the main dashboard."""
    logger.info("Dashboard accessed")

    with data_lock:
        runs = sorted(demo_runs, key=lambda x: x['id'], reverse=True)[:DEFAULT_RECENT_WINDOW]
        stats = _build_stats_locked()
        anomalies = list(demo_anomalies[:6])
        insights = dict(demo_insights)

        initial_payload = {
            'runs': runs,
            'stats': stats,
            'anomalies': anomalies,
            'insights': insights
        }

    metrics = demo_generator.generate_real_time_metrics()
    initial_payload['metrics'] = metrics

    return render_template(
        'demo_dashboard.html',
        runs=runs,
        anomalies=anomalies,
        insights=insights,
        stats=stats,
        metrics=metrics,
        initial_data=initial_payload,
        auto_refresh_interval=10,
        demo_mode=True
    )


@app.route('/api/live-update')
@limiter.limit("120 per minute")
def live_update():
    """Return a live payload allowing the frontend to update in place."""
    metrics = demo_generator.generate_real_time_metrics()

    with data_lock:
        if random.random() < 0.1:
            _append_run_locked(demo_generator.generate_run())

        runs = sorted(demo_runs, key=lambda x: x['id'], reverse=True)[:DEFAULT_RECENT_WINDOW]
        stats = _build_stats_locked()
        anomalies = list(demo_anomalies[:6])
        insights = dict(demo_insights)

    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'runs': runs,
        'anomalies': anomalies,
        'insights': insights,
        'metrics': metrics
    })


@app.route('/api/runs')
@limiter.limit("60 per minute")
def get_runs():
    """Return the latest pipeline runs."""
    limit = request.args.get('limit', DEFAULT_RECENT_WINDOW, type=int)

    with data_lock:
        runs = sorted(demo_runs, key=lambda x: x['id'], reverse=True)[:limit]
        total = len(demo_runs)

    return jsonify({'success': True, 'runs': runs, 'total': total})


@app.route('/api/anomalies')
@limiter.limit("60 per minute")
def get_anomalies():
    """Return the current anomaly list."""
    with data_lock:
        anomalies = list(demo_anomalies)

    return jsonify({'success': True, 'anomalies': anomalies, 'total': len(anomalies)})


@app.route('/api/insights')
@limiter.limit("60 per minute")
def get_insights():
    """Return the AI-powered insights snapshot."""
    with data_lock:
        insights = dict(demo_insights)

    return jsonify({'success': True, 'insights': insights})


@app.route('/api/metrics')
@limiter.limit("120 per minute")
def get_metrics():
    """Return infrastructure metrics used for the live status panel."""
    metrics = demo_generator.generate_real_time_metrics()

    return jsonify({'success': True, 'metrics': metrics, 'timestamp': datetime.now().isoformat()})


@app.route('/api/add-demo-run')
@limiter.limit("20 per minute")
def add_demo_run():
    """Allow viewers to inject a manual pipeline run."""
    status = request.args.get('status', None)
    new_run = demo_generator.generate_run(status)

    with data_lock:
        _append_run_locked(new_run)

    return jsonify({'success': True, 'run': new_run, 'message': 'Demo run added successfully'})


@app.route('/health')
def health():
    """Simple health probe."""
    with data_lock:
        runs_count = len(demo_runs)

    return jsonify({
        'status': 'healthy',
        'demo_mode': True,
        'timestamp': datetime.now().isoformat(),
        'runs_count': runs_count
    })


# Error handlers -------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal error: %s", error)
    return jsonify({'error': 'Internal server error'}), 500


# Entrypoint -----------------------------------------------------------------
if __name__ == '__main__':
    with data_lock:
        stats_preview = _build_stats_locked()
        recommendations = len(demo_insights.get('recommendations', []))

    print("🚀 Starting PipeGuard Demo Application")
    print("=" * 60)
    print("📊 Demo Mode: Enabled")
    print(f"📈 Runs staged: {stats_preview['total_runs']}")
    print(f"⚠️  Active alerts: {stats_preview['active_alerts']}")
    print(f"🤖 Recommendations ready: {recommendations}")
    print("=" * 60)
    print("🌐 Access the dashboard at: http://localhost:8080")
    print("📡 API endpoints available at: http://localhost:8080/api/*")
    print("=" * 60)
    print("\n✨ Press Ctrl+C to stop\n")

    _start_data_feeder_if_needed()

    app.run(host='0.0.0.0', port=8080, debug=False)
