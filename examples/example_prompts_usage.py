"""
Example demonstrating all prompt templates in CallFlow Tracer AI.

Shows how to use each of the 8 domain-specific prompt templates
with real-world scenarios.
"""

from callflow_tracer.ai import get_prompt_for_task, PromptTemplates


def example_1_performance_analysis():
    """Example 1: Performance Analysis Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Performance Analysis Prompt")
    print("="*80)
    
    graph_summary = """
    Total execution time: 5.234s
    Total functions: 42
    Total calls: 1523
    
    Top functions by execution time:
    1. database_query: 3.500s (66.9%) - 50 calls
    2. process_data: 1.200s (22.9%) - 100 calls
    3. validate_input: 0.300s (5.7%) - 500 calls
    4. format_output: 0.150s (2.9%) - 200 calls
    5. log_event: 0.084s (1.6%) - 773 calls
    """
    
    question = "What are the main performance bottlenecks and how can I optimize them?"
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'performance_analysis',
        graph_summary=graph_summary,
        question=question
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Expert performance analyst persona")
    print("  - Focus on high-impact issues (>5% execution time)")
    print("  - Considers call frequency and average time")
    print("  - Identifies patterns (N+1, recursion, memory leaks)")
    print("  - Provides actionable recommendations")


def example_2_root_cause_analysis():
    """Example 2: Root Cause Analysis Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Root Cause Analysis Prompt")
    print("="*80)
    
    root_causes = """
    1. database_query (module: app.db)
       - Called 50 times in loop
       - Average time: 70ms per call
       - Total impact: 3.5s
       - Pattern: N+1 query problem
    
    2. process_data (module: app.processor)
       - Called 100 times
       - Average time: 12ms per call
       - Total impact: 1.2s
       - Pattern: Inefficient algorithm
    
    3. validate_input (module: app.validators)
       - Called 500 times
       - Average time: 0.6ms per call
       - Total impact: 0.3s
       - Pattern: Redundant validation
    """
    
    impact = """
    - Total affected functions: 15
    - Total time impact: 5.0s
    - Impact percentage: 95.5%
    """
    
    issue_type = "performance"
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'root_cause_analysis',
        root_causes=root_causes,
        impact=impact,
        issue_type=issue_type
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Master debugger persona")
    print("  - Traces call chains from symptoms to root cause")
    print("  - Quantifies impact of each issue")
    print("  - Identifies cascading problems")
    print("  - Prioritizes fixes by impact and effort")


def example_3_code_fix_generation():
    """Example 3: Code Fix Generation Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Code Fix Generation Prompt")
    print("="*80)
    
    before_code = """
def get_user_orders(user_id):
    '''Fetch all orders for a user.'''
    orders = []
    order_ids = db.query('SELECT id FROM orders WHERE user_id = ?', user_id)
    
    for order_id in order_ids:
        # N+1 query problem: one query per order
        order = db.query('SELECT * FROM orders WHERE id = ?', order_id)
        orders.append(order)
    
    return orders
"""
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'code_fix',
        issue_type='n_plus_one',
        function_name='get_user_orders',
        context='Database query in loop causing N+1 problem',
        before_code=before_code
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Expert code optimizer persona")
    print("  - Minimal, surgical code changes")
    print("  - Maintains backward compatibility")
    print("  - Clear comments explaining optimization")
    print("  - Estimates performance improvement")
    print("  - Provides test cases")


def example_4_anomaly_analysis():
    """Example 4: Anomaly Analysis Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Anomaly Analysis Prompt")
    print("="*80)
    
    anomalies = """
    DETECTED ANOMALIES:
    
    1. Time Anomaly: process_data
       - Current value: 2.5s
       - Expected value: 0.8s
       - Deviation: 1.7s (212% above baseline)
       - Z-score: 3.2 (highly unusual)
    
    2. Frequency Anomaly: database_query
       - Current calls: 150
       - Expected calls: 50
       - Deviation: 100 extra calls (200% increase)
       - Pattern: Sudden spike in call count
    
    3. Pattern Anomaly: recursive_function
       - Depth: 500 (expected: <50)
       - Total calls: 10000 (expected: <1000)
       - Risk: Stack overflow potential
    """
    
    baseline = """
    BASELINE COMPARISON:
    - Average execution time: 0.5s
    - Standard deviation: 0.1s
    - Normal call frequency: 50 calls
    - Normal recursion depth: 20
    """
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'anomaly_analysis',
        anomalies=anomalies,
        baseline=baseline
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Statistical analyst persona")
    print("  - Classifies anomalies by type")
    print("  - Calculates deviation from baseline")
    print("  - Assesses severity and business impact")
    print("  - Identifies root causes")
    print("  - Recommends preventive measures")


