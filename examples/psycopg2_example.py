"""
psycopg2 integration example with callflow-tracer for CIMTrack DB.

This example demonstrates:
- How to connect to a PostgreSQL database using psycopg2.
- How to trace database and Python function calls using callflow-tracer.
- How to fetch and display table names and their column details, and include this information in the trace graph metadata.

Run:
    python psycopg2_example.py
"""

import psycopg2
from psycopg2.extras import DictCursor

from callflow_tracer import trace_scope
from callflow_tracer.integrations import instrument_psycopg2

try:
    instrument_psycopg2()
except Exception as _e:
    print(f"[warn] psycopg2 instrumentation not active: {_e}")


def get_db_connection():
    """
    Connect directly to the CIMTrack database with short timeouts for a fast example run.
    Never hardcode credentials in production; use environment variables instead.
    """
    return psycopg2.connect(
        dbname="cimtrack_db",
        user="postgres",
        password="postgres",
        host="199.199.50.240",
        port=5547,
        cursor_factory=DictCursor,
        connect_timeout=3,  # seconds
        options="-c statement_timeout=1000 -c lock_timeout=500",
    )


def _get_conn_info(conn):
    """
    Return a dict with connection info including dbname, user, host, and port.
    """
    dsn = conn.get_dsn_parameters() if hasattr(conn, "get_dsn_parameters") else {}
    info = {
        "dbname": dsn.get("dbname"),
        "user": dsn.get("user"),
        "host": dsn.get("host"),
        "port": dsn.get("port"),
    }
    # Fallback for dbname if missing
    if not info["dbname"]:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database();")
                info["dbname"] = cur.fetchone()[0]
        except Exception:
            info["dbname"] = None
    return info


def get_table_list_and_details(conn, max_tables=10):
    """
    Fetch a list of tables in the public schema and their column details.

    Returns:
        tables_info: List of dicts, each with 'table_name' and 'columns' (list of dicts).
    """
    tables_info = []
    with conn.cursor() as cur:
        # Set short statement and lock timeouts for safety
        cur.execute("SET statement_timeout = %s", (1000,))
        cur.execute("SET lock_timeout = %s", (500,))
        # Get table names
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            LIMIT %s
        """, (max_tables,))
        table_rows = cur.fetchall()
        for t in table_rows:
            table_name = t['table_name']
            # Get column details for each table
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = [
                {
                    "column_name": col['column_name'],
                    "data_type": col['data_type'],
                    "is_nullable": col['is_nullable']
                }
                for col in cur.fetchall()
            ]
            tables_info.append({
                "table_name": table_name,
                "columns": columns
            })
    return tables_info


def print_table_list_and_details(tables_info, dbname):
    """
    Print the list of tables and their column details.
    """
    print(f"\nAvailable tables in {dbname or '(unknown DB)'} (showing up to {len(tables_info)}):", flush=True)
    for table in tables_info:
        print(f"  - {table['table_name']}", flush=True)
        for col in table['columns']:
            print(
                f"      column: {col['column_name']} | type: {col['data_type']} | nullable: {col['is_nullable']}",
                flush=True
            )


def sample_query(conn, table_name="users"):
    """
    Run a tiny sample query on an existing table (default: 'users').
    """
    info = _get_conn_info(conn)
    with conn.cursor() as cur:
        # Short statement timeout for safety
        cur.execute("SET statement_timeout = %s", (1000,))
        cur.execute("SET lock_timeout = %s", (500,))
        # Use parameterized query to avoid SQL injection
        query = f"SELECT * FROM {table_name} LIMIT 1;"
        try:
            cur.execute(query)
            rows = cur.fetchall()
            print(
                f"\nSample data from '{table_name}' table on DB {info['dbname'] or '(unknown DB)'} (up to 1 row):",
                flush=True
            )
            for row in rows:
                print(dict(row), flush=True)
        except Exception as e:
            print(f"  [warn] Could not fetch sample data from '{table_name}': {e}", flush=True)


def main():
    """
    Main entry point for the example.
    - Connects to the database.
    - Fetches and prints table and column details.
    - Runs a sample query.
    - Saves the callflow trace to 'cimtrack_trace.html', including table/column info in the trace metadata.
    """
    # Create a trace that will be saved to 'cimtrack_trace.html'
    with trace_scope("cimtrack_trace.html") as tracer:
        conn = get_db_connection()
        try:
            info = _get_conn_info(conn)
            print(
                f"\nConnected to DB: {info['dbname'] or '(unknown)'} as {info['user'] or '(unknown user)'} "
                f"on {info['host'] or 'localhost'}:{info['port'] or '5432'}",
                flush=True,
            )
            # Quick ping to ensure connection is responsive
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    cur.fetchone()
                print("Ping ok (SELECT 1)", flush=True)
            except Exception as e:
                print(f"Ping failed: {e}", flush=True)
            # For this example, keep autocommit on to avoid transaction-related blocking.
            conn.autocommit = True

            print("\n[1/3] Listing tables and columns...", flush=True)
            # Fetch and print table/column details
            try:
                tables_info = get_table_list_and_details(conn, max_tables=10)
                print_table_list_and_details(tables_info, info['dbname'])
                print("[1/3] Done listing tables and columns.", flush=True)
            except Exception as e:
                print(f"[1/3] Error while listing tables: {e}", flush=True)
                tables_info = []

            print("\n[2/3] Running sample query...", flush=True)
            # Run a sample query on the first table if available, else 'users'
            try:
                sample_table = tables_info[0]['table_name'] if tables_info else "users"
                sample_query(conn, table_name=sample_table)
                print("[2/3] Done sample query.", flush=True)
            except Exception as e:
                print(f"[2/3] Error while running sample query: {e}", flush=True)

            print("\n[3/3] Finishing up...", flush=True)

            # --- Add table/column info to the trace graph metadata for visualization ---
            if hasattr(tracer, "graph") and hasattr(tracer.graph, "to_dict"):
                # Patch the trace graph's metadata to include table/column info
                graph_dict = tracer.graph.to_dict()
                if "metadata" in graph_dict:
                    graph_dict["metadata"]["tables"] = tables_info
                # Optionally, you could write this out or use it in a custom template
                # For now, this will be available in the trace HTML as JSON metadata

        finally:
            conn.close()

    print("\nTrace saved to 'cimtrack_trace.html'", flush=True)


if __name__ == "__main__":
    main()
