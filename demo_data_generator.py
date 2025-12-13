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
        self.branches = ['main', 'develop', 'feature/auth', 'feature/ui', 'hotfix/security']
        self.workflows = ['CI/CD Pipeline', 'Test Suite', 'Deploy Production', 'Security Scan', 'Code Quality']
        self.authors = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        
        # Build steps with realistic durations
        self.build_steps = [
            {'name': 'Checkout Code', 'duration_range': (2, 5)},
            {'name': 'Setup Python 3.11', 'duration_range': (10, 15)},
            {'name': 'Install Dependencies', 'duration_range': (20, 45)},
            {'name': 'Lint Code', 'duration_range': (5, 10)},
            {'name': 'Run Unit Tests', 'duration_range': (15, 30)},
            {'name': 'Run Integration Tests', 'duration_range': (20, 40)},
            {'name': 'Build Docker Image', 'duration_range': (25, 60)},
            {'name': 'Security Scan', 'duration_range': (10, 20)},
            {'name': 'Deploy to Staging', 'duration_range': (15, 25)}
        ]
        
        # Sample log messages
        self.log_templates = {
            'success': [
                "✓ All tests passed successfully",
                "✓ Build completed without errors",
                "✓ No security vulnerabilities found",
                "✓ Code coverage: {coverage}%",
                "✓ Deployment successful"
            ],
            'failure': [
                "✗ Test suite failed: 3 tests failed",
                "✗ Build error: Module 'app' not found",
                "✗ Security vulnerability detected: CVE-2024-12345",
                "✗ Code coverage below threshold: {coverage}%",
                "✗ Deployment failed: Connection timeout"
            ],
            'warning': [
                "⚠ Deprecated dependency: flask 2.0.0",
                "⚠ High memory usage detected",
                "⚠ Slow test execution: test_integration.py"
            ]
        }
        
        # Sample code changes
        self.code_changes = [
            {
                'file': 'app.py',
                'additions': random.randint(10, 50),
                'deletions': random.randint(5, 30),
                'changes': [
                    '+ def process_payment(amount, currency):',
                    '+     """Process payment with validation"""',
                    '+     if amount <= 0:',
                    '+         raise ValueError("Invalid amount")',
                    '-     return process(amount)  # Old method'
                ]
            },
            {
                'file': 'tests/test_api.py',
                'additions': random.randint(15, 40),
                'deletions': random.randint(3, 15),
                'changes': [
                    '+ def test_payment_validation():',
                    '+     with pytest.raises(ValueError):',
                    '+         process_payment(-100, "USD")'
                ]
            }
        ]
        
    def generate_run(self, status=None):
        """Generate a single pipeline run with realistic data"""
        if status is None:
            # 75% success rate for realistic demo
            status = 'success' if random.random() < 0.75 else 'failure'
        
        # Generate build steps with timing
        steps = []
        total_duration = 0
        
        for step_template in self.build_steps:
            step_duration = random.randint(*step_template['duration_range'])
            step_status = status if step_template == self.build_steps[-1] else 'success'
            
            # If this is a failure run, fail at a random step
            if status == 'failure' and random.random() < 0.3:
                step_status = 'failure'
                steps.append({
                    'name': step_template['name'],
                    'duration': step_duration,
                    'status': step_status
                })
                total_duration += step_duration
                break
            
            steps.append({
                'name': step_template['name'],
                'duration': step_duration,
                'status': step_status
            })
            total_duration += step_duration
        
        # Add some anomalies
        if random.random() < 0.1:  # 10% chance of slow build
            total_duration += random.randint(100, 300)
        
        # Generate logs
        logs = []
        if status == 'success':
            logs = [random.choice(self.log_templates['success']) for _ in range(3)]
            logs.append(f"✓ Code coverage: {random.randint(75, 95)}%")
        else:
            logs = [random.choice(self.log_templates['failure']) for _ in range(2)]
            logs.append(f"✗ Failed at step: {steps[-1]['name']}")
        
        # Add warnings occasionally
        if random.random() < 0.3:
            logs.append(random.choice(self.log_templates['warning']))
        
        # Select random code change
        code_change = random.choice(self.code_changes)
        
        run = {
            'id': self.run_counter,
            'run_id': f'run-{self.run_counter}',
            'status': status,
            'duration': total_duration,
            'branch': random.choice(self.branches),
            'workflow': random.choice(self.workflows),
            'author': random.choice(self.authors),
            'timestamp': (datetime.now() - timedelta(minutes=self.run_counter * 10)).isoformat(),
            'commit': f'{random.randint(100000, 999999):x}'[:7],
            'commit_message': self._generate_commit_message(status),
            'steps': steps,
            'logs': logs,
            'code_changes': {
                'files_changed': random.randint(1, 5),
                'additions': code_change['additions'],
                'deletions': code_change['deletions'],
                'example_file': code_change['file'],
                'example_changes': code_change['changes'][:3]
            },
            'test_results': self._generate_test_results(status),
            'artifacts': [
                {'name': 'coverage-report.html', 'size': f'{random.randint(10, 500)}KB'},
                {'name': 'test-results.xml', 'size': f'{random.randint(5, 50)}KB'}
            ] if status == 'success' else []
        }
        
        self.run_counter += 1
        return run
    
    def _generate_commit_message(self, status):
        """Generate realistic commit messages"""
        messages = [
            "feat: Add payment processing module",
            "fix: Resolve authentication bug",
            "refactor: Improve database queries",
            "test: Add integration tests",
            "docs: Update API documentation",
            "chore: Update dependencies",
            "perf: Optimize image loading",
            "security: Fix XSS vulnerability"
        ]
        return random.choice(messages)
    
    def _generate_test_results(self, status):
        """Generate realistic test results"""
        total_tests = random.randint(50, 150)
        
        if status == 'success':
            passed = total_tests
            failed = 0
            skipped = random.randint(0, 5)
        else:
            passed = random.randint(int(total_tests * 0.6), total_tests - 3)
            failed = total_tests - passed
            skipped = random.randint(0, 3)
        
        return {
            'total': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': random.randint(15, 60)
        }
    
    def generate_runs(self, count=20):
        """Generate multiple pipeline runs"""
        runs = []
        for _ in range(count):
            runs.append(self.generate_run())
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
