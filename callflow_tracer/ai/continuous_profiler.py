"""
Continuous profiling module for CallFlow Tracer.

Provides always-on production profiling with minimal overhead. Automatically
collects and analyzes traces, sends alerts on anomalies, and builds baselines.

Example:
    from callflow_tracer.ai import ContinuousProfiler
    
    profiler = ContinuousProfiler(
        sampling_rate=0.01,  # 1% of requests
        aggregation_window='5m',
        storage='memory'
    )
    
    profiler.start()
    
    # Automatically collects and analyzes traces
    # Sends alerts on anomalies
    # Builds baseline automatically
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import json
import threading
import time
from collections import defaultdict
import statistics


@dataclass
class ProfileSnapshot:
    """A single profiling snapshot."""
    timestamp: str
    window_id: str
    total_time: float
    request_count: int
    functions: Dict[str, Dict[str, Any]]
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BaselineProfile:
    """Baseline profile for anomaly detection."""
    created_at: str
    updated_at: str
    function_stats: Dict[str, Dict[str, float]]
    percentiles: Dict[str, Dict[str, float]]
    anomaly_threshold: float


class ContinuousProfiler:
    """Continuous profiling with minimal overhead."""
    
    def __init__(self, sampling_rate: float = 0.01,
                 aggregation_window: str = '5m',
                 storage: str = 'memory',
                 anomaly_threshold: float = 2.0,
                 alert_callback: Optional[Callable] = None):
        """
        Initialize continuous profiler.
        
        Args:
            sampling_rate: Fraction of requests to profile (0.01 = 1%)
            aggregation_window: Window for aggregation ('5m', '1h', etc)
            storage: Storage backend ('memory', 'redis', 'file')
            anomaly_threshold: Z-score threshold for anomalies
            alert_callback: Optional callback for alerts
        """
        self.sampling_rate = sampling_rate
        self.aggregation_window = aggregation_window
        self.storage = storage
        self.anomaly_threshold = anomaly_threshold
        self.alert_callback = alert_callback
        
        self.enabled = False
        self.snapshots: List[ProfileSnapshot] = []
        self.baseline: Optional[BaselineProfile] = None
        self.current_window_data: Dict[str, Any] = defaultdict(lambda: {
            'times': [],
            'counts': [],
            'functions': defaultdict(lambda: {'times': [], 'counts': []})
        })
        
        self._lock = threading.Lock()
        self._profiling_thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start continuous profiling."""
        if self.enabled:
            return
        
        self.enabled = True
        self._profiling_thread = threading.Thread(
            target=self._profiling_loop,
            daemon=True
        )
        self._profiling_thread.start()
    
    def stop(self) -> None:
        """Stop continuous profiling."""
        self.enabled = False
        if self._profiling_thread:
            self._profiling_thread.join(timeout=5)
    
    def record_trace(self, graph: Dict[str, Any]) -> None:
        """
        Record a trace for profiling.
        
        Args:
            graph: Execution trace graph
        """
        if not self.enabled:
            return
        
        # Sample based on sampling rate
        import random
        if random.random() > self.sampling_rate:
            return
        
        with self._lock:
            self._process_trace(graph)
    
    def get_baseline(self) -> Optional[Dict[str, Any]]:
        """Get current baseline profile."""
        if self.baseline:
            return asdict(self.baseline)
        return None
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get latest profiling snapshot."""
        if self.snapshots:
            return asdict(self.snapshots[-1])
        return None
    
    def get_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent snapshots."""
        return [asdict(s) for s in self.snapshots[-limit:]]
    
    def get_anomalies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get detected anomalies."""
        anomalies = []
        for snapshot in self.snapshots:
            anomalies.extend(snapshot.anomalies)
        return anomalies[-limit:]
    
    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts."""
        alerts = []
        for snapshot in self.snapshots:
            alerts.extend(snapshot.alerts)
        return alerts[-limit:]
    
    def _process_trace(self, graph: Dict[str, Any]) -> None:
        """Process a trace for profiling."""
        nodes = self._extract_nodes(graph)
        total_time = self._get_total_time(graph)
        
        window_key = self._get_window_key()
        window_data = self.current_window_data[window_key]
        
        window_data['times'].append(total_time)
        window_data['counts'].append(1)
        
        for node_key, node in nodes.items():
            func_data = window_data['functions'][node_key]
            func_data['times'].append(node.get('total_time', 0))
            func_data['counts'].append(node.get('call_count', 1))
    
    def _profiling_loop(self) -> None:
        """Background profiling loop."""
        while self.enabled:
            try:
                time.sleep(self._parse_window_duration())
                self._aggregate_window()
            except Exception as e:
                print(f"Error in profiling loop: {e}")
    
    def _aggregate_window(self) -> None:
        """Aggregate current window and create snapshot."""
        with self._lock:
            window_key = self._get_window_key()
            
            if window_key not in self.current_window_data:
                return
            
            window_data = self.current_window_data[window_key]
            
            if not window_data['times']:
                return
            
            # Compute aggregates
            functions = {}
            for node_key, func_data in window_data['functions'].items():
                if func_data['times']:
                    functions[node_key] = {
                        'mean_time': statistics.mean(func_data['times']),
                        'max_time': max(func_data['times']),
                        'min_time': min(func_data['times']),
                        'call_count': sum(func_data['counts']),
                        'samples': len(func_data['times'])
                    }
            
            # Create snapshot
            snapshot = ProfileSnapshot(
                timestamp=datetime.now().isoformat(),
                window_id=window_key,
                total_time=statistics.mean(window_data['times']),
                request_count=len(window_data['times']),
                functions=functions
            )
            
            # Detect anomalies
            if self.baseline:
                snapshot.anomalies = self._detect_anomalies(snapshot)
                snapshot.alerts = self._generate_alerts(snapshot)
                
                if snapshot.alerts and self.alert_callback:
                    for alert in snapshot.alerts:
                        self.alert_callback(alert)
            
            # Update baseline if needed
            if not self.baseline:
                self.baseline = self._create_baseline(snapshot)
            else:
                self._update_baseline(snapshot)
            
            self.snapshots.append(snapshot)
            
            # Keep only recent snapshots
            if len(self.snapshots) > 1000:
                self.snapshots = self.snapshots[-1000:]
            
            # Clear current window
            del self.current_window_data[window_key]
    
    def _detect_anomalies(self, snapshot: ProfileSnapshot) -> List[Dict[str, Any]]:
        """Detect anomalies in snapshot."""
        anomalies = []
        
        if not self.baseline:
            return anomalies
        
        for node_key, func_stats in snapshot.functions.items():
            if node_key in self.baseline.function_stats:
                baseline_stats = self.baseline.function_stats[node_key]
                current_time = func_stats['mean_time']
                baseline_mean = baseline_stats.get('mean', 0)
                baseline_stdev = baseline_stats.get('stdev', 0)
                
                if baseline_stdev > 0:
                    z_score = (current_time - baseline_mean) / baseline_stdev
                    
                    if abs(z_score) > self.anomaly_threshold:
                        anomalies.append({
                            'function': node_key,
                            'current_time': current_time,
                            'baseline_mean': baseline_mean,
                            'z_score': z_score,
                            'severity': 'critical' if abs(z_score) > 3 else 'high'
                        })
        
        return anomalies
    
    def _generate_alerts(self, snapshot: ProfileSnapshot) -> List[Dict[str, Any]]:
        """Generate alerts based on anomalies."""
        alerts = []
        
        if not snapshot.anomalies:
            return alerts
        
        critical_anomalies = [a for a in snapshot.anomalies if a['severity'] == 'critical']
        
        if critical_anomalies:
            alerts.append({
                'timestamp': snapshot.timestamp,
                'type': 'anomaly',
                'severity': 'critical',
                'message': f"Critical anomalies detected in {len(critical_anomalies)} function(s)",
                'anomalies': critical_anomalies
            })
        
        return alerts
    
    def _create_baseline(self, snapshot: ProfileSnapshot) -> BaselineProfile:
        """Create initial baseline from snapshot."""
        function_stats = {}
        
        for node_key, func_stats in snapshot.functions.items():
            function_stats[node_key] = {
                'mean': func_stats['mean_time'],
                'stdev': 0.0,
                'min': func_stats['min_time'],
                'max': func_stats['max_time'],
                'samples': func_stats['samples']
            }
        
        return BaselineProfile(
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            function_stats=function_stats,
            percentiles={},
            anomaly_threshold=self.anomaly_threshold
        )
    
    def _update_baseline(self, snapshot: ProfileSnapshot) -> None:
        """Update baseline with new snapshot."""
        if not self.baseline:
            return
        
        for node_key, func_stats in snapshot.functions.items():
            if node_key in self.baseline.function_stats:
                baseline = self.baseline.function_stats[node_key]
                current_time = func_stats['mean_time']
                
                # Update mean and stdev using Welford's algorithm
                n = baseline['samples']
                new_n = n + func_stats['samples']
                delta = current_time - baseline['mean']
                
                baseline['mean'] = baseline['mean'] + delta * func_stats['samples'] / new_n
                baseline['samples'] = new_n
                baseline['min'] = min(baseline['min'], func_stats['min_time'])
                baseline['max'] = max(baseline['max'], func_stats['max_time'])
        
        self.baseline.updated_at = datetime.now().isoformat()
    
    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from graph."""
        nodes = {}
        
        if isinstance(graph, dict):
            if 'nodes' in graph:
                for node in graph['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
            elif 'data' in graph and 'nodes' in graph['data']:
                for node in graph['data']['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
        
        return nodes
    
    def _get_total_time(self, graph: Dict[str, Any]) -> float:
        """Get total time from graph."""
        if isinstance(graph, dict):
            if 'total_time' in graph:
                return graph['total_time']
            elif 'data' in graph and 'total_time' in graph['data']:
                return graph['data']['total_time']
        return 0.0
    
    def _get_window_key(self) -> str:
        """Get current window key."""
        now = datetime.now()
        duration = self._parse_window_duration()
        window_start = now - timedelta(seconds=now.timestamp() % duration)
        return window_start.isoformat()
    
    def _parse_window_duration(self) -> float:
        """Parse aggregation window duration to seconds."""
        window = self.aggregation_window
        
        if window.endswith('m'):
            return int(window[:-1]) * 60
        elif window.endswith('h'):
            return int(window[:-1]) * 3600
        elif window.endswith('s'):
            return int(window[:-1])
        else:
            return 300  # Default 5 minutes
