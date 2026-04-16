import threading
import sys
import os

# Adjust path to import singletons
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))

from fantasy_team_usecase_1.singletons import DatabaseManager

def worker(results_list, index):
    # Attempt to get the instance
    db_manager = DatabaseManager()
    results_list[index] = id(db_manager)

def test_singleton_thread_safety():
    num_threads = 50
    threads = []
    results = [None] * num_threads

    # Create threads
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(results, i))
        threads.append(t)

    # Start threads concurrently
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Check if all instances are the same (have the same id)
    unique_ids = set(results)
    
    print(f"Total threads run: {num_threads}")
    print(f"Unique instance IDs generated: {len(unique_ids)}")
    
    if len(unique_ids) == 1:
        print("SUCCESS: Singleton is thread-safe. All threads received the identical instance.")
    else:
        print("FAILED: Singleton is NOT thread-safe. Multiple instances were created.")

if __name__ == "__main__":
    test_singleton_thread_safety()
