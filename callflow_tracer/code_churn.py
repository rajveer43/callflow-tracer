"""
Code Churn Analysis Module for CallFlow Tracer.

Analyzes code churn and correlates it with performance and quality metrics.
"""

import os
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class ChurnMetrics:
    """Code churn metrics for a file or function."""
    file_path: str
    function_name: Optional[str]
    total_commits: int
    lines_added: int
    lines_deleted: int
    lines_modified: int
    churn_rate: float  # Changes per day
    last_modified: str
    authors: List[str]
    hotspot_score: float  # 0-100, higher = more churned
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ChurnCorrelation:
    """Correlation between churn and quality/performance."""
    file_path: str
    churn_score: float
    complexity_score: float
    performance_score: float
    bug_correlation: float  # -1 to 1
    quality_correlation: float  # -1 to 1
    risk_assessment: str  # Low, Medium, High, Critical
    recommendations: List[str]
    
    def to_dict(self):
        return asdict(self)


class CodeChurnAnalyzer:
    """Analyze code churn using git history."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._verify_git_repo()
    
    def _verify_git_repo(self):
        """Verify that the path is a git repository."""
        git_dir = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_dir):
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def analyze_file_churn(self, file_path: str, days: int = 90) -> ChurnMetrics:
        """Analyze churn for a specific file."""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Get commit count
        commits = self._get_commit_count(file_path, since_date)
        
        # Get line changes
        added, deleted = self._get_line_changes(file_path, since_date)
        
        # Get authors
        authors = self._get_authors(file_path, since_date)
        
        # Get last modified date
        last_modified = self._get_last_modified(file_path)
        
        # Calculate churn rate
        churn_rate = (added + deleted) / days if days > 0 else 0
        
        # Calculate hotspot score
        hotspot_score = self._calculate_hotspot_score(commits, added + deleted, len(authors))
        
        return ChurnMetrics(
            file_path=file_path,
            function_name=None,
            total_commits=commits,
            lines_added=added,
            lines_deleted=deleted,
            lines_modified=added + deleted,
            churn_rate=round(churn_rate, 2),
            last_modified=last_modified,
            authors=authors,
            hotspot_score=round(hotspot_score, 2)
        )
    
    def analyze_directory_churn(self, directory: str = ".", days: int = 90) -> List[ChurnMetrics]:
        """Analyze churn for all Python files in a directory."""
        churn_metrics = []
        
        for root, dirs, files in os.walk(directory):
            # Skip .git and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        metrics = self.analyze_file_churn(file_path, days)
                        churn_metrics.append(metrics)
                    except Exception as e:
                        print(f"Error analyzing {file_path}: {e}")
        
        return sorted(churn_metrics, key=lambda x: x.hotspot_score, reverse=True)
    
    def identify_hotspots(self, directory: str = ".", days: int = 90, 
                         top_n: int = 10) -> List[ChurnMetrics]:
        """Identify code hotspots (most churned files)."""
        all_churn = self.analyze_directory_churn(directory, days)
        return all_churn[:top_n]
    
    def _get_commit_count(self, file_path: str, since_date: str) -> int:
        """Get number of commits for a file."""
        try:
            cmd = [
                "git", "-C", self.repo_path, "log",
                "--since", since_date,
                "--oneline",
                "--", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except:
            return 0
    
    def _get_line_changes(self, file_path: str, since_date: str) -> Tuple[int, int]:
        """Get lines added and deleted."""
        try:
            cmd = [
                "git", "-C", self.repo_path, "log",
                "--since", since_date,
                "--numstat",
                "--pretty=format:",
                "--", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            added = 0
            deleted = 0
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                        added += int(parts[0])
                        deleted += int(parts[1])
            
            return added, deleted
        except:
            return 0, 0
    
    def _get_authors(self, file_path: str, since_date: str) -> List[str]:
        """Get list of authors who modified the file."""
        try:
            cmd = [
                "git", "-C", self.repo_path, "log",
                "--since", since_date,
                "--format=%an",
                "--", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            authors = set()
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    authors.add(line.strip())
            
            return sorted(list(authors))
        except:
            return []
    
    def _get_last_modified(self, file_path: str) -> str:
        """Get last modified date."""
        try:
            cmd = [
                "git", "-C", self.repo_path, "log",
                "-1",
                "--format=%ai",
                "--", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout.strip()[:10] if result.stdout.strip() else "Unknown"
        except:
            return "Unknown"
    
    def _calculate_hotspot_score(self, commits: int, lines_changed: int, 
                                 num_authors: int) -> float:
        """Calculate hotspot score (0-100)."""
        # Normalize factors
        commit_score = min(commits / 10, 1.0) * 40  # Max 40 points
        change_score = min(lines_changed / 1000, 1.0) * 40  # Max 40 points
        author_score = min(num_authors / 5, 1.0) * 20  # Max 20 points
        
        return commit_score + change_score + author_score


class ChurnCorrelationAnalyzer:
    """Correlate code churn with quality and performance metrics."""
    
    def correlate_churn_with_quality(self, churn_metrics: List[ChurnMetrics],
                                     complexity_metrics: List,
                                     performance_data: Dict) -> List[ChurnCorrelation]:
        """Correlate churn with code quality and performance."""
        correlations = []
        
        for churn in churn_metrics:
            # Find corresponding complexity metrics
            complexity_score = self._get_complexity_score(churn.file_path, complexity_metrics)
            
            # Find corresponding performance data
            performance_score = self._get_performance_score(churn.file_path, performance_data)
            
            # Calculate correlations
            bug_correlation = self._estimate_bug_correlation(churn.hotspot_score, complexity_score)
            quality_correlation = self._estimate_quality_correlation(churn.churn_rate, complexity_score)
            
            # Assess risk
            risk = self._assess_risk(churn.hotspot_score, complexity_score, performance_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(churn, complexity_score, performance_score, risk)
            
            correlation = ChurnCorrelation(
                file_path=churn.file_path,
                churn_score=churn.hotspot_score,
                complexity_score=complexity_score,
                performance_score=performance_score,
                bug_correlation=bug_correlation,
                quality_correlation=quality_correlation,
                risk_assessment=risk,
                recommendations=recommendations
            )
            correlations.append(correlation)
        
        return sorted(correlations, key=lambda x: x.churn_score, reverse=True)
    
    def _get_complexity_score(self, file_path: str, complexity_metrics: List) -> float:
        """Get complexity score for a file."""
        # Extract filename
        filename = os.path.basename(file_path).replace('.py', '')
        
        # Find matching metrics
        matching = [m for m in complexity_metrics if m.get('module') == filename]
        
        if matching:
            avg_complexity = sum(m.get('cyclomatic_complexity', 0) for m in matching) / len(matching)
            # Normalize to 0-100
            return min(avg_complexity * 5, 100)
        
        return 50.0  # Default
    
    def _get_performance_score(self, file_path: str, performance_data: Dict) -> float:
        """Get performance score for a file."""
        filename = os.path.basename(file_path).replace('.py', '')
        
        # Look for performance data
        if filename in performance_data:
            # Lower time = higher score
            avg_time = performance_data[filename].get('avg_time', 0)
            if avg_time > 0:
                return max(0, 100 - (avg_time * 1000))  # Convert to ms
        
        return 50.0  # Default
    
    def _estimate_bug_correlation(self, churn_score: float, complexity_score: float) -> float:
        """Estimate correlation between churn and bugs."""
        # High churn + high complexity = high bug correlation
        combined = (churn_score + complexity_score) / 200
        
        # Normalize to -1 to 1 range (positive correlation expected)
        return min(1.0, combined * 2 - 0.5)
    
    def _estimate_quality_correlation(self, churn_rate: float, complexity_score: float) -> float:
        """Estimate correlation between churn and quality."""
        # High churn rate often indicates quality issues (negative correlation with quality)
        if churn_rate > 10:
            base_correlation = -0.7
        elif churn_rate > 5:
            base_correlation = -0.4
        else:
            base_correlation = -0.1
        
        # Adjust based on complexity
        if complexity_score > 70:
            base_correlation -= 0.2
        
        return max(-1.0, min(1.0, base_correlation))
    
    def _assess_risk(self, churn_score: float, complexity_score: float, 
                    performance_score: float) -> str:
        """Assess overall risk level."""
        risk_score = (churn_score + complexity_score) / 2
        
        # Adjust for performance
        if performance_score < 30:
            risk_score += 20
        
        if risk_score >= 80:
            return "Critical"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, churn: ChurnMetrics, complexity: float,
                                  performance: float, risk: str) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if churn.hotspot_score > 70:
            recommendations.append("High churn detected - consider refactoring for stability")
        
        if complexity > 70:
            recommendations.append("High complexity - simplify code structure")
        
        if performance < 40:
            recommendations.append("Performance issues detected - profile and optimize")
        
        if len(churn.authors) > 5:
            recommendations.append("Multiple authors - ensure code review and documentation")
        
        if churn.churn_rate > 10:
            recommendations.append("Very high churn rate - investigate root cause")
        
        if risk in ["Critical", "High"]:
            recommendations.append("PRIORITY: This file requires immediate attention")
            recommendations.append("Consider adding comprehensive tests")
        
        return recommendations


def generate_churn_report(repo_path: str = ".", days: int = 90,
                         complexity_metrics: List = None,
                         performance_data: Dict = None) -> Dict:
    """Generate comprehensive churn analysis report."""
    analyzer = CodeChurnAnalyzer(repo_path)
    
    # Analyze churn
    churn_metrics = analyzer.analyze_directory_churn(".", days)
    hotspots = analyzer.identify_hotspots(".", days, top_n=10)
    
    # Correlate with quality if data provided
    correlations = []
    if complexity_metrics or performance_data:
        correlator = ChurnCorrelationAnalyzer()
        correlations = correlator.correlate_churn_with_quality(
            churn_metrics,
            complexity_metrics or [],
            performance_data or {}
        )
    
    # Calculate summary statistics
    total_commits = sum(m.total_commits for m in churn_metrics)
    total_changes = sum(m.lines_modified for m in churn_metrics)
    avg_churn_rate = sum(m.churn_rate for m in churn_metrics) / len(churn_metrics) if churn_metrics else 0
    
    return {
        "churn_metrics": [m.to_dict() for m in churn_metrics],
        "hotspots": [h.to_dict() for h in hotspots],
        "correlations": [c.to_dict() for c in correlations],
        "summary": {
            "total_files": len(churn_metrics),
            "total_commits": total_commits,
            "total_changes": total_changes,
            "average_churn_rate": round(avg_churn_rate, 2),
            "analysis_period_days": days,
            "high_risk_files": len([c for c in correlations if c.risk_assessment in ["Critical", "High"]])
        }
    }
