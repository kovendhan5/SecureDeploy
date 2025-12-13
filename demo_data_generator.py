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
        
    def generate_run(self, status=None, offset_minutes=0):
        """Generate a single pipeline run with realistic data"""
        if status is None:
            # 75% success rate for realistic demo
            status = 'success' if random.random() < 0.75 else 'failure'
        
        # Base duration depends on status
        if status == 'success':
            duration = random.randint(60, 180)  # 1-3 minutes
        else:
            duration = random.randint(30, 120)  # Failures often faster
        
        # Add some anomalies
        if random.random() < 0.1:  # 10% chance of slow build
            duration += random.randint(100, 300)
        
        finished_at = datetime.now() - timedelta(minutes=offset_minutes)
        started_at = finished_at - timedelta(seconds=duration)

        run = {
            'id': self.run_counter,
            'run_id': f'run-{self.run_counter}',
            'status': status,
            'duration': duration,
            'branch': random.choice(self.branches),
            'workflow': random.choice(self.workflows),
            'author': random.choice(self.authors),
            'timestamp': finished_at.isoformat(),
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'commit': f'{random.randint(100000, 999999):x}'[:7]
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
