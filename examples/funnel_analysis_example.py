#!/usr/bin/env python3
"""
Comprehensive Funnel Analysis Example

This example demonstrates how to use CallFlow Tracer's funnel analysis
capabilities to track user journeys, analyze performance, and generate insights.
"""

import time
import random
from pathlib import Path
from callflow_tracer import (
    FunnelType,
    StepStatus,
    funnel_scope,
    create_funnel_visualizer,
    generate_funnel_dashboard,
    analyze_funnel_anomalies,
    predict_funnel_performance,
    generate_optimization_plan,
)


def simulate_user_registration():
    """Simulate a user registration funnel"""
    print("=== User Registration Funnel Analysis ===\n")

    # Create funnel analyzer
    with funnel_scope("user_registration", FunnelType.CONVERSION) as analyzer:
        # Define funnel steps
        analyzer.add_step("landing_page", "User visits landing page")
        analyzer.add_step("signup_form", "User views signup form")
        analyzer.add_step("form_validation", "Form validation and submission")
        analyzer.add_step("email_verification", "Email verification process")
        analyzer.add_step("profile_completion", "User completes profile")
        analyzer.add_step("welcome_email", "Welcome email sent")

        # Simulate user sessions
        for i in range(100):
            session = analyzer.start_session(user_id=f"user_{i}")

            # Landing page (100% visit)
            time.sleep(0.001)  # Simulate page load time
            analyzer.track_step(
                session.session_id, "landing_page", StepStatus.SUCCESS, 1000
            )

            # Signup form (80% proceed)
            if random.random() < 0.8:
                time.sleep(0.002)
                analyzer.track_step(
                    session.session_id, "signup_form", StepStatus.SUCCESS, 2000
                )

                # Form validation (70% pass)
                if random.random() < 0.7:
                    time.sleep(0.001)
                    analyzer.track_step(
                        session.session_id, "form_validation", StepStatus.SUCCESS, 1000
                    )

                    # Email verification (60% complete)
                    if random.random() < 0.6:
                        time.sleep(0.003)
                        analyzer.track_step(
                            session.session_id,
                            "email_verification",
                            StepStatus.SUCCESS,
                            3000,
                        )

                        # Profile completion (50% complete)
                        if random.random() < 0.5:
                            time.sleep(0.002)
                            analyzer.track_step(
                                session.session_id,
                                "profile_completion",
                                StepStatus.SUCCESS,
                                2000,
                            )

                            # Welcome email (90% sent)
                            if random.random() < 0.9:
                                time.sleep(0.001)
                                analyzer.track_step(
                                    session.session_id,
                                    "welcome_email",
                                    StepStatus.SUCCESS,
                                    1000,
                                )
                                analyzer.complete_session(
                                    session.session_id,
                                    StepStatus.SUCCESS,
                                    conversion_value=25.0,
                                )
                            else:
                                analyzer.complete_session(
                                    session.session_id, StepStatus.FAILURE
                                )
                        else:
                            analyzer.complete_session(
                                session.session_id, StepStatus.FAILURE
                            )
                    else:
                        # Some users have email verification errors
                        if random.random() < 0.1:
                            analyzer.track_step(
                                session.session_id,
                                "email_verification",
                                StepStatus.ERROR,
                                5000,
                                "Email service unavailable",
                            )
                        analyzer.complete_session(
                            session.session_id, StepStatus.FAILURE
                        )
                else:
                    # Form validation failures
                    analyzer.track_step(
                        session.session_id, "form_validation", StepStatus.FAILURE, 1500
                    )
                    analyzer.complete_session(session.session_id, StepStatus.FAILURE)
            else:
                # Users who don't proceed to signup
                analyzer.complete_session(session.session_id, StepStatus.FAILURE)

        # Get analytics
        analytics = analyzer.get_analytics()

        print("Funnel Analytics:")
        print(f"Total Sessions: {analytics['conversion_metrics']['total_sessions']}")
        print(
            f"Completed Sessions: {analytics['conversion_metrics']['completed_sessions']}"
        )
        print(
            f"Overall Conversion Rate: {analytics['conversion_metrics']['overall_conversion_rate']:.1f}%"
        )

        print("\nStep-by-Step Analysis:")
        for step in analytics["steps"]:
            print(f"  {step['name']}:")
            print(f"    Users: {step['total_users']}")
            print(f"    Conversion: {step['conversion_rate']:.1f}%")
            print(f"    Dropoff: {step['dropoff_rate']:.1f}%")
            print(f"    Avg Time: {step['avg_time_ms']:.0f}ms")
            if step["error_rate"] > 0:
                print(f"    Error Rate: {step['error_rate']:.1f}%")

        return analyzer