def example_5_security_analysis():
    """Example 5: Security Analysis Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Security Analysis Prompt")
    print("="*80)
    
    issues = """
    DETECTED SECURITY ISSUES:
    
    1. SQL Injection Risk
       - Function: execute_query
       - Pattern: String concatenation in SQL
       - Severity: CRITICAL
       - Affected lines: 45-50
    
    2. Hardcoded Credentials
       - Function: connect_database
       - Pattern: API key in source code
       - Severity: CRITICAL
       - Affected lines: 12-15
    
    3. Weak Cryptography
       - Function: hash_password
       - Pattern: MD5 hashing (deprecated)
       - Severity: HIGH
       - Affected lines: 78-82
    
    4. Insecure Deserialization
       - Function: load_config
       - Pattern: pickle.loads() on untrusted data
       - Severity: HIGH
       - Affected lines: 120-125
    """
    
    code_context = """
    def execute_query(user_input):
        query = "SELECT * FROM users WHERE name = '" + user_input + "'"
        return db.execute(query)
    
    def connect_database():
        api_key = "sk-1234567890abcdef"
        return db.connect(api_key)
    """
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'security_analysis',
        issues=issues,
        code_context=code_context
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Cybersecurity expert persona")
    print("  - OWASP Top 10 classification")
    print("  - Severity assessment")
    print("  - Exploitation scenarios")
    print("  - Specific remediation code")
    print("  - Prevention best practices")


def example_6_refactoring():
    """Example 6: Refactoring Suggestions Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Refactoring Suggestions Prompt")
    print("="*80)
    
    function_code = """
def process_user_data(user_data):
    if user_data is None:
        return None
    
    if not isinstance(user_data, dict):
        return None
    
    if 'name' not in user_data:
        return None
    
    name = user_data['name']
    
    if not isinstance(name, str):
        return None
    
    if len(name) == 0:
        return None
    
    if 'email' not in user_data:
        return None
    
    email = user_data['email']
    
    if not isinstance(email, str):
        return None
    
    if '@' not in email:
        return None
    
    if 'age' in user_data:
        age = user_data['age']
        if not isinstance(age, int):
            return None
        if age < 0 or age > 150:
            return None
    
    result = {
        'name': name,
        'email': email,
        'age': user_data.get('age', None)
    }
    
    return result
"""
    
    metrics = {
        'cyclomatic_complexity': 18,
        'cognitive_complexity': 22,
        'lines_of_code': 45,
        'maintainability_index': 45,
    }
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'refactoring',
        function_code=function_code,
        metrics=metrics
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Software architect persona")
    print("  - Code smell identification")
    print("  - Design pattern suggestions")
    print("  - Complexity reduction")
    print("  - Testability improvements")


def example_7_test_generation():
    """Example 7: Test Generation Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Test Generation Prompt")
    print("="*80)
    
    function_code = """
def calculate_discount(price, customer_type, quantity):
    '''Calculate discount based on customer type and quantity.'''
    base_discount = 0
    
    if customer_type == 'premium':
        base_discount = 0.15
    elif customer_type == 'regular':
        base_discount = 0.05
    
    quantity_discount = 0
    if quantity >= 100:
        quantity_discount = 0.10
    elif quantity >= 50:
        quantity_discount = 0.05
    
    total_discount = base_discount + quantity_discount
    if total_discount > 0.25:
        total_discount = 0.25
    
    return price * (1 - total_discount)
"""
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'test_generation',
        function_code=function_code,
        function_name='calculate_discount'
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - QA engineer persona")
    print("  - Happy path, edge cases, error cases")
    print("  - High coverage (>90%)")
    print("  - pytest framework")
    print("  - Descriptive test names")
    print("  - Mock external dependencies")


def example_8_documentation():
    """Example 8: Documentation Generation Prompt"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Documentation Generation Prompt")
    print("="*80)
    
    function_code = """
def merge_sorted_arrays(arr1, arr2):
    '''Merge two sorted arrays into one sorted array.'''
    result = []
    i, j = 0, 0
    
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    
    result.extend(arr1[i:])
    result.extend(arr2[j:])
    
    return result
"""
    
    # Get enhanced prompts
    system_prompt, user_prompt = get_prompt_for_task(
        'documentation',
        function_code=function_code,
        function_name='merge_sorted_arrays'
    )
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    
    print("\n📝 USER PROMPT:")
    print("-" * 80)
    print(user_prompt)
    
    print("\n✨ KEY FEATURES:")
    print("  - Technical writer persona")
    print("  - Google-style docstrings")
    print("  - Type hints")
    print("  - Clear examples")
    print("  - Parameter documentation")
    print("  - Exception documentation")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("CallFlow Tracer - Enhanced Prompt Templates Examples")
    print("="*80)
    
    examples = [
        example_1_performance_analysis,
        example_2_root_cause_analysis,
        example_3_code_fix_generation,
        example_4_anomaly_analysis,
        example_5_security_analysis,
        example_6_refactoring,
        example_7_test_generation,
        example_8_documentation,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {str(e)}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)
    print("\n📚 Next Steps:")
    print("  1. Review the prompts above")
    print("  2. Use them with your LLM provider:")
    print("     from callflow_tracer.ai import OpenAIProvider")
    print("     provider = OpenAIProvider(model='gpt-4o')")
    print("     response = provider.generate(user_prompt, system_prompt)")
    print("  3. Check AI_ENHANCEMENTS_GUIDE.md for more details")


if __name__ == "__main__":
    main()
