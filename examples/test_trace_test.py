from callflow_tracer import trace
import time

@trace
def slow_function():
    time.sleep(0.1)
    return "slow"

@trace
def fast_function():
    time.sleep(0.01)
    return "fast"

@trace
def process_data():
    result1 = fast_function()
    result2 = slow_function()
    return f"{result1} and {result2}"

@trace
def main():
    result = process_data()
    print(result)

if __name__ == "__main__":
    main()