def simulate_api_performance_funnel():
    """Simulate an API performance funnel"""
    print("\n=== API Performance Funnel Analysis ===\n")

    with funnel_scope("api_performance", FunnelType.PERFORMANCE) as analyzer:
        # Define API funnel steps
        analyzer.add_step("request_received", "HTTP request received")
        analyzer.add_step("authentication", "User authentication")
        analyzer.add_step("authorization", "Permission check")
        analyzer.add_step("validation", "Input validation")
        analyzer.add_step("business_logic", "Business logic processing")
        analyzer.add_step("database_query", "Database operations")
        analyzer.add_step("response_generation", "Response creation")
        analyzer.add_step("response_sent", "HTTP response sent")

        # Simulate API calls
        for i in range(200):
            session = analyzer.start_session(user_id=f"client_{i}")

            # Request received
            analyzer.track_step(
                session.session_id, "request_received", StepStatus.SUCCESS, 1
            )

            # Authentication (95% success)
            if random.random() < 0.95:
                auth_time = random.uniform(50, 150)
                analyzer.track_step(
                    session.session_id, "authentication", StepStatus.SUCCESS, auth_time
                )

                # Authorization (98% success)
                if random.random() < 0.98:
                    authz_time = random.uniform(20, 50)
                    analyzer.track_step(
                        session.session_id,
                        "authorization",
                        StepStatus.SUCCESS,
                        authz_time,
                    )

                    # Validation (90% success)
                    if random.random() < 0.9:
                        val_time = random.uniform(10, 30)
                        analyzer.track_step(
                            session.session_id,
                            "validation",
                            StepStatus.SUCCESS,
                            val_time,
                        )

                        # Business logic (variable performance)
                        biz_time = random.uniform(100, 500)
                        analyzer.track_step(
                            session.session_id,
                            "business_logic",
                            StepStatus.SUCCESS,
                            biz_time,
                        )

                        # Database query (sometimes slow)
                        if random.random() < 0.1:  # 10% slow queries
                            db_time = random.uniform(1000, 3000)
                        else:
                            db_time = random.uniform(50, 200)
                        analyzer.track_step(
                            session.session_id,
                            "database_query",
                            StepStatus.SUCCESS,
                            db_time,
                        )

                        # Response generation
                        resp_time = random.uniform(20, 100)
                        analyzer.track_step(
                            session.session_id,
                            "response_generation",
                            StepStatus.SUCCESS,
                            resp_time,
                        )

                        # Response sent
                        analyzer.track_step(
                            session.session_id, "response_sent", StepStatus.SUCCESS, 5
                        )

                        analyzer.complete_session(
                            session.session_id, StepStatus.SUCCESS
                        )
                    else:
                        # Validation errors
                        analyzer.track_step(
                            session.session_id,
                            "validation",
                            StepStatus.ERROR,
                            25,
                            "Invalid input format",
                        )
                        analyzer.complete_session(
                            session.session_id, StepStatus.FAILURE
                        )
                else:
                    # Authorization failures
                    analyzer.track_step(
                        session.session_id, "authorization", StepStatus.FAILURE, 30
                    )
                    analyzer.complete_session(session.session_id, StepStatus.FAILURE)
            else:
                # Authentication failures
                analyzer.track_step(
                    session.session_id,
                    "authentication",
                    StepStatus.ERROR,
                    100,
                    "Invalid credentials",
                )
                analyzer.complete_session(session.session_id, StepStatus.FAILURE)

        # Get performance analytics
        analytics = analyzer.get_analytics()

        print("API Performance Analysis:")
        print(f"Total Requests: {analytics['conversion_metrics']['total_sessions']}")
        print(
            f"Successful Requests: {analytics['conversion_metrics']['completed_sessions']}"
        )
        print(
            f"Success Rate: {analytics['conversion_metrics']['overall_conversion_rate']:.1f}%"
        )

        print("\nPerformance Metrics:")
        perf_metrics = analytics["performance_metrics"]
        print(f"Average Step Time: {perf_metrics['average_step_time_ms']:.1f}ms")
        print(f"Slowest Step: {perf_metrics['slowest_step']}")
        print(f"Fastest Step: {perf_metrics['fastest_step']}")

        print("\nStep Performance:")
        for step in analytics["steps"]:
            print(f"  {step['name']}:")
            print(f"    Avg Time: {step['avg_time_ms']:.1f}ms")
            print(f"    Median Time: {step.get('median_time_ms', 0):.1f}ms")
            print(f"    P95 Time: {step.get('p95_time_ms', 0):.1f}ms")
            print(f"    Success Rate: {step['conversion_rate']:.1f}%")

        return analyzer


