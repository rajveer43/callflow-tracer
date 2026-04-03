#!/usr/bin/env python3
"""
Funnel Analysis Quick Start Guide

This example shows the quickest way to get started with funnel analysis
in CallFlow Tracer.
"""

from callflow_tracer import (
    FunnelAnalyzer,
    FunnelType,
    StepStatus,
    funnel_scope,
    create_funnel_visualizer,
)


def quick_funnel_example():
    """Quick funnel analysis example"""

    # Method 1: Using context manager (recommended)
    with funnel_scope("checkout_funnel", FunnelType.CONVERSION) as analyzer:
        # Define your funnel steps
        analyzer.add_step("view_product", "Customer views product")
        analyzer.add_step("add_to_cart", "Customer adds to cart")
        analyzer.add_step("checkout", "Customer starts checkout")
        analyzer.add_step("payment", "Customer completes payment")

        # Simulate some user sessions
        for i in range(50):
            session = analyzer.start_session(user_id=f"user_{i}")

            # Track user progress through funnel
            analyzer.track_step(
                session.session_id, "view_product", StepStatus.SUCCESS, 1000
            )

            # 80% add to cart
            if i % 5 != 0:
                analyzer.track_step(
                    session.session_id, "add_to_cart", StepStatus.SUCCESS, 2000
                )

                # 60% proceed to checkout
                if i % 5 < 3:
                    analyzer.track_step(
                        session.session_id, "checkout", StepStatus.SUCCESS, 3000
                    )

                    # 40% complete payment
                    if i % 5 < 2:
                        analyzer.track_step(
                            session.session_id, "payment", StepStatus.SUCCESS, 5000
                        )
                        analyzer.complete_session(
                            session.session_id, StepStatus.SUCCESS, 50.0
                        )
                    else:
                        analyzer.complete_session(
                            session.session_id, StepStatus.FAILURE
                        )
                else:
                    analyzer.complete_session(session.session_id, StepStatus.FAILURE)
            else:
                analyzer.complete_session(session.session_id, StepStatus.FAILURE)

        # Get analytics
        analytics = analyzer.get_analytics()

        print("Quick Funnel Results:")
        print(
            f"Conversion Rate: {analytics['conversion_metrics']['overall_conversion_rate']:.1f}%"
        )
        print(f"Total Sessions: {analytics['conversion_metrics']['total_sessions']}")

        # Generate visualization
        visualizer = create_funnel_visualizer(analyzer)
        visualizer.generate_funnel_chart()

        # Export to HTML (save inside examples folder for easy preview)
        from pathlib import Path

        html_content = visualizer.export_visualization("funnel", "html")
        out_path = Path(__file__).with_name("quick_funnel.html")
        with open(out_path, "w") as f:
            f.write(html_content)

        print(f"Visualization saved to: {out_path}")

        return analyzer


def method_2_programmatic():
    """Method 2: Programmatic funnel creation"""

    # Create analyzer directly
    analyzer = FunnelAnalyzer("api_performance", FunnelType.PERFORMANCE)

    # Add steps
    analyzer.add_step("request", "HTTP request received")
    analyzer.add_step("auth", "Authentication")
    analyzer.add_step("process", "Business logic")
    analyzer.add_step("response", "Response sent")

    # Track a session
    session = analyzer.start_session("client_123")
    analyzer.track_step(session.session_id, "request", StepStatus.SUCCESS, 10)
    analyzer.track_step(session.session_id, "auth", StepStatus.SUCCESS, 100)
    analyzer.track_step(session.session_id, "process", StepStatus.SUCCESS, 500)
    analyzer.track_step(session.session_id, "response", StepStatus.SUCCESS, 20)
    analyzer.complete_session(session.session_id, StepStatus.SUCCESS)

    # Get results
    analytics = analyzer.get_analytics()
    print("API Performance Results:")
    for step in analytics["steps"]:
        print(f"{step['name']}: {step['avg_time_ms']:.1f}ms average")

    return analyzer


if __name__ == "__main__":
    print("Funnel Analysis Quick Start")
    print("=" * 40)

    # Try both methods
    analyzer1 = quick_funnel_example()
    print()
    analyzer2 = method_2_programmatic()

    print("\nQuick start complete!")
    from pathlib import Path

    print(f"Check {Path(__file__).with_name('quick_funnel.html')} for visualization")
