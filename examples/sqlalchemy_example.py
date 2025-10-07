"""
SQLAlchemy integration example with callflow-tracer.

This example uses an in-memory SQLite database so it runs instantly and without
external dependencies. It demonstrates how to instrument a SQLAlchemy Engine to
record query timings into the callflow trace.

Run:
    python sqlalchemy_example.py
"""

from sqlalchemy import create_engine, text

from callflow_tracer import trace_scope
from callflow_tracer.integrations.sqlalchemy_integration import (
    instrument_sqlalchemy_engine,
)


def main() -> None:
    """Create an engine, instrument it, and run a few quick queries."""
    # Use in-memory SQLite for a fast, dependency-free demo
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    # Attach listeners that capture timings for each executed statement
    instrument_sqlalchemy_engine(engine, label="sqlalchemy.query")

    # Trace everything in this scope and write an interactive HTML
    with trace_scope("sqlalchemy_trace.html"):
        # Create a demo table, insert some rows, then read them back
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                    """
                )
            )

            conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"},
                    {"name": "Carol", "email": "carol@example.com"},
                ],
            )

            rows = conn.execute(text("SELECT id, name, email FROM users ORDER BY id"))
            for row in rows:
                # Print results so you see the example running
                print(dict(row._mapping))

    print("\nTrace saved to 'sqlalchemy_trace.html'")


if __name__ == "__main__":
    main()


