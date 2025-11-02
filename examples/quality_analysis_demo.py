"""
Demo script for code quality and predictive analysis features.

This demonstrates:
- Cyclomatic complexity analysis
- Maintainability index calculation
- Technical debt detection
- Performance prediction
- Code churn analysis

Usage:
    python quality_analysis_demo.py
    
    # Or use CLI:
    callflow quality examples/
    callflow churn examples/ --days 30
"""

import time
import random


# Example 1: Simple function (low complexity)
def simple_function(x, y):
    """A simple function with low complexity."""
    return x + y


# Example 2: Moderate complexity
def moderate_complexity(data):
    """Function with moderate complexity."""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(item)
    return result


# Example 3: High complexity (needs refactoring)
def high_complexity_function(data, mode, threshold, apply_filter):
    """Function with high cyclomatic complexity - needs refactoring."""
    results = []
    
    for item in data:
        if mode == "process":
            if item > threshold:
                if apply_filter:
                    if item % 2 == 0:
                        results.append(item * 2)
                    else:
                        results.append(item * 3)
                else:
                    results.append(item)
            else:
                if apply_filter:
                    results.append(item / 2)
                else:
                    results.append(item)
        elif mode == "filter":
            if item > threshold and apply_filter:
                results.append(item)
        elif mode == "transform":
            if item > 0:
                if item < threshold:
                    results.append(item ** 2)
                else:
                    results.append(item ** 0.5)
            else:
                results.append(0)
        else:
            results.append(item)
    
    return results


# Example 4: Very high complexity (critical - needs immediate refactoring)
def very_high_complexity(x, y, z, mode, flag1, flag2, flag3):
    """Critical complexity - immediate refactoring needed."""
    result = 0
    
    if mode == "A":
        if flag1:
            if flag2:
                if flag3:
                    result = x + y + z
                else:
                    result = x + y - z
            else:
                if flag3:
                    result = x - y + z
                else:
                    result = x - y - z
        else:
            if flag2:
                if flag3:
                    result = x * y + z
                else:
                    result = x * y - z
            else:
                result = x * y * z
    elif mode == "B":
        if flag1 and flag2:
            result = x ** y
        elif flag1 or flag2:
            result = x + y
        else:
            result = x - y
        
        if flag3:
            result = result * z
    elif mode == "C":
        for i in range(x):
            if i % 2 == 0:
                if flag1:
                    result += i
                else:
                    result -= i
            else:
                if flag2:
                    result *= 2
                else:
                    result /= 2
    else:
        result = x + y + z
    
    return result


# Example 5: Long function (maintainability issue)
def long_function_with_poor_maintainability():
    """Very long function with poor maintainability."""
    # This function is intentionally long to demonstrate maintainability issues
    data = []
    
    # Step 1: Generate data
    for i in range(100):
        data.append(random.random() * 100)
    
    # Step 2: Process data
    processed = []
    for item in data:
        if item > 50:
            processed.append(item * 2)
        else:
            processed.append(item / 2)
    
    # Step 3: Filter data
    filtered = []
    for item in processed:
        if item > 25 and item < 75:
            filtered.append(item)
    
    # Step 4: Transform data
    transformed = []
    for item in filtered:
        transformed.append(item ** 2)
    
    # Step 5: Aggregate data
    total = sum(transformed)
    average = total / len(transformed) if transformed else 0
    maximum = max(transformed) if transformed else 0
    minimum = min(transformed) if transformed else 0
    
    # Step 6: More processing
    final_result = {
        'total': total,
        'average': average,
        'max': maximum,
        'min': minimum,
        'count': len(transformed)
    }
    
    # Step 7: Additional calculations
    variance = sum((x - average) ** 2 for x in transformed) / len(transformed) if transformed else 0
    std_dev = variance ** 0.5
    
    final_result['variance'] = variance
    final_result['std_dev'] = std_dev
    
    # Step 8: Even more processing
    above_avg = [x for x in transformed if x > average]
    below_avg = [x for x in transformed if x <= average]
    
    final_result['above_avg_count'] = len(above_avg)
    final_result['below_avg_count'] = len(below_avg)
    
    return final_result


# Example 6: Function with performance issues (for prediction demo)
def slow_function(n):
    """Function that gets slower over time - for prediction demo."""
    time.sleep(0.01 * n)  # Simulates increasing execution time
    result = 0
    for i in range(n * 100):
        result += i ** 2
    return result


# Example 7: Recursive function (complexity analysis)
def recursive_fibonacci(n):
    """Recursive Fibonacci - demonstrates complexity."""
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


# Example 8: Well-structured function (good example)
def well_structured_function(data):
    """Well-structured function with good maintainability."""
    # Clear, single responsibility
    validated_data = _validate_data(data)
    processed_data = _process_data(validated_data)
    return _format_result(processed_data)


def _validate_data(data):
    """Validate input data."""
    return [x for x in data if isinstance(x, (int, float))]


def _process_data(data):
    """Process validated data."""
    return [x * 2 for x in data if x > 0]


def _format_result(data):
    """Format the result."""
    return {
        'values': data,
        'count': len(data),
        'sum': sum(data)
    }


def main():
    """Main function to demonstrate all examples."""
    print("=== Code Quality Analysis Demo ===\n")
    
    # Test simple function
    print("1. Simple function (low complexity):")
    result = simple_function(5, 3)
    print(f"   Result: {result}\n")
    
    # Test moderate complexity
    print("2. Moderate complexity function:")
    result = moderate_complexity([1, -2, 3, -4, 5])
    print(f"   Result: {result}\n")
    
    # Test high complexity
    print("3. High complexity function (needs refactoring):")
    result = high_complexity_function([1, 2, 3, 4, 5], "process", 3, True)
    print(f"   Result: {result}\n")
    
    # Test very high complexity
    print("4. Very high complexity function (critical):")
    result = very_high_complexity(2, 3, 4, "A", True, False, True)
    print(f"   Result: {result}\n")
    
    # Test long function
    print("5. Long function with poor maintainability:")
    result = long_function_with_poor_maintainability()
    print(f"   Result keys: {list(result.keys())}\n")
    
    # Test slow function
    print("6. Slow function (performance prediction demo):")
    for n in [1, 2, 3]:
        start = time.time()
        slow_function(n)
        elapsed = time.time() - start
        print(f"   n={n}: {elapsed:.4f}s")
    print()
    
    # Test recursive function
    print("7. Recursive function:")
    result = recursive_fibonacci(10)
    print(f"   Fibonacci(10) = {result}\n")
    
    # Test well-structured function
    print("8. Well-structured function (good example):")
    result = well_structured_function([1, 2, -3, 4, "invalid", 5])
    print(f"   Result: {result}\n")
    
    print("=== Demo Complete ===\n")
    print("To analyze this file's quality:")
    print("  callflow quality examples/quality_analysis_demo.py")
    print("\nTo see complexity metrics:")
    print("  python -c \"from callflow_tracer import ComplexityAnalyzer; ")
    print("  analyzer = ComplexityAnalyzer(); ")
    print("  metrics = analyzer.analyze_file('examples/quality_analysis_demo.py'); ")
    print("  for m in metrics: print(f'{m.function_name}: {m.cyclomatic_complexity}')\"")


if __name__ == "__main__":
    main()