def demonstrate_advanced_features(analyzer):
    """Demonstrate advanced funnel analysis features"""
    print("\n=== Advanced Funnel Analysis Features ===\n")

    # Anomaly detection
    print("1. Anomaly Detection:")
    anomalies = analyze_funnel_anomalies(analyzer)
    if anomalies:
        for anomaly in anomalies[:3]:  # Show top 3
            print(f"   [{anomaly.severity.upper()}] {anomaly.anomaly_type}")
            print(f"   Description: {anomaly.description}")
            print(f"   Confidence: {anomaly.confidence:.2f}")
            if anomaly.recommendations:
                print(f"   Recommendation: {anomaly.recommendations[0]}")
            print()
    else:
        print("   No significant anomalies detected.\n")

    # Predictive analysis
    print("2. Predictive Analysis:")
    predictions = predict_funnel_performance(analyzer, "next_hour")
    for prediction in predictions:
        print(f"   {prediction.prediction_type}:")
        print(f"   Predicted Value: {prediction.predicted_value:.2f}")
        print(f"   Confidence: {prediction.confidence:.2f}")
        print(f"   Time Horizon: {prediction.time_horizon}")
        print()

    # Optimization plan
    print("3. Optimization Plan:")
    plan = generate_optimization_plan(analyzer)
    summary = plan.get("summary", {})
    print(
        f"   Current Conversion Rate: {summary.get('current_performance', {}).get('conversion_rate', 0):.1f}%"
    )
    print(
        f"   Potential Improvement: +{summary.get('optimization_potential', {}).get('conversion_improvement', 0):.1f}%"
    )

    priorities = plan.get("priorities", [])
    if priorities:
        print(f"   Top Priority: {priorities[0]['title']}")
        print(f"   Impact: {priorities[0]['impact']}")
        print(f"   Effort: {priorities[0]['effort']}")

    print()


def demonstrate_visualizations(analyzer):
    """Demonstrate funnel visualization capabilities"""
    print("=== Funnel Visualization ===\n")

    # Create visualizer
    visualizer = create_funnel_visualizer(analyzer)

    # Generate funnel chart
    funnel_chart = visualizer.generate_funnel_chart("standard", "default", True)
    print("1. Standard Funnel Chart Generated:")
    print(f"   Steps: {len(funnel_chart['steps'])}")
    print(f"   Chart Type: {funnel_chart['type']}")
    print(f"   Style: {funnel_chart['style']}")

    # Generate performance chart
    perf_chart = visualizer.generate_performance_chart("timeline")
    print("\n2. Performance Timeline Chart Generated:")
    print(f"   Series: {len(perf_chart['series'])}")
    print(f"   Chart Type: {perf_chart['type']}")

    # Generate error analysis chart
    error_chart = visualizer.generate_error_analysis_chart()
    print("\n3. Error Analysis Chart Generated:")
    print(f"   Charts: {list(error_chart['charts'].keys())}")

    # Generate dashboard
    dashboard = generate_funnel_dashboard(analyzer)
    print("\n4. Comprehensive Dashboard Generated:")
    print(f"   Widgets: {len(dashboard['widgets'])}")
    print(f"   Theme: {dashboard['theme']}")

    # Export visualizations
    try:
        funnel_html = visualizer.export_visualization("funnel", "html")
        print("\n5. Visualization Export:")
        print(f"   Funnel HTML exported (length: {len(funnel_html)} chars)")

        # Save to file (in examples folder next to this script)
        out_path = Path(__file__).with_name("funnel_visualization.html")
        with open(out_path, "w") as f:
            f.write(funnel_html)
        print(f"   Saved to: {out_path}")

    except Exception as e:
        print(f"   Export error: {e}")

    print()


def main():
    """Main demonstration function"""
    print("CallFlow Tracer - Funnel Analysis Demo")
    print("=" * 50)

    # Run user registration funnel
    reg_analyzer = simulate_user_registration()

    # Run API performance funnel
    simulate_api_performance_funnel()

    # Demonstrate advanced features
    demonstrate_advanced_features(reg_analyzer)

    # Demonstrate visualizations
    demonstrate_visualizations(reg_analyzer)

    print("=== Demo Complete ===")
    print(
        f"Check {Path(__file__).with_name('funnel_visualization.html')} for interactive funnel visualization"
    )


if __name__ == "__main__":
    main()
