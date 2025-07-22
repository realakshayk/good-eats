import time
import os
LOG_PATH = os.path.join(os.path.dirname(__file__), '../logs/app.log')
with open(LOG_PATH, 'r') as f:
    f.seek(0, os.SEEK_END)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.5)
            continue
        print(line, end='') 