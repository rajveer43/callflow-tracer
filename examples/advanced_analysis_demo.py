"""
Advanced Analysis Demo - Comprehensive example of new features.

This example demonstrates:
1. Real-time quality monitoring
2. Performance prediction from historical data
3. Scalability analysis with load testing
4. Resource forecasting
5. Churn-quality correlation
6. Automated quality gates

Usage:
    python advanced_analysis_demo.py
    
    # Or use CLI commands:
    callflow quality examples/ --track-trends
    callflow predict examples/trace_history.json
    callflow churn examples/ --days 30
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================================
# Example 1: Data Processing Pipeline with Quality Issues
# ============================================================================

class DataProcessor:
    """Example class with various quality issues for analysis."""
    
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.stats = {'processed': 0, 'errors': 0}
    
    def process_batch(self, data_batch, mode="standard", validate=True, 
                     transform=True, filter_invalid=True, apply_rules=True):
        """
        Process a batch of data.
        
        WARNING: This function has high cyclomatic complexity (16+)
        and should be refactored into smaller functions.
        """
        results = []
        
        for item in data_batch:
            try:
                # Validation phase
                if validate:
                    if not isinstance(item, dict):
                        if filter_invalid:
                            continue
                        else:
                            item = {'value': item}
                    
                    if 'value' not in item:
                        if filter_invalid:
                            continue
                        else:
                            item['value'] = 0
                
                # Processing phase
                if mode == "standard":
                    if transform:
                        if item['value'] > 0:
                            processed = item['value'] * 2
                        else:
                            processed = item['value']
                    else:
                        processed = item['value']
                elif mode == "advanced":
                    if transform:
                        if item['value'] > 100:
                            processed = item['value'] ** 0.5
                        elif item['value'] > 50:
                            processed = item['value'] * 1.5
                        else:
                            processed = item['value'] * 2
                    else:
                        processed = item['value']
                elif mode == "custom":
                    if apply_rules:
                        if item.get('priority') == 'high':
                            processed = item['value'] * 3
                        elif item.get('priority') == 'medium':
                            processed = item['value'] * 2
                        else:
                            processed = item['value']
                    else:
                        processed = item['value']
                else:
                    processed = item['value']
                
                # Caching phase
                if self.config.get('use_cache'):
                    cache_key = f"{mode}_{item['value']}"
                    if cache_key in self.cache:
                        processed = self.cache[cache_key]
                    else:
                        self.cache[cache_key] = processed
                
                results.append(processed)
                self.stats['processed'] += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                if not filter_invalid:
                    raise
        
        return results


# ============================================================================
# Example 2: Performance-Critical Functions for Prediction
# ============================================================================

def simulate_degrading_performance(iteration):
    """
    Simulates a function whose performance degrades over time.
    Perfect for performance prediction analysis.
    """
    # Simulate memory leak or resource accumulation
    data = [random.random() for _ in range(iteration * 100)]
    
    # Simulate increasing computation time
    time.sleep(0.001 * iteration)
    
    # Process data
    result = sum(x ** 2 for x in data)
    return result / len(data)


def simulate_stable_performance():
    """Simulates a function with stable performance."""
    time.sleep(0.01)
    return sum(range(1000))


def simulate_improving_performance(iteration):
    """Simulates a function that improves over time (e.g., with caching)."""
    # Simulate caching effect
    cache_factor = max(0.1, 1.0 - (iteration * 0.1))
    time.sleep(0.01 * cache_factor)
    return sum(range(1000))


# ============================================================================
# Example 3: Scalability Test Functions
# ============================================================================

def linear_algorithm(n):
    """O(n) algorithm - scales linearly."""
    result = 0
    for i in range(n):
        result += i
    return result


def quadratic_algorithm(n):
    """O(n²) algorithm - scales poorly."""
    result = 0
    for i in range(n):
        for j in range(n):
            result += i * j
    return result


def logarithmic_algorithm(n):
    """O(log n) algorithm - scales well."""
    result = 0
    i = n
    while i > 1:
        result += i
        i = i // 2
    return result


def constant_algorithm(n):
    """O(1) algorithm - constant time."""
    return n * 2 + 5


# ============================================================================
# Example 4: Memory-Intensive Functions for Resource Forecasting
# ============================================================================

class MemoryIntensiveProcessor:
    """Class that demonstrates memory growth patterns."""
    
    def __init__(self):
        self.data_store = []
        self.cache = {}
    
    def accumulate_data(self, size_mb):
        """Accumulates data in memory (simulates memory leak)."""
        # Allocate approximately size_mb megabytes
        num_elements = int(size_mb * 1024 * 1024 / 8)
        new_data = [random.random() for _ in range(num_elements)]
        self.data_store.append(new_data)
        return len(self.data_store)
    
    def process_with_cache(self, key, value):
        """Demonstrates cache growth."""
        if key not in self.cache:
            self.cache[key] = value * 2
        return self.cache[key]
    
    def clear_old_data(self, keep_last_n=5):
        """Cleanup method (good practice)."""
        if len(self.data_store) > keep_last_n:
            self.data_store = self.data_store[-keep_last_n:]


# ============================================================================
# Example 5: Refactored vs Non-Refactored Code
# ============================================================================

# BAD: High complexity, poor maintainability
def calculate_discount_bad(price, customer_type, quantity, season, is_member, 
                          promo_code, loyalty_points):
    """
    BAD EXAMPLE: High complexity (cyclomatic complexity ~20+)
    This needs refactoring!
    """
    discount = 0
    
    if customer_type == "premium":
        if quantity > 100:
            discount = 0.25
        elif quantity > 50:
            discount = 0.20
        else:
            discount = 0.15
        
        if season == "holiday":
            discount += 0.05
        
        if is_member:
            discount += 0.03
    elif customer_type == "regular":
        if quantity > 100:
            discount = 0.15
        elif quantity > 50:
            discount = 0.10
        else:
            discount = 0.05
        
        if season == "holiday":
            discount += 0.03
    else:
        if quantity > 50:
            discount = 0.05
        else:
            discount = 0.02
    
    if promo_code == "SAVE20":
        discount += 0.20
    elif promo_code == "SAVE10":
        discount += 0.10
    
    if loyalty_points > 1000:
        discount += 0.05
    elif loyalty_points > 500:
        discount += 0.03
    
    discount = min(discount, 0.50)  # Max 50% discount
    
    return price * (1 - discount)


# GOOD: Refactored with low complexity
def calculate_discount_good(price, customer_type, quantity, season, 
                           is_member, promo_code, loyalty_points):
    """
    GOOD EXAMPLE: Low complexity, high maintainability
    Each concern is separated into its own function.
    """
    base_discount = _get_base_discount(customer_type, quantity)
    seasonal_discount = _get_seasonal_discount(customer_type, season)
    membership_discount = _get_membership_discount(is_member)
    promo_discount = _get_promo_discount(promo_code)
    loyalty_discount = _get_loyalty_discount(loyalty_points)
    
    total_discount = sum([
        base_discount,
        seasonal_discount,
        membership_discount,
        promo_discount,
        loyalty_discount
    ])
    
    total_discount = min(total_discount, 0.50)  # Cap at 50%
    
    return price * (1 - total_discount)


def _get_base_discount(customer_type, quantity):
    """Calculate base discount based on customer type and quantity."""
    discount_matrix = {
        'premium': {100: 0.25, 50: 0.20, 0: 0.15},
        'regular': {100: 0.15, 50: 0.10, 0: 0.05},
        'guest': {50: 0.05, 0: 0.02}
    }
    
    thresholds = discount_matrix.get(customer_type, discount_matrix['guest'])
    for threshold, discount in sorted(thresholds.items(), reverse=True):
        if quantity >= threshold:
            return discount
    return 0


def _get_seasonal_discount(customer_type, season):
    """Calculate seasonal discount."""
    if season == "holiday":
        return 0.05 if customer_type == "premium" else 0.03
    return 0


def _get_membership_discount(is_member):
    """Calculate membership discount."""
    return 0.03 if is_member else 0


def _get_promo_discount(promo_code):
    """Calculate promo code discount."""
    promo_discounts = {
        'SAVE20': 0.20,
        'SAVE10': 0.10,
        'SAVE5': 0.05
    }
    return promo_discounts.get(promo_code, 0)


def _get_loyalty_discount(loyalty_points):
    """Calculate loyalty points discount."""
    if loyalty_points > 1000:
        return 0.05
    elif loyalty_points > 500:
        return 0.03
    return 0


# ============================================================================
# Demo Functions
# ============================================================================

def demo_quality_analysis():
    """Demonstrate code quality analysis."""
    print("=" * 70)
    print("DEMO 1: Code Quality Analysis")
    print("=" * 70)
    
    try:
        from callflow_tracer import ComplexityAnalyzer, MaintainabilityAnalyzer
        
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze_file(__file__)
        
        print(f"\nAnalyzed {len(metrics)} functions in this file:\n")
        
        # Sort by complexity
        sorted_metrics = sorted(metrics, key=lambda m: m.cyclomatic_complexity, reverse=True)
        
        print("Top 5 Most Complex Functions:")
        print("-" * 70)
        for i, metric in enumerate(sorted_metrics[:5], 1):
            print(f"{i}. {metric.function_name}")
            print(f"   Cyclomatic Complexity: {metric.cyclomatic_complexity} ({metric.complexity_rating})")
            print(f"   Cognitive Complexity: {metric.cognitive_complexity}")
            print(f"   Nesting Depth: {metric.nesting_depth}")
            print(f"   Lines of Code: {metric.lines_of_code}")
            print()
        
        # Maintainability analysis
        maint_analyzer = MaintainabilityAnalyzer()
        maint_metrics = maint_analyzer.analyze_file(__file__)
        
        print("\nMaintainability Analysis:")
        print("-" * 70)
        avg_mi = sum(m.maintainability_index for m in maint_metrics) / len(maint_metrics)
        print(f"Average Maintainability Index: {avg_mi:.1f}/100")
        
        # Find functions needing attention
        needs_attention = [m for m in maint_metrics if m.maintainability_index < 60]
        if needs_attention:
            print(f"\n⚠️  {len(needs_attention)} functions need attention:")
            for m in needs_attention[:3]:
                print(f"   - {m.function_name}: MI = {m.maintainability_index:.1f} ({m.maintainability_rating})")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure callflow-tracer is installed: pip install -e .")


def demo_performance_prediction():
    """Demonstrate performance prediction."""
    print("\n" + "=" * 70)
    print("DEMO 2: Performance Prediction")
    print("=" * 70)
    
    print("\nSimulating function performance over 10 iterations...")
    
    # Collect performance data
    degrading_times = []
    stable_times = []
    improving_times = []
    
    for i in range(1, 11):
        # Degrading performance
        start = time.time()
        simulate_degrading_performance(i)
        degrading_times.append(time.time() - start)
        
        # Stable performance
        start = time.time()
        simulate_stable_performance()
        stable_times.append(time.time() - start)
        
        # Improving performance
        start = time.time()
        simulate_improving_performance(i)
        improving_times.append(time.time() - start)
    
    print("\nPerformance Trends:")
    print("-" * 70)
    print(f"Degrading function: {degrading_times[0]:.4f}s → {degrading_times[-1]:.4f}s (↑ {((degrading_times[-1]/degrading_times[0])-1)*100:.1f}%)")
    print(f"Stable function:    {stable_times[0]:.4f}s → {stable_times[-1]:.4f}s (≈ stable)")
    print(f"Improving function: {improving_times[0]:.4f}s → {improving_times[-1]:.4f}s (↓ {((improving_times[0]/improving_times[-1])-1)*100:.1f}%)")
    
    print("\n💡 Tip: Use 'callflow predict' to analyze historical traces and predict future issues")


def demo_scalability_analysis():
    """Demonstrate scalability analysis."""
    print("\n" + "=" * 70)
    print("DEMO 3: Scalability Analysis")
    print("=" * 70)
    
    print("\nTesting algorithms with different input sizes...")
    
    test_sizes = [100, 500, 1000, 5000]
    
    algorithms = {
        'O(1) - Constant': constant_algorithm,
        'O(log n) - Logarithmic': logarithmic_algorithm,
        'O(n) - Linear': linear_algorithm,
        'O(n²) - Quadratic': quadratic_algorithm
    }
    
    print("\nPerformance Results:")
    print("-" * 70)
    
    for name, algo in algorithms.items():
        print(f"\n{name}:")
        times = []
        for size in test_sizes:
            start = time.time()
            algo(size)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  n={size:5d}: {elapsed:.6f}s")
        
        # Calculate scaling factor
        if times[0] > 0:
            scaling = times[-1] / times[0]
            input_scaling = test_sizes[-1] / test_sizes[0]
            print(f"  Scaling: {scaling:.1f}x time for {input_scaling:.1f}x input")


def demo_resource_monitoring():
    """Demonstrate resource monitoring."""
    print("\n" + "=" * 70)
    print("DEMO 4: Resource Monitoring")
    print("=" * 70)
    
    print("\nSimulating memory growth pattern...")
    
    processor = MemoryIntensiveProcessor()
    
    print("\nMemory Accumulation:")
    print("-" * 70)
    for i in range(1, 6):
        count = processor.accumulate_data(size_mb=5)
        cache_size = len(processor.cache)
        print(f"Iteration {i}: {count} data chunks, {cache_size} cache entries")
    
    print("\n⚠️  Memory is growing! This pattern indicates a potential memory leak.")
    print("💡 Tip: Use 'callflow memory-leak' to detect such issues automatically")
    
    # Demonstrate cleanup
    print("\nCleaning up old data...")
    processor.clear_old_data(keep_last_n=2)
    print(f"✓ Reduced to {len(processor.data_store)} data chunks")


def demo_code_comparison():
    """Demonstrate comparing refactored vs non-refactored code."""
    print("\n" + "=" * 70)
    print("DEMO 5: Refactored vs Non-Refactored Code")
    print("=" * 70)
    
    # Test both implementations
    test_params = (100.0, "premium", 75, "holiday", True, "SAVE10", 800)
    
    result_bad = calculate_discount_bad(*test_params)
    result_good = calculate_discount_good(*test_params)
    
    print(f"\nBoth implementations produce the same result: ${result_bad:.2f}")
    print("\nBut their quality metrics differ significantly:")
    print("-" * 70)
    
    try:
        from callflow_tracer import ComplexityAnalyzer
        
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze_file(__file__)
        
        bad_metric = next((m for m in metrics if m.function_name == 'calculate_discount_bad'), None)
        good_metric = next((m for m in metrics if m.function_name == 'calculate_discount_good'), None)
        
        if bad_metric and good_metric:
            print(f"\ncalculate_discount_bad:")
            print(f"  Complexity: {bad_metric.cyclomatic_complexity} ({bad_metric.complexity_rating})")
            print(f"  Nesting Depth: {bad_metric.nesting_depth}")
            print(f"  Lines of Code: {bad_metric.lines_of_code}")
            
            print(f"\ncalculate_discount_good:")
            print(f"  Complexity: {good_metric.cyclomatic_complexity} ({good_metric.complexity_rating})")
            print(f"  Nesting Depth: {good_metric.nesting_depth}")
            print(f"  Lines of Code: {good_metric.lines_of_code}")
            
            improvement = ((bad_metric.cyclomatic_complexity - good_metric.cyclomatic_complexity) 
                          / bad_metric.cyclomatic_complexity * 100)
            print(f"\n✓ Complexity reduced by {improvement:.1f}% through refactoring!")
    
    except Exception as e:
        print(f"Note: Install callflow-tracer to see detailed metrics")


def demo_technical_debt():
    """Demonstrate technical debt analysis."""
    print("\n" + "=" * 70)
    print("DEMO 6: Technical Debt Analysis")
    print("=" * 70)
    
    try:
        from callflow_tracer import (
            ComplexityAnalyzer, 
            MaintainabilityAnalyzer, 
            TechnicalDebtAnalyzer
        )
        
        # Analyze this file
        comp_analyzer = ComplexityAnalyzer()
        maint_analyzer = MaintainabilityAnalyzer()
        
        complexity_metrics = comp_analyzer.analyze_file(__file__)
        maintainability_metrics = maint_analyzer.analyze_file(__file__)
        
        # Analyze technical debt
        debt_analyzer = TechnicalDebtAnalyzer()
        debt_indicators = debt_analyzer.analyze_from_metrics(
            complexity_metrics,
            maintainability_metrics
        )
        
        if debt_indicators:
            print(f"\nFound {len(debt_indicators)} functions with technical debt:\n")
            
            # Show top 3
            for i, debt in enumerate(debt_indicators[:3], 1):
                print(f"{i}. {debt.function_name}")
                print(f"   Debt Score: {debt.debt_score:.1f}/100")
                print(f"   Severity: {debt.severity}")
                print(f"   Estimated Hours to Fix: {debt.estimated_hours:.1f}")
                print(f"   Issues:")
                for issue in debt.issues:
                    print(f"     • {issue}")
                print()
            
            total_debt = sum(d.debt_score for d in debt_indicators)
            total_hours = sum(d.estimated_hours for d in debt_indicators)
            
            print(f"Total Technical Debt Score: {total_debt:.1f}")
            print(f"Estimated Total Refactoring Time: {total_hours:.1f} hours")
        else:
            print("\n✓ No significant technical debt detected!")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure callflow-tracer is installed: pip install -e .")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "CALLFLOW TRACER - ADVANCED ANALYSIS DEMO" + " " * 13 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run all demos
    demo_quality_analysis()
    demo_performance_prediction()
    demo_scalability_analysis()
    demo_resource_monitoring()
    demo_code_comparison()
    demo_technical_debt()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - How to Use These Features")
    print("=" * 70)
    
    print("\n📊 CLI Commands:")
    print("-" * 70)
    print("  callflow quality examples/          # Analyze code quality")
    print("  callflow quality --track-trends     # Track quality over time")
    print("  callflow churn . --days 90          # Analyze code churn")
    print("  callflow predict traces.json        # Predict performance issues")
    
    print("\n🐍 Python API:")
    print("-" * 70)
    print("  from callflow_tracer import analyze_codebase")
    print("  results = analyze_codebase('./src')")
    print("  print(results['summary'])")
    
    print("\n📚 Documentation:")
    print("-" * 70)
    print("  See QUALITY_ANALYSIS_GUIDE.md for comprehensive examples")
    
    print("\n✅ Demo Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
