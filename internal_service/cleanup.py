import shutil
import os
import time

def cleanup():
    print("Running cleanup...")
    # Simulated cleanup task
    tmp_dir = "/tmp/nexus_cache"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
        print("Cache cleared.")
    else:
        print("No cache found.")

if __name__ == "__main__":
    cleanup()
