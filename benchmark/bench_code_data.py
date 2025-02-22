# -*- coding: utf-8 -*-
import time
import io
import random
import iscc_core as ic


def generate_test_data(size_mb=1024):
    """Generate random test data of specified size in MB (default 1GB)."""
    size_bytes = size_mb * 1024 * 1024
    chunk_size = 64 * 1024 * 1024  # 64MB chunks
    buffer = io.BytesIO()

    remaining = size_bytes
    while remaining > 0:
        chunk = min(remaining, chunk_size)
        buffer.write(random.randbytes(chunk))
        remaining -= chunk

    buffer.seek(0)
    return buffer


def benchmark_gen_data_code():
    """Benchmark data code generation with 1GB of random data."""
    data = generate_test_data()
    file_size = data.getbuffer().nbytes

    start_time = time.time()
    ic.gen_data_code(data)
    end_time = time.time()

    duration = end_time - start_time
    speed = file_size / (1024 * 1024 * duration)  # MB/s

    return {"file_size_mb": file_size / (1024 * 1024), "duration_s": duration, "speed_mbs": speed}


def main():
    results = benchmark_gen_data_code()

    print("\nBenchmark results for gen_data_code:")
    print(f"File size: {results['file_size_mb']:.2f} MB")
    print(f"Duration: {results['duration_s']:.2f} seconds")
    print(f"Speed: {results['speed_mbs']:.2f} MB/s")
    print(f"Cython extension modules used: {ic.turbo()}")


if __name__ == "__main__":
    main()
