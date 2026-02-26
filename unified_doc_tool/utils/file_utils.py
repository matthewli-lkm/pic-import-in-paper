import os
import time
import threading

def cleanup_old_files(folders, max_age_hours=24):
    """
    Deletes files in the specified folders that are older than max_age_hours.
    """
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    
    deleted_count = 0
    
    for folder in folders:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            # Skip directories (unless we want to recursively clean, but top-level seems safer for now)
            if not os.path.isfile(file_path):
                continue
            
            try:
                # Check modification time
                if os.path.getmtime(file_path) < cutoff:
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                print(f"Error checking/deleting {file_path}: {e}")
                
    if deleted_count > 0:
        print(f"Auto-cleanup: Removed {deleted_count} old temporary files.")

def start_periodic_cleanup(app_root, interval_hours=1, max_age_hours=24):
    """
    Starts a background thread to run cleanup periodically.
    """
    # Define paths relative to app root
    folders_to_clean = [
        os.path.join(app_root, 'uploads'),
        os.path.join(app_root, 'processed')
    ]

    def run_cleanup():
        while True:
            try:
                cleanup_old_files(folders_to_clean, max_age_hours=max_age_hours)
            except Exception as e:
                print(f"Cleanup task failed: {e}")
            
            # Sleep for the interval
            time.sleep(interval_hours * 3600)

    # Start daemon thread
    thread = threading.Thread(target=run_cleanup, daemon=True)
    thread.start()
