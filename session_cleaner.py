import os
import time

SESSION_FOLDER = './flask_session'
MAX_AGE_SECONDS = 60 * 60

while True:
    now = time.time()
    for filename in os.listdir(SESSION_FOLDER):
        file_path = os.path.join(SESSION_FOLDER, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > MAX_AGE_SECONDS:
                os.remove(file_path)
                print(f"Usunięto plik sesji: {file_path}")
    time.sleep(30)