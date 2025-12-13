#!/usr/bin/env python3
"""
Demo Data Generator for PipeGuard
Generates realistic sample data for demonstration purposes
"""

import random
import time
from datetime import datetime, timedelta

class DemoDataGenerator:
    """Generate realistic demo data for pipeline monitoring"""
    
    def __init__(self):
        self.run_counter = 1
        self.branches = ['main', 'develop', 'feature/user-auth', 'feature/dashboard-v2', 'hotfix/db-connection', 'release/v2.1.0']
        self.workflows = [
            {'name': 'Build & Test', 'file': '.github/workflows/ci.yml'},
            {'name': 'Deploy to Production', 'file': '.github/workflows/deploy-prod.yml'},
            {'name': 'Security Scan', 'file': '.github/workflows/security.yml'},
            {'name': 'Integration Tests', 'file': '.github/workflows/integration.yml'},
            {'name': 'Docker Build', 'file': '.github/workflows/docker.yml'},
        ]
        self.authors = [
            {'name': 'Sarah Chen', 'username': 'schen'},
            {'name': 'Marcus Johnson', 'username': 'mjohnson'},
            {'name': 'Priya Patel', 'username': 'ppatel'},
            {'name': 'Alex Rivera', 'username': 'arivera'},
            {'name': 'Jordan Kim', 'username': 'jkim'},
        ]
        self.commit_messages = [
            'fix: resolve database connection timeout issue',
            'feat: add user authentication middleware',
            'chore: update dependencies to latest versions',
            'fix: correct pagination offset calculation',
            'feat: implement rate limiting for API endpoints',
            'refactor: optimize query performance',
            'docs: update API documentation',
            'test: add unit tests for auth service',
            'fix: handle edge case in data validation',
            'feat: add webhook notification support',
        ]
        self.pipeline_steps = {
            'Build & Test': [
                {'name': 'Checkout', 'command': 'git checkout $GITHUB_SHA', 'duration': (2, 5)},
                {'name': 'Setup Node.js', 'command': 'nvm use 18.17.0 && npm ci', 'duration': (15, 30)},
                {'name': 'Lint', 'command': 'npm run lint -- --max-warnings 0', 'duration': (8, 15)},
                {'name': 'Unit Tests', 'command': 'npm run test:unit -- --coverage', 'duration': (20, 45)},
                {'name': 'Build', 'command': 'npm run build -- --mode production', 'duration': (25, 50)},
            ],
            'Deploy to Production': [
                {'name': 'Checkout', 'command': 'git checkout $GITHUB_SHA', 'duration': (2, 5)},
                {'name': 'Setup AWS CLI', 'command': 'aws configure set region us-east-1', 'duration': (3, 8)},
                {'name': 'Build Docker Image', 'command': 'docker build -t app:$SHA --cache-from app:latest .', 'duration': (30, 60)},
                {'name': 'Push to ECR', 'command': 'docker push $ECR_REPO:$SHA', 'duration': (15, 30)},
                {'name': 'Deploy to EKS', 'command': 'kubectl apply -f k8s/ && kubectl rollout status deployment/app', 'duration': (20, 45)},
                {'name': 'Health Check', 'command': 'curl -f https://api.example.com/health || exit 1', 'duration': (5, 15)},
            ],
            'Security Scan': [
                {'name': 'Checkout', 'command': 'git checkout $GITHUB_SHA', 'duration': (2, 5)},
                {'name': 'SAST Scan', 'command': 'semgrep --config auto --json -o sast-results.json .', 'duration': (25, 50)},
                {'name': 'Dependency Audit', 'command': 'npm audit --audit-level=high && pip-audit', 'duration': (10, 20)},
                {'name': 'Secret Detection', 'command': 'gitleaks detect --source . --report-format json', 'duration': (8, 15)},
                {'name': 'Container Scan', 'command': 'trivy image --severity HIGH,CRITICAL app:latest', 'duration': (15, 30)},
            ],
            'Integration Tests': [
                {'name': 'Checkout', 'command': 'git checkout $GITHUB_SHA', 'duration': (2, 5)},
                {'name': 'Setup Services', 'command': 'docker-compose -f docker-compose.test.yml up -d', 'duration': (20, 40)},
                {'name': 'Wait for DB', 'command': 'dockerize -wait tcp://localhost:5432 -timeout 60s', 'duration': (5, 15)},
                {'name': 'Run Migrations', 'command': 'python manage.py migrate --no-input', 'duration': (5, 12)},
                {'name': 'Integration Tests', 'command': 'pytest tests/integration/ -v --tb=short', 'duration': (45, 90)},
                {'name': 'Cleanup', 'command': 'docker-compose -f docker-compose.test.yml down -v', 'duration': (5, 10)},
            ],
            'Docker Build': [
                {'name': 'Checkout', 'command': 'git checkout $GITHUB_SHA', 'duration': (2, 5)},
                {'name': 'Setup QEMU', 'command': 'docker run --rm --privileged multiarch/qemu-user-static --reset -p yes', 'duration': (3, 8)},
                {'name': 'Setup Buildx', 'command': 'docker buildx create --use --name multiarch', 'duration': (2, 5)},
                {'name': 'Build Multi-arch', 'command': 'docker buildx build --platform linux/amd64,linux/arm64 -t app:$SHA .', 'duration': (60, 120)},
                {'name': 'Push to Registry', 'command': 'docker push $REGISTRY/app:$SHA', 'duration': (15, 30)},
            ],
        }
        self.failure_reasons = [
            {'step': 'Unit Tests', 'error': 'FAIL src/auth/auth.test.ts\n  ✕ should validate JWT token (45ms)\n    Expected: true\n    Received: false'},
            {'step': 'Lint', 'error': 'error  Unexpected console statement  no-console\n  12 errors and 3 warnings found'},
            {'step': 'Build', 'error': "Module not found: Error: Can't resolve './utils/helpers'\n  at /app/src/index.ts:15:1"},
            {'step': 'Deploy to EKS', 'error': 'error: deployment "app" exceeded its progress deadline'},
            {'step': 'Integration Tests', 'error': 'FAILED tests/integration/test_api.py::test_user_creation\n  AssertionError: 500 != 201'},
            {'step': 'Container Scan', 'error': 'CRITICAL: CVE-2024-1234 found in package openssl-1.1.1\n  Fixed version: 1.1.1w'},
        ]
        
    def generate_run(self, status=None, offset_minutes=0):
        """Generate a single pipeline run with realistic data"""
        if status is None:
            # 78% success rate for realistic demo
            status = 'success' if random.random() < 0.78 else 'failure'
        
        workflow = random.choice(self.workflows)
        workflow_name = workflow['name']
        workflow_file = workflow['file']
        author = random.choice(self.authors)
        commit_msg = random.choice(self.commit_messages)
        
        # Generate pipeline steps with realistic timing
        steps = []
        total_duration = 0
        failed_step = None
        failure_log = None
        
        pipeline_steps = self.pipeline_steps.get(workflow_name, self.pipeline_steps['Build & Test'])
        
        for i, step_template in enumerate(pipeline_steps):
            step_duration = random.randint(*step_template['duration'])
            step_status = 'success'
            step_log = f"$ {step_template['command']}\n✓ Completed in {step_duration}s"
            
            # If this run failed and we haven't hit the failing step yet
            if status == 'failure' and failed_step is None:
                # 30% chance each step fails, higher for later steps
                fail_chance = 0.15 + (i * 0.1)
                if random.random() < fail_chance or i == len(pipeline_steps) - 1:
                    step_status = 'failure'
                    failed_step = step_template['name']
                    # Find matching failure reason or generate generic one
                    matching_failures = [f for f in self.failure_reasons if f['step'] == step_template['name']]
                    if matching_failures:
                        failure_log = random.choice(matching_failures)['error']
                    else:
                        failure_log = f"Error: Process exited with code 1\n  Command failed: {step_template['command']}"
                    step_log = f"$ {step_template['command']}\n✗ Failed after {step_duration}s\n\n{failure_log}"
            
            if step_status == 'success':
                total_duration += step_duration
            else:
                total_duration += step_duration
                # Skip remaining steps after failure
                steps.append({
                    'name': step_template['name'],
                    'command': step_template['command'],
                    'status': step_status,
                    'duration': step_duration,
                    'log': step_log
                })
                # Add skipped steps
                for remaining in pipeline_steps[i+1:]:
                    steps.append({
                        'name': remaining['name'],
                        'command': remaining['command'],
                        'status': 'skipped',
                        'duration': 0,
                        'log': '⊘ Skipped due to previous failure'
                    })
                break
            
            steps.append({
                'name': step_template['name'],
                'command': step_template['command'],
                'status': step_status,
                'duration': step_duration,
                'log': step_log
            })
        
        # Add some variance to duration
        if random.random() < 0.1:  # 10% chance of slow build
            total_duration += random.randint(60, 180)
        
        finished_at = datetime.now() - timedelta(minutes=offset_minutes)
        started_at = finished_at - timedelta(seconds=total_duration)
        commit_sha = f'{random.randint(0x100000, 0xFFFFFF):06x}'

        run = {
            'id': self.run_counter,
            'run_id': f'run-{self.run_counter}',
            'run_number': 1000 + self.run_counter,
            'status': status,
            'conclusion': status,
            'duration': total_duration,
            'branch': random.choice(self.branches),
            'workflow': workflow_name,
            'workflow_file': workflow_file,
            'author': author['name'],
            'author_username': author['username'],
            'commit_message': commit_msg,
            'timestamp': finished_at.isoformat(),
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'commit': commit_sha,
            'commit_url': f'https://github.com/example/app/commit/{commit_sha}',
            'run_url': f'https://github.com/example/app/actions/runs/{1000 + self.run_counter}',
            'steps': steps,
            'failed_step': failed_step,
            'failure_log': failure_log,
            'event': random.choice(['push', 'pull_request', 'schedule', 'workflow_dispatch']),
            'runner': f'ubuntu-runner-{random.randint(1, 8)}',
        }
        
        self.run_counter += 1
        return run
    
    def generate_runs(self, count=20):
        """Generate multiple pipeline runs"""
        runs = []
        offset = random.randint(count * 4, count * 8)

        for _ in range(count):
            runs.append(self.generate_run(offset_minutes=offset))
            offset = max(0, offset - random.randint(5, 12))

        return runs
    
    def detect_anomalies(self, runs):
        """Detect anomalies in the generated runs"""
        anomalies = []
        
        if not runs:
            return anomalies
        
        # Calculate average duration
        avg_duration = sum(run['duration'] for run in runs) / len(runs)
        
        for run in runs:
            # Check for slow builds
            if run['duration'] > avg_duration * 1.5:
                anomalies.append({
                    'run_id': run['run_id'],
                    'type': 'Slow Build',
                    'issue': f'Build duration ({run["duration"]}s) is significantly higher than average ({avg_duration:.0f}s)',
                    'fix': 'Consider optimizing build steps or checking for resource constraints',
                    'severity': 'warning'
                })
            
            # Check for failures
            if run['status'] == 'failure':
                anomalies.append({
                    'run_id': run['run_id'],
                    'type': 'Build Failure',
                    'issue': f'Pipeline failed on {run["branch"]} branch',
                    'fix': f'Review logs for run #{run["id"]} and fix failing tests or build errors',
                    'severity': 'critical'
                })
        
        # Check for failure patterns
        recent_runs = runs[-5:]
        failure_count = sum(1 for run in recent_runs if run['status'] == 'failure')
        
        if failure_count >= 3:
            anomalies.append({
                'run_id': 'pattern-detection',
                'type': 'High Failure Rate',
                'issue': f'{failure_count} out of last 5 builds failed - potential systemic issue',
                'fix': 'Investigate common factors: dependency changes, infrastructure issues, or test flakiness',
                'severity': 'critical'
            })
        
        return anomalies
    
    def generate_ai_insights(self, runs, anomalies):
        """Generate AI-powered insights"""
        insights = {
            'patterns': [],
            'predictions': [],
            'recommendations': [],
            'optimizations': []
        }
        
        if not runs:
            return insights
        
        # Pattern detection
        success_rate = sum(1 for run in runs if run['status'] == 'success') / len(runs)
        avg_duration = sum(run['duration'] for run in runs) / len(runs)
        
        if success_rate < 0.7:
            insights['patterns'].append('⚠️ Success rate below 70% - stability issues detected')
        else:
            insights['patterns'].append('✅ Consistent build success rate - stable pipeline')
        
        if avg_duration > 150:
            insights['patterns'].append('⚠️ Average build time exceeds 2.5 minutes')
        
        # Predictions
        recent_trend = [run['duration'] for run in runs[-5:]]
        if len(recent_trend) >= 3:
            if recent_trend[-1] > recent_trend[-2] > recent_trend[-3]:
                insights['predictions'].append('📈 Build times trending upward - performance degradation likely')
            elif recent_trend[-1] < recent_trend[-2] < recent_trend[-3]:
                insights['predictions'].append('📉 Build times improving - optimizations working')
        
        # Recommendations
        if success_rate < 0.8:
            insights['recommendations'].append({
                'title': 'Improve Test Reliability',
                'description': 'Consider adding retry logic for flaky tests and improving test isolation',
                'impact': 'high',
                'effort': 'medium'
            })
        
        if avg_duration > 120:
            insights['recommendations'].append({
                'title': 'Optimize Build Pipeline',
                'description': 'Enable caching for dependencies and parallelize independent tasks',
                'impact': 'high',
                'effort': 'low'
            })
        
        insights['recommendations'].append({
            'title': 'Add Performance Monitoring',
            'description': 'Track build step duration to identify bottlenecks',
            'impact': 'medium',
            'effort': 'low'
        })
        
        # Optimizations
        insights['optimizations'] = [
            {'step': 'Dependencies', 'suggestion': 'Cache node_modules and pip packages', 'time_saved': '30-60s'},
            {'step': 'Tests', 'suggestion': 'Run unit and integration tests in parallel', 'time_saved': '20-40s'},
            {'step': 'Build', 'suggestion': 'Use incremental compilation', 'time_saved': '15-30s'}
        ]
        
        return insights
    
    def generate_real_time_metrics(self):
        """Generate real-time metrics for dashboard"""
        return {
            'active_builds': random.randint(0, 3),
            'queue_length': random.randint(0, 5),
            'avg_wait_time': random.randint(5, 30),
            'cpu_usage': random.randint(30, 80),
            'memory_usage': random.randint(40, 85),
            'disk_usage': random.randint(50, 75),
            'last_success': (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat(),
            'last_failure': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        }

    def generate_live_update(self):
        """Generate a single live update for real-time demo"""
        run = self.generate_run()
        metrics = self.generate_real_time_metrics()
        
        return {
            'run': run,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }


# Test the generator
if __name__ == '__main__':
    print("🎯 PipeGuard Demo Data Generator Test\n")
    
    generator = DemoDataGenerator()
    
    # Generate sample runs
    print("Generating 10 sample pipeline runs...")
    runs = generator.generate_runs(10)
    
    print(f"\n✅ Generated {len(runs)} runs")
    print(f"Success rate: {sum(1 for r in runs if r['status'] == 'success') / len(runs) * 100:.1f}%")
    print(f"Average duration: {sum(r['duration'] for r in runs) / len(runs):.1f}s")
    
    # Detect anomalies
    print("\n🔍 Detecting anomalies...")
    anomalies = generator.detect_anomalies(runs)
    print(f"Found {len(anomalies)} anomalies")
    
    for anomaly in anomalies[:3]:
        print(f"\n⚠️  {anomaly['type']}")
        print(f"   Issue: {anomaly['issue']}")
        print(f"   Fix: {anomaly['fix']}")
    
    # Generate insights
    print("\n🤖 Generating AI insights...")
    insights = generator.generate_ai_insights(runs, anomalies)
    
    print(f"\nPatterns detected: {len(insights['patterns'])}")
    for pattern in insights['patterns']:
        print(f"  • {pattern}")
    
    print(f"\nRecommendations: {len(insights['recommendations'])}")
    for rec in insights['recommendations']:
        print(f"  • {rec['title']}: {rec['description']}")
    
    print("\n✅ Demo data generator working correctly!")
