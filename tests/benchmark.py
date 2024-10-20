# -*- coding: utf-8 -*-
import time
import psutil
import random
import platform
import iscc_core as ic
from iscc_core.code_content_text import gen_text_code

try:
    import cpuinfo
except ImportError:
    print("cpuinfo module not found. Install it using: pip install py-cpuinfo")
    cpuinfo = None


def generate_text(length, seed=42):
    """
    Generates deterministic random Unicode text with a given length and seed.

    Parameters:
        length (int): The number of characters to generate.
        seed (int): The seed for the random generator to make the function deterministic.

    Returns:
        str: A deterministic random Unicode string of the specified length.
    """
    # UTF-8 encodable Unicode character ranges
    ranges = [
        (0x0020, 0x007E),  # Basic Latin (includes common characters, numbers, punctuation)
        (0x00A1, 0x00FF),  # Latin-1 Supplement
        (0x0400, 0x04FF),  # Cyrillic
        (0x0370, 0x03FF),  # Greek
        (0x0530, 0x058F),  # Armenian
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs (common in Chinese, Japanese, Korean)
        (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs (includes emojis)
    ]

    random.seed(seed)

    def get_random_char():
        # Choose a random range and then pick a random character within that range
        char_range = random.choice(ranges)
        return chr(random.randint(*char_range))

    return "".join(get_random_char() for _ in range(length))


def benchmark_gen_text_code(text_length, iterations=100):
    text = generate_text(text_length)
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # in MB

    start_time = time.time()
    for _ in range(iterations):
        gen_text_code(text)
    end_time = time.time()
    max_memory = psutil.Process().memory_info().rss / 1024 / 1024  # in MB

    total_time = end_time - start_time
    pages_per_second = (iterations * text_length / 3000) / total_time
    memory_increase = max_memory - memory_usage

    return pages_per_second, memory_increase


def main():
    text_length = 3000 * 100  # 100 pages
    iterations = 3

    print("System Information:")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Processor: {platform.processor()}")
    print(
        f"CPU cores: {psutil.cpu_count(logical=False)} (Physical),"
        f" {psutil.cpu_count(logical=True)} (Logical)"
    )
    print(f"CPU speed: {psutil.cpu_freq().current / 1000:.2f} GHz")
    print(f"Total memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")

    if cpuinfo:
        cpu_info = cpuinfo.get_cpu_info()
        print("\nCPU Features:")
        print(f"Brand: {cpu_info['brand_raw']}")
        print(f"Architecture: {cpu_info['arch']}")
        print(f"Bits: {cpu_info['bits']}")

        # SIMD and other relevant features
        relevant_flags = [
            "sse",
            "sse2",
            "sse3",
            "ssse3",
            "sse4_1",
            "sse4_2",
            "avx",
            "avx2",
            "fma3",
            "mmx",
            "neon",
        ]
        supported_flags = [flag for flag in relevant_flags if flag in cpu_info["flags"]]
        print(f"Instructions: {', '.join(supported_flags)}")

    pages_per_second, memory_increase = benchmark_gen_text_code(text_length, iterations)

    print("\nBenchmark results for gen_text_code:")
    print(f"Pages per second: {pages_per_second:.2f}")
    print(f"Max memory increase: {memory_increase:.2f} MB")
    print(f"Cython extension modules used: {ic.turbo()}")


if __name__ == "__main__":
    main()
