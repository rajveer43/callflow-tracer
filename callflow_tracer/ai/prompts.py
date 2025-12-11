"""
Enhanced prompt templates for CallFlow Tracer AI features.

Provides domain-specific, few-shot prompts with chain-of-thought reasoning
for better LLM performance across different analysis tasks.
"""

from typing import Dict, Optional, List, Any


class PromptTemplates:
    """Collection of enhanced prompt templates for AI analysis."""
    
    # ============================================================================
    # QUERY ENGINE PROMPTS
    # ============================================================================
    
    @staticmethod
    def query_performance_analysis(graph_summary: str, question: str) -> tuple:
        """
        Advanced prompt for comprehensive performance analysis with multi-dimensional insights.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class performance engineer with expertise in:
- Python internals and optimization techniques
- Distributed systems and concurrent programming
- Database query optimization and indexing strategies
- Memory profiling and garbage collection tuning
- Network I/O optimization and caching strategies
- Algorithmic complexity analysis and optimization

YOUR ANALYTICAL FRAMEWORK:
1. MULTI-DIMENSIONAL ANALYSIS:
   - Time complexity (absolute and relative)
   - Space complexity and memory allocation patterns
   - I/O patterns (disk, network, database)
   - Concurrency bottlenecks and lock contention
   - Resource utilization (CPU, memory, I/O)

2. PATTERN RECOGNITION:
   - N+1 query patterns and batch optimization opportunities
   - Inefficient algorithms (O(n²) where O(n log n) possible)
   - Excessive object allocation and GC pressure
   - Blocking operations in async contexts
   - Cache misses and memory access patterns
   - Lock contention and synchronization overhead

3. CONTEXTUAL ANALYSIS:
   - Business impact of performance issues
   - User experience implications
   - Scalability limitations
   - Cost implications (cloud infrastructure)
   - Technical debt and maintenance burden

4. RECOMMENDATION QUALITY:
   - Prioritize by impact/effort ratio
   - Consider implementation complexity
   - Account for team expertise and constraints
   - Suggest both quick wins and long-term improvements
   - Provide risk assessment for each recommendation

RESPONSE STRUCTURE:
- Executive summary with key metrics
- Detailed bottleneck analysis with quantified impact
- Root cause analysis with evidence
- Prioritized optimization strategies with implementation details
- Performance improvement projections with confidence levels
- Risk assessment and mitigation strategies
- Monitoring and validation approach"""
        
        user_prompt = f"""Perform a comprehensive performance analysis of this system execution trace.

EXECUTION TRACE DATA:
{graph_summary}

ANALYSIS QUESTION: {question}

REQUIRED ANALYSIS DEPTH:
1. BOTTLENECK IDENTIFICATION:
   - Identify all functions consuming >2% of execution time
   - Analyze call patterns (frequency, recursion depth, branching)
   - Quantify time spent in I/O vs computation vs synchronization
   - Identify cascading effects and dependencies

2. ROOT CAUSE ANALYSIS:
   - For each bottleneck, determine the underlying cause
   - Trace the call chain from entry point to bottleneck
   - Identify algorithmic inefficiencies
   - Detect resource contention and blocking operations
   - Analyze data structure choices and their impact

3. OPTIMIZATION OPPORTUNITIES:
   - Suggest specific, implementable optimizations
   - Estimate performance improvement for each optimization
   - Consider trade-offs (memory vs speed, complexity vs maintainability)
   - Identify quick wins vs long-term improvements
   - Suggest caching, batching, or parallelization opportunities

4. IMPACT ASSESSMENT:
   - Calculate potential speedup (e.g., "2.5x faster")
   - Estimate resource savings (CPU, memory, I/O)
   - Project user experience improvements
   - Assess scalability implications
   - Evaluate cost impact for cloud deployments

5. IMPLEMENTATION GUIDANCE:
   - Provide specific code patterns or libraries to use
   - Suggest testing strategy to validate improvements
   - Identify potential pitfalls and how to avoid them
   - Recommend monitoring metrics to track improvements
   - Suggest rollout strategy for high-risk changes

ANALYSIS METHODOLOGY:
- Use chain-of-thought reasoning to explain each finding
- Support claims with specific metrics from the trace
- Consider multiple optimization approaches and compare
- Account for system constraints and requirements
- Provide confidence levels for projections

RESPONSE FORMAT:
## Executive Summary
[Key findings, overall performance assessment, main recommendations]

## Critical Bottlenecks (>5% execution time)
[For each: function name, time spent, % of total, impact assessment]

## Root Cause Analysis
[For each bottleneck: underlying cause, evidence, contributing factors]

## Optimization Strategies
[Prioritized list with: strategy, implementation approach, estimated improvement, effort level, risk level]

## Performance Projections
[Expected speedup, resource savings, scalability improvements]

## Implementation Roadmap
[Quick wins, medium-term improvements, long-term architectural changes]

## Monitoring & Validation
[Metrics to track, testing approach, success criteria]"""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def root_cause_analysis(root_causes: str, impact: str, issue_type: str) -> tuple:
        """
        Advanced prompt for deep root cause analysis with causal chain mapping.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a master systems debugger and forensic analyst with expertise in:
- Causal chain analysis and dependency mapping
- System dynamics and feedback loops
- Distributed systems failure modes
- Performance degradation patterns
- Architectural anti-patterns and their consequences
- Risk propagation and cascading failures

YOUR INVESTIGATION METHODOLOGY:
1. SYMPTOM-TO-ROOT-CAUSE TRACING:
   - Map the complete causal chain from observed symptoms to root causes
   - Identify direct causes vs contributing factors vs enabling conditions
   - Distinguish between symptoms and root causes
   - Trace through multiple layers of abstraction
   - Identify hidden dependencies and side effects

2. CAUSAL ANALYSIS FRAMEWORK:
   - Why-Why analysis (5 whys minimum, go deeper if needed)
   - Dependency graph construction
   - Feedback loop identification
   - Failure mode analysis
   - Interaction effects between multiple issues

3. IMPACT QUANTIFICATION:
   - Direct impact on system performance/reliability
   - Cascading effects on dependent systems
   - User experience degradation
   - Business impact (revenue, reputation, compliance)
   - Technical debt accumulation
   - Future scalability implications

4. SYSTEMIC ANALYSIS:
   - Identify architectural weaknesses
   - Detect design patterns that enable the issue
   - Analyze organizational/process factors
   - Consider team expertise and constraints
   - Evaluate monitoring and alerting gaps

5. REMEDIATION STRATEGY:
   - Distinguish between symptoms vs root cause fixes
   - Prioritize by impact and feasibility
   - Identify quick wins vs structural changes
   - Assess risk of each remediation approach
   - Plan for validation and rollback
   - Consider preventive measures

RESPONSE QUALITY CRITERIA:
- Depth: Go beyond surface-level analysis
- Evidence: Support claims with specific data
- Completeness: Address all contributing factors
- Actionability: Provide concrete remediation steps
- Risk-awareness: Identify potential side effects
- Systemic thinking: Consider broader implications"""
        
        user_prompt = f"""Perform a comprehensive forensic root cause analysis for {issue_type} issues.

IDENTIFIED ISSUES AND SYMPTOMS:
{root_causes}

IMPACT ASSESSMENT:
{impact}

INVESTIGATION REQUIREMENTS:

1. CAUSAL CHAIN MAPPING:
   - Trace each symptom back to its root cause(s)
   - Map the complete dependency chain
   - Identify direct causes vs contributing factors
   - Distinguish between symptoms and root causes
   - Explain why each identified cause is truly a root cause

2. DEEP ROOT CAUSE ANALYSIS:
   - For each root cause, apply 5-why analysis
   - Identify systemic factors enabling the issue
   - Analyze architectural decisions that contributed
   - Examine process/organizational factors
   - Consider monitoring and visibility gaps

3. CASCADING EFFECTS ANALYSIS:
   - How does this issue propagate through the system?
   - What dependent systems are affected?
   - Are there secondary failures triggered?
   - What feedback loops are created?
   - How does the issue compound over time?

4. IMPACT QUANTIFICATION:
   - Quantify performance degradation (latency, throughput, resource usage)
   - Calculate business impact (affected users, revenue impact)
   - Assess reliability implications (error rates, SLA violations)
   - Evaluate technical debt created
   - Project future scalability impact

5. REMEDIATION ANALYSIS:
   - Identify all potential remediation approaches
   - Classify as: quick fix, temporary mitigation, permanent solution
   - For each approach, analyze:
     * Effectiveness in addressing root cause
     * Implementation complexity and effort
     * Risk of side effects or regressions
     * Time to implement and validate
     * Long-term maintainability

6. PREVENTION STRATEGY:
   - What monitoring/alerting should have caught this?
   - What architectural changes prevent recurrence?
   - What process improvements are needed?
   - What testing strategies would have prevented this?
   - How to build organizational knowledge?

ANALYSIS METHODOLOGY:
- Use structured reasoning to build the causal chain
- Support each claim with specific evidence from the data
- Consider multiple hypotheses and compare
- Identify assumptions and validate them
- Provide confidence levels for conclusions
- Explain uncertainty and limitations

RESPONSE STRUCTURE:
## Executive Summary
[Overall assessment, critical findings, main recommendations]

## Symptom Analysis
[What is actually broken, how it manifests, scope of impact]

## Causal Chain Mapping
[Trace from symptoms to root causes with evidence]

## Root Cause Identification
[For each root cause: why it's a root cause, evidence, contributing factors]

## Cascading Effects
[How the issue propagates, secondary failures, feedback loops]

## Impact Assessment
[Quantified business and technical impact]

## Remediation Options
[Multiple approaches with pros/cons, effort, risk, timeline]

## Recommended Solution
[Specific steps, implementation approach, validation strategy]

## Prevention Measures
[Monitoring, architectural changes, process improvements]

## Risk Assessment
[Risks of proposed fixes, mitigation strategies, rollback plan]"""
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # AUTO-FIXER PROMPTS
    # ============================================================================
    
    @staticmethod
    def generate_code_fix(issue_type: str, function_name: str, 
                         context: str, before_code: Optional[str] = None) -> tuple:
        """
        Advanced prompt for surgical code optimization with comprehensive validation.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class code optimization specialist with expertise in:
- Python performance optimization and micro-optimizations
- Algorithmic complexity reduction and data structure selection
- Memory management and garbage collection optimization
- I/O optimization (disk, network, database)
- Concurrency and parallelization patterns
- Design patterns and architectural optimization
- Code safety and regression prevention

YOUR OPTIMIZATION METHODOLOGY:
1. PROBLEM ANALYSIS:
   - Identify the specific inefficiency (algorithm, data structure, I/O, etc.)
   - Quantify the performance impact
   - Understand the constraints and requirements
   - Identify edge cases and special conditions
   - Analyze the broader context and dependencies

2. SOLUTION DESIGN:
   - Generate multiple optimization approaches
   - Analyze trade-offs (speed vs memory, complexity vs maintainability)
   - Select the optimal approach based on constraints
   - Consider team expertise and code readability
   - Plan for backward compatibility and migration

3. IMPLEMENTATION QUALITY:
   - Minimal, surgical code changes
   - Clear, self-documenting code
   - Comprehensive error handling
   - Edge case coverage
   - Performance validation strategy

4. SAFETY & VALIDATION:
   - Identify potential regressions
   - Design test cases for validation
   - Plan for gradual rollout if needed
   - Create monitoring strategy
   - Prepare rollback plan

5. PERFORMANCE QUANTIFICATION:
   - Estimate speedup (e.g., 2.5x faster)
   - Calculate resource savings (CPU, memory, I/O)
   - Project scalability improvements
   - Assess cost impact
   - Provide confidence levels

OPTIMIZATION PRINCIPLES:
- Correctness first, then optimization
- Measure before and after
- Consider the full system impact
- Document assumptions and constraints
- Plan for long-term maintainability"""
        
        user_prompt = f"""Generate a surgical, production-grade optimization for this {issue_type} issue.

FUNCTION: {function_name}
CONTEXT: {context}

OPTIMIZATION REQUIREMENTS:

1. PROBLEM ANALYSIS:
   - What specifically is inefficient? (algorithm, data structure, I/O, etc.)
   - Why is it inefficient? (complexity analysis, resource usage)
   - What is the current performance? (latency, throughput, resource usage)
   - What are the constraints? (backward compatibility, team expertise, etc.)
   - What are edge cases and special conditions?

2. SOLUTION DESIGN:
   - Generate 2-3 alternative optimization approaches
   - For each approach, analyze:
     * How it solves the problem
     * Performance improvement potential
     * Implementation complexity
     * Risk of regressions
     * Impact on code readability
   - Select the optimal approach with justification

3. IMPLEMENTATION DETAILS:
   - Provide complete, runnable optimized code
   - Maintain backward compatibility
   - Include comprehensive comments explaining changes
   - Handle edge cases explicitly
   - Add error handling and validation
   - Consider thread safety if applicable

4. PERFORMANCE VALIDATION:
   - Quantify expected improvement (e.g., "2.5x faster")
   - Calculate resource savings (CPU, memory, I/O)
   - Explain the basis for performance estimates
   - Identify metrics to measure improvement
   - Design validation test cases

5. REGRESSION PREVENTION:
   - Identify potential side effects
   - Design test cases to prevent regressions
   - Plan for gradual rollout if needed
   - Create monitoring strategy
   - Prepare rollback plan

6. MIGRATION STRATEGY:
   - If breaking changes needed, plan migration
   - Provide deprecation path if applicable
   - Document API changes
   - Create upgrade guide

ANALYSIS METHODOLOGY:
- Use complexity analysis (Big O notation)
- Provide specific code examples
- Support claims with performance reasoning
- Consider multiple optimization approaches
- Explain trade-offs clearly
- Provide confidence levels for estimates

RESPONSE STRUCTURE:
## Problem Analysis
[Specific inefficiency, why it's slow, current performance metrics]

## Alternative Solutions
[2-3 approaches with pros/cons, effort, risk, performance potential]

## Recommended Solution
[Selected approach with detailed justification]

## Implementation
[Complete optimized code with detailed comments]

## Performance Impact
[Quantified improvement, resource savings, scalability impact]

## Validation Strategy
[Test cases, metrics to measure, success criteria]

## Risk Assessment
[Potential regressions, mitigation strategies, rollback plan]

## Migration Plan
[If needed: deprecation path, upgrade guide, timeline]

## Monitoring & Maintenance
[Metrics to track, monitoring strategy, long-term maintenance]"""
        
        if before_code:
            user_prompt += f"\n\nCURRENT CODE:\n```python\n{before_code}\n```\n\nAnalyze this code and provide the optimization."
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # ANOMALY DETECTION PROMPTS
    # ============================================================================
    
    @staticmethod
    def analyze_anomalies(anomalies: str, baseline: Optional[str] = None) -> tuple:
        """
        Advanced prompt for statistical anomaly analysis with predictive insights.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a statistical analyst and system reliability engineer with expertise in:
- Statistical analysis and hypothesis testing
- Time series analysis and trend detection
- Anomaly detection algorithms and thresholds
- System performance monitoring and alerting
- Failure prediction and risk assessment
- Root cause analysis for anomalies
- Capacity planning and resource forecasting

YOUR ANALYSIS FRAMEWORK:
1. ANOMALY CLASSIFICATION:
   - Type: Performance, reliability, resource, pattern, behavioral
   - Severity: Based on deviation magnitude and impact
   - Scope: Single function, subsystem, system-wide
   - Temporal: Transient, persistent, recurring
   - Correlation: Independent vs related anomalies

2. STATISTICAL ANALYSIS:
   - Deviation quantification (standard deviations, percentiles)
   - Statistical significance testing
   - Confidence intervals for estimates
   - Trend analysis and forecasting
   - Correlation analysis with other metrics

3. ROOT CAUSE ANALYSIS:
   - Identify contributing factors
   - Distinguish correlation from causation
   - Analyze temporal relationships
   - Consider external factors (deployments, traffic changes)
   - Evaluate system state at time of anomaly

4. IMPACT ASSESSMENT:
   - Direct performance impact
   - User experience degradation
   - Business impact (revenue, SLA violations)
   - Cascading effects on dependent systems
   - Long-term implications (technical debt, scalability)

5. PREDICTIVE ANALYSIS:
   - Will this anomaly recur?
   - Is the system trending toward failure?
   - What's the risk trajectory?
   - What early warning signs should we monitor?
   - What's the time to critical state?

6. ACTIONABLE RECOMMENDATIONS:
   - Immediate mitigation steps
   - Root cause remediation
   - Preventive measures
   - Monitoring and alerting improvements
   - Capacity planning adjustments"""
        
        user_prompt = f"""Perform comprehensive statistical analysis of these system anomalies.

DETECTED ANOMALIES:
{anomalies}"""
        
        if baseline:
            user_prompt += f"\n\nBASELINE & HISTORICAL DATA:\n{baseline}"
        
        user_prompt += """

ANALYSIS REQUIREMENTS:

1. ANOMALY CLASSIFICATION:
   - Classify each anomaly by type, severity, scope, and temporal pattern
   - Quantify deviation from baseline (standard deviations, percentiles)
   - Assess statistical significance
   - Identify correlations between anomalies

2. STATISTICAL ANALYSIS:
   - Calculate confidence intervals for estimates
   - Perform hypothesis testing on anomaly causes
   - Analyze temporal patterns and trends
   - Identify seasonal or cyclical patterns
   - Assess data quality and outlier impact

3. ROOT CAUSE INVESTIGATION:
   - For each anomaly, identify contributing factors
   - Analyze system state at time of anomaly
   - Consider external factors (deployments, traffic patterns, etc.)
   - Evaluate correlation vs causation
   - Identify hidden dependencies

4. IMPACT QUANTIFICATION:
   - Quantify performance degradation
   - Calculate business impact (affected users, revenue impact)
   - Assess SLA violation risk
   - Evaluate cascading effects
   - Project long-term implications

5. PREDICTIVE ANALYSIS:
   - Will this anomaly recur? (probability and frequency)
   - Is the system trending toward failure?
   - What's the risk trajectory?
   - What early warning signs should we monitor?
   - Time to critical state (if applicable)

6. SEVERITY ASSESSMENT:
   - CRITICAL: Immediate action required, system at risk, SLA violation
   - HIGH: Significant impact, should be addressed in current sprint
   - MEDIUM: Notable deviation, plan fix in next release
   - LOW: Minor anomaly, monitor for trends

7. RECOMMENDED ACTIONS:
   - Immediate mitigation (if needed)
   - Root cause remediation
   - Preventive measures
   - Monitoring and alerting improvements
   - Capacity planning adjustments

ANALYSIS METHODOLOGY:
- Use statistical reasoning with specific calculations
- Support claims with data from the anomalies
- Provide confidence levels for predictions
- Explain assumptions and limitations
- Consider multiple hypotheses
- Distinguish between correlation and causation

RESPONSE STRUCTURE:
## Executive Summary
[Key findings, overall risk assessment, main recommendations]

## Anomaly Classification
[For each: type, severity, scope, temporal pattern, statistical significance]

## Statistical Analysis
[Deviation quantification, significance testing, trend analysis]

## Root Cause Analysis
[Contributing factors, temporal relationships, external influences]

## Impact Assessment
[Performance impact, business impact, cascading effects, long-term implications]

## Predictive Analysis
[Recurrence probability, failure risk trajectory, early warning signs]

## Risk Assessment
[Severity levels, risk scores, time to critical state]

## Recommended Actions
[Immediate mitigation, root cause remediation, preventive measures]

## Monitoring Strategy
[Metrics to track, alert thresholds, early warning indicators]"""
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # SECURITY ANALYSIS PROMPTS
    # ============================================================================
    
    @staticmethod
    def analyze_security_issues(issues: str, code_context: Optional[str] = None) -> tuple:
        """
        Advanced prompt for comprehensive security analysis with threat modeling.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class application security expert with expertise in:
- OWASP Top 10 and CWE/CVSS scoring
- Threat modeling and attack surface analysis
- Secure coding practices and secure design patterns
- Cryptography and authentication/authorization
- Input validation and output encoding
- SQL injection, XSS, CSRF, and injection attacks
- Access control and privilege escalation
- Data protection and privacy
- Security testing and vulnerability assessment
- Compliance (GDPR, HIPAA, PCI-DSS, etc.)

YOUR SECURITY ANALYSIS FRAMEWORK:
1. VULNERABILITY CLASSIFICATION:
   - OWASP category and CWE mapping
   - Attack vector (network, local, physical)
   - Attack complexity (low, high)
   - Privileges required (none, low, high)
   - User interaction (required, not required)
   - Scope (unchanged, changed)
   - Confidentiality/Integrity/Availability impact

2. THREAT MODELING:
   - Identify threat actors and motivations
   - Analyze attack scenarios and exploitation paths
   - Assess likelihood and impact
   - Evaluate business context
   - Consider compliance implications

3. RISK ASSESSMENT:
   - CVSS scoring (base, temporal, environmental)
   - Business impact assessment
   - Exploitability assessment
   - Detectability assessment
   - Remediation complexity

4. EXPLOITATION ANALYSIS:
   - Detailed exploitation scenarios
   - Proof-of-concept code (if applicable)
   - Real-world attack examples
   - Attacker skill level required
   - Tools/techniques used

5. REMEDIATION STRATEGY:
   - Immediate mitigation (if needed)
   - Secure coding fix
   - Architectural improvements
   - Defense-in-depth approach
   - Secure design patterns

6. PREVENTION & HARDENING:
   - Input validation and sanitization
   - Output encoding
   - Authentication/authorization
   - Encryption and key management
   - Error handling and logging
   - Security testing

7. COMPLIANCE & GOVERNANCE:
   - Relevant compliance requirements
   - Audit and logging needs
   - Documentation requirements
   - Incident response implications"""
        
        user_prompt = f"""Perform comprehensive security analysis of these detected vulnerabilities.

SECURITY ISSUES:
{issues}"""
        
        if code_context:
            user_prompt += f"\n\nCODE CONTEXT:\n{code_context}"
        
        user_prompt += """

ANALYSIS REQUIREMENTS:

1. VULNERABILITY CLASSIFICATION:
   - OWASP category and CWE mapping
   - CVSS v3.1 scoring (base metrics)
   - Attack vector and complexity
   - Privileges and user interaction required
   - Impact on confidentiality, integrity, availability

2. THREAT MODELING:
   - Identify potential threat actors
   - Describe realistic attack scenarios
   - Analyze exploitation paths
   - Assess likelihood and impact
   - Consider business context

3. EXPLOITATION ANALYSIS:
   - Detailed step-by-step exploitation scenario
   - Real-world attack examples
   - Proof-of-concept approach (without actual exploit code)
   - Tools and techniques an attacker would use
   - Skill level required for exploitation

4. IMPACT ASSESSMENT:
   - Direct security impact (data breach, unauthorized access, etc.)
   - Business impact (revenue loss, reputation damage, compliance violations)
   - User impact (privacy violation, financial loss, etc.)
   - Cascading effects on dependent systems
   - Long-term implications

5. REMEDIATION STRATEGY:
   - Immediate mitigation (if needed)
   - Secure code fix with explanation
   - Secure design pattern application
   - Defense-in-depth approach
   - Architectural improvements

6. PREVENTION & HARDENING:
   - Input validation and sanitization strategy
   - Output encoding approach
   - Authentication/authorization improvements
   - Encryption and key management
   - Error handling and logging
   - Security testing approach

7. COMPLIANCE & GOVERNANCE:
   - Relevant compliance requirements (GDPR, HIPAA, PCI-DSS, etc.)
   - Audit and logging requirements
   - Documentation needs
   - Incident response implications

8. TESTING & VALIDATION:
   - Security test cases
   - Penetration testing approach
   - Validation strategy
   - Success criteria

ANALYSIS METHODOLOGY:
- Use CVSS scoring for objective severity assessment
- Provide specific exploitation scenarios
- Support claims with real-world examples
- Consider defense-in-depth
- Explain trade-offs between security and usability
- Provide confidence levels for risk assessments

RESPONSE STRUCTURE:
## Executive Summary
[Overall security posture, critical findings, main recommendations]

## Vulnerability Classification
[For each issue: OWASP category, CWE, CVSS score, severity]

## Threat Modeling
[Threat actors, attack scenarios, exploitation paths]

## Exploitation Analysis
[Detailed exploitation scenario, real-world examples, attacker skill level]

## Impact Assessment
[Security impact, business impact, user impact, cascading effects]

## Risk Assessment
[CVSS scoring, business risk, exploitability, detectability]

## Remediation Strategy
[Immediate mitigation, secure code fix, architectural improvements]

## Prevention & Hardening
[Input validation, output encoding, authentication, encryption, logging]

## Compliance Implications
[Relevant regulations, audit requirements, documentation needs]

## Testing & Validation
[Security test cases, penetration testing approach, success criteria]

## Implementation Roadmap
[Priority, effort, dependencies, timeline]"""
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # REFACTORING PROMPTS
    # ============================================================================
    
    @staticmethod
    def suggest_refactoring(function_code: str, metrics: Dict[str, Any]) -> tuple:
        """
        Advanced prompt for architectural refactoring with design patterns.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class software architect with expertise in:
- SOLID principles (Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion)
- Design patterns (creational, structural, behavioral)
- Code smells and anti-patterns
- Refactoring techniques and strategies
- Clean code principles
- Testability and dependency injection
- Performance optimization
- Scalability and maintainability
- Python idioms and best practices

YOUR REFACTORING FRAMEWORK:
1. CODE SMELL DETECTION:
   - Identify all code smells and anti-patterns
   - Classify by severity and impact
   - Trace root causes
   - Assess cascading effects

2. COMPLEXITY ANALYSIS:
   - Cyclomatic complexity (decision points)
   - Cognitive complexity (mental effort)
   - Function length and cohesion
   - Nesting depth and branching
   - Parameter count and coupling

3. DESIGN PATTERN APPLICATION:
   - Identify opportunities for design patterns
   - Evaluate pattern fit and trade-offs
   - Consider implementation complexity
   - Assess long-term maintainability

4. REFACTORING STRATEGY:
   - Generate multiple refactoring approaches
   - Analyze trade-offs for each approach
   - Prioritize by impact and effort
   - Plan incremental refactoring if needed
   - Ensure backward compatibility

5. QUALITY IMPROVEMENTS:
   - Testability enhancement
   - Readability improvement
   - Maintainability increase
   - Performance optimization
   - Scalability improvements

6. VALIDATION & TESTING:
   - Test strategy for refactoring
   - Regression prevention
   - Behavioral preservation
   - Performance validation"""
        
        user_prompt = f"""Perform comprehensive architectural refactoring analysis for this function.

FUNCTION CODE:
```python
{function_code}
```

CURRENT METRICS:
{chr(10).join(f"- {k}: {v}" for k, v in metrics.items())}

REFACTORING REQUIREMENTS:

1. CODE SMELL DETECTION:
   - Identify all code smells and anti-patterns
   - Classify by severity (critical, high, medium, low)
   - Explain why each is a problem
   - Assess impact on maintainability

2. COMPLEXITY ANALYSIS:
   - Analyze cyclomatic complexity (decision points)
   - Analyze cognitive complexity (mental effort)
   - Identify nesting depth issues
   - Assess parameter coupling
   - Evaluate function cohesion

3. DESIGN PATTERN OPPORTUNITIES:
   - Identify applicable design patterns
   - Evaluate pattern fit and benefits
   - Assess implementation complexity
   - Consider long-term maintainability
   - Analyze trade-offs

4. REFACTORING STRATEGIES:
   - Generate 2-3 refactoring approaches
   - For each approach:
     * Explain the refactoring technique
     * Show refactored code
     * Quantify improvements
     * Assess implementation effort
     * Evaluate risk and trade-offs
   - Recommend optimal approach

5. QUALITY IMPROVEMENTS:
   - How refactoring improves testability
   - How it enhances readability
   - How it increases maintainability
   - Performance implications
   - Scalability improvements

6. IMPLEMENTATION STRATEGY:
   - Incremental refactoring plan if needed
   - Backward compatibility approach
   - Test strategy
   - Validation approach
   - Timeline and effort

ANALYSIS METHODOLOGY:
- Use SOLID principles as framework
- Provide specific code examples
- Quantify improvements (complexity reduction, etc.)
- Consider team expertise and constraints
- Explain trade-offs clearly
- Provide confidence levels for estimates

RESPONSE STRUCTURE:
## Executive Summary
[Key findings, main refactoring opportunities, expected improvements]

## Code Smell Analysis
[For each smell: description, severity, impact, root cause]

## Complexity Assessment
[Cyclomatic complexity, cognitive complexity, nesting, coupling analysis]

## Design Pattern Opportunities
[Applicable patterns, benefits, implementation complexity]

## Refactoring Strategies
[2-3 approaches with pros/cons, effort, risk, improvements]

## Recommended Refactoring
[Selected approach with detailed explanation]

## Refactored Code
[Complete refactored code with comments]

## Quality Improvements
[Testability, readability, maintainability, performance, scalability]

## Implementation Plan
[Incremental steps, backward compatibility, test strategy, timeline]

## Risk Assessment
[Potential issues, mitigation strategies, validation approach]"""
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # TEST GENERATION PROMPTS
    # ============================================================================
    
    @staticmethod
    def generate_tests(function_code: str, function_name: str) -> tuple:
        """
        Advanced prompt for comprehensive test generation with coverage strategy.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class QA engineer and test architect with expertise in:
- Unit testing and test-driven development (TDD)
- pytest framework and advanced testing patterns
- Edge case and boundary condition identification
- Mock/stub/spy strategies and dependency injection
- Code coverage analysis and coverage-driven testing
- Performance and load testing
- Integration and end-to-end testing
- Test data generation and fixtures
- Regression testing and test maintenance
- Mutation testing and test quality

YOUR TEST GENERATION FRAMEWORK:
1. COVERAGE ANALYSIS:
   - Identify all code paths and branches
   - Analyze decision points and conditions
   - Map edge cases and boundary conditions
   - Identify error paths and exceptions
   - Calculate coverage requirements

2. TEST CASE DESIGN:
   - Happy path (normal operation)
   - Edge cases (boundaries, special values)
   - Error cases (invalid inputs, exceptions)
   - Performance cases (execution time, memory)
   - Integration cases (dependencies, side effects)

3. TEST QUALITY:
   - Clear, descriptive test names
   - AAA pattern (Arrange, Act, Assert)
   - Single responsibility per test
   - Comprehensive assertions
   - Proper test isolation

4. MOCK STRATEGY:
   - Identify external dependencies
   - Design mock/stub/spy strategy
   - Ensure proper isolation
   - Validate mock behavior
   - Test with and without mocks

5. PARAMETRIZATION:
   - Use pytest.mark.parametrize for multiple cases
   - Data-driven testing approach
   - Reduce test code duplication
   - Improve test maintainability

6. COVERAGE TARGETS:
   - Line coverage > 90%
   - Branch coverage > 85%
   - All error paths tested
   - All edge cases covered
   - Mutation testing resistant"""
        
        user_prompt = f"""Generate comprehensive, production-grade tests for this function.

FUNCTION NAME: {function_name}

FUNCTION CODE:
```python
{function_code}
```

TEST GENERATION REQUIREMENTS:

1. COVERAGE ANALYSIS:
   - Identify all code paths and branches
   - Map all decision points
   - Identify edge cases and boundaries
   - List all error conditions
   - Analyze dependencies

2. TEST CASE DESIGN:
   - Happy path tests (normal operation with valid inputs)
   - Edge case tests (boundaries, special values, empty inputs)
   - Error case tests (invalid inputs, exceptions, error conditions)
   - Performance tests (execution time, memory usage if applicable)
   - Integration tests (with dependencies if applicable)

3. MOCK STRATEGY:
   - Identify external dependencies (I/O, network, database, etc.)
   - Design mock/stub strategy for each dependency
   - Plan for testing with and without mocks
   - Ensure proper test isolation
   - Validate mock behavior

4. TEST IMPLEMENTATION:
   - Use pytest framework
   - Follow AAA pattern (Arrange, Act, Assert)
   - Use pytest.mark.parametrize for multiple test cases
   - Include comprehensive docstrings
   - Add clear assertions with meaningful messages
   - Use fixtures for common setup
   - Mock external dependencies properly

5. COVERAGE TARGETS:
   - Achieve > 90% line coverage
   - Achieve > 85% branch coverage
   - Test all error paths
   - Cover all edge cases
   - Resistant to mutation testing

6. TEST QUALITY:
   - Descriptive test names (test_<function>_<scenario>_<expected>)
   - Single responsibility per test
   - No test interdependencies
   - Proper test isolation
   - Clear, maintainable code

ANALYSIS METHODOLOGY:
- Analyze code structure to identify paths
- Consider all input combinations
- Identify boundary conditions
- Plan for error scenarios
- Design for maintainability
- Aim for mutation-resistant tests

RESPONSE STRUCTURE:
## Coverage Analysis
[Code paths, branches, edge cases, error conditions]

## Test Strategy
[Happy path, edge cases, error cases, performance, integration]

## Mock Strategy
[Dependencies, mocking approach, isolation strategy]

## Test Implementation
[Complete pytest code with all test cases]

## Coverage Report
[Expected line coverage, branch coverage, gaps]

## Test Execution Guide
[How to run tests, expected results, debugging tips]"""
        
        return system_prompt, user_prompt
    
    # ============================================================================
    # DOCUMENTATION PROMPTS
    # ============================================================================
    
    @staticmethod
    def generate_documentation(function_code: str, function_name: str) -> tuple:
        """
        Advanced prompt for comprehensive technical documentation.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are a world-class technical writer and documentation architect with expertise in:
- Google-style docstrings and PEP 257 conventions
- API documentation and developer guides
- Code examples and usage patterns
- Performance and complexity documentation
- Error handling and exception documentation
- Type hints and type annotations
- Markdown and reStructuredText formatting
- API reference documentation
- Architecture and design documentation
- Migration guides and deprecation notices

YOUR DOCUMENTATION FRAMEWORK:
1. COMPREHENSIVE DESCRIPTION:
   - What the function does (purpose and use cases)
   - Why it exists (problem it solves)
   - When to use it (appropriate scenarios)
   - When not to use it (anti-patterns)
   - Related functions and alternatives

2. PARAMETER DOCUMENTATION:
   - Type hints and type descriptions
   - Valid value ranges and constraints
   - Default values and their implications
   - Optional vs required parameters
   - Special parameter handling

3. RETURN VALUE DOCUMENTATION:
   - Return type and structure
   - Possible return values
   - Special return cases
   - Null/None handling
   - Side effects

4. EXCEPTION DOCUMENTATION:
   - All exceptions that may be raised
   - Conditions that trigger each exception
   - How to handle each exception
   - Recovery strategies
   - Prevention approaches

5. USAGE EXAMPLES:
   - Basic usage examples
   - Advanced usage patterns
   - Common use cases
   - Edge case handling
   - Error handling examples

6. PERFORMANCE & COMPLEXITY:
   - Time complexity (Big O notation)
   - Space complexity
   - Performance characteristics
   - Optimization opportunities
   - Scalability considerations

7. DESIGN & ARCHITECTURE:
   - Design patterns used
   - Architectural decisions
   - Dependencies and relationships
   - Thread safety (if applicable)
   - Concurrency considerations

8. MAINTENANCE & EVOLUTION:
   - Known limitations
   - Future improvements
   - Deprecation notices
   - Migration guides
   - Backward compatibility notes"""
        
        user_prompt = f"""Generate comprehensive, production-grade documentation for this function.

FUNCTION NAME: {function_name}

FUNCTION CODE:
```python
{function_code}
```

DOCUMENTATION REQUIREMENTS:

1. FUNCTION DESCRIPTION:
   - Clear, concise description of what the function does
   - Purpose and use cases
   - Problem it solves
   - When to use it (and when not to)
   - Related functions and alternatives

2. PARAMETER DOCUMENTATION:
   - Type hints with descriptions
   - Valid value ranges and constraints
   - Default values and implications
   - Optional vs required parameters
   - Special handling or validation

3. RETURN VALUE DOCUMENTATION:
   - Return type and structure
   - Possible return values
   - Special return cases
   - Null/None handling
   - Side effects (if any)

4. EXCEPTION DOCUMENTATION:
   - All exceptions that may be raised
   - Conditions triggering each exception
   - How to handle each exception
   - Recovery strategies
   - Prevention approaches

5. USAGE EXAMPLES:
   - Basic usage example
   - Advanced usage patterns
   - Common use cases
   - Edge case handling
   - Error handling examples

6. PERFORMANCE & COMPLEXITY:
   - Time complexity (Big O notation)
   - Space complexity
   - Performance characteristics
   - Optimization opportunities
   - Scalability considerations

7. DESIGN & ARCHITECTURE:
   - Design patterns used
   - Architectural decisions
   - Dependencies and relationships
   - Thread safety (if applicable)
   - Concurrency considerations

8. MAINTENANCE & EVOLUTION:
   - Known limitations
   - Future improvements
   - Deprecation notices (if applicable)
   - Migration guides (if applicable)
   - Backward compatibility notes

DOCUMENTATION STANDARDS:
- Use Google-style docstring format
- Include type hints in documentation
- Provide clear, concise descriptions
- Use proper Markdown formatting
- Include code examples where helpful
- Document all edge cases
- Explain complex logic

RESPONSE STRUCTURE:
## Function Overview
[Purpose, use cases, when to use]

## Google-Style Docstring
[Complete docstring with all sections]

## Detailed Explanation
[Complex logic explanation, design decisions]

## Usage Examples
[Basic and advanced examples]

## Performance & Complexity
[Time/space complexity, optimization notes]

## Exception Handling
[All exceptions, handling strategies]

## Related Functions
[Related functions, alternatives, patterns]

## Notes & Limitations
[Known limitations, future improvements]"""
        
        return system_prompt, user_prompt


def get_prompt_for_task(task_type: str, **kwargs) -> tuple:
    """
    Get enhanced prompt template for a specific task.
    
    Args:
        task_type: Type of analysis task
        **kwargs: Task-specific parameters
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    
    Example:
        >>> system, user = get_prompt_for_task(
        ...     'performance_analysis',
        ...     graph_summary='...',
        ...     question='...'
        ... )
    """
    task_handlers = {
        'performance_analysis': PromptTemplates.query_performance_analysis,
        'root_cause_analysis': PromptTemplates.root_cause_analysis,
        'code_fix': PromptTemplates.generate_code_fix,
        'anomaly_analysis': PromptTemplates.analyze_anomalies,
        'security_analysis': PromptTemplates.analyze_security_issues,
        'refactoring': PromptTemplates.suggest_refactoring,
        'test_generation': PromptTemplates.generate_tests,
        'documentation': PromptTemplates.generate_documentation,
    }
    
    if task_type not in task_handlers:
        raise ValueError(f"Unknown task type: {task_type}")
    
    handler = task_handlers[task_type]
    return handler(**kwargs)
