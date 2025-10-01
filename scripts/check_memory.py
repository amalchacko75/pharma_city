import psutil


def get_memory_usage():
    mem = psutil.virtual_memory()
    print("="*40)
    print("📊 Memory Usage Report")
    print("="*40)
    print(f"Total     : {mem.total / (1024 ** 3):.2f} GB")
    print(f"Available : {mem.available / (1024 ** 3):.2f} GB")
    print(f"Used      : {mem.used / (1024 ** 3):.2f} GB")
    print(f"Percent   : {mem.percent}%")
    print("="*40)


if __name__ == "__main__":
    get_memory_usage()
