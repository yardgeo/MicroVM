import os
import time

from config import Config


def check_files_existence(file1, file2):
    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < Config.TIME_LIMIT:
        if os.path.isfile(file1) and os.path.isfile(file2):
            print("Both files exist.")
            break

        time.sleep(Config.TIME_SLEEP)
        elapsed_time = time.time() - start_time

    if elapsed_time >= Config.TIME_LIMIT:
        print("Time limit exceeded.")
        return False
    else:
        print("Loop stopped.")
        return True
