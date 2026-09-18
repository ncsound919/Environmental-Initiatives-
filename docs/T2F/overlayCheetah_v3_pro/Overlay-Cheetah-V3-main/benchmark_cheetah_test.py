import time
import random
import statistics

# Simulated Cheetah benchmark test


def benchmark_cheetah(iterations=1000):
    results = []
    for i in range(iterations):
        # Simulate a core operation (e.g., MIDI generation, template rendering)
        start = time.perf_counter()
        # Simulate workload: random MIDI generation
        midi_data = [random.randint(0, 127) for _ in range(1000)]
        # Simulate processing (e.g., arrangement, export)
        midi_data.sort()
        end = time.perf_counter()
        results.append(end - start)
    avg_time = statistics.mean(results)
    min_time = min(results)
    max_time = max(results)
    stdev_time = statistics.stdev(results)
    print(f"Cheetah Benchmark Results:")
    print(f"Iterations: {iterations}")
    print(f"Average Time per Operation: {avg_time*1000:.3f} ms")
    print(f"Min Time: {min_time*1000:.3f} ms")
    print(f"Max Time: {max_time*1000:.3f} ms")
    print(f"Std Dev: {stdev_time*1000:.3f} ms")
    return {
        "iterations": iterations,
        "average_ms": avg_time * 1000,
        "min_ms": min_time * 1000,
        "max_ms": max_time * 1000,
        "stdev_ms": stdev_time * 1000,
    }


if __name__ == "__main__":
    benchmark_cheetah()
