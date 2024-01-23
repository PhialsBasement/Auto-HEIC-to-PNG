import os
import time
import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from PIL import Image
import pillow_heif

# Set the downloads folder based on the operating system
if platform.system() == "Windows":
    DOWNLOADS_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
elif platform.system() == "Linux":
    DOWNLOADS_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
else:
    raise Exception("Unsupported operating system")

API_ENDPOINT = "http://127.0.0.1:5000/convert"

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        file_name, file_extension = os.path.splitext(file_path)

        if file_extension.lower() == '.heic':
            # Retry up to 5 times with a 1-second delay
            for _ in range(5):
                if os.path.exists(file_path):
                    convert_and_replace(file_path)
                    break
                time.sleep(1)

def convert_and_replace(heic_path):
    with open(heic_path, 'rb') as heic_file:
        files = {'image': ('heic_image.heic', heic_file, 'image/heic')}
        response = requests.post(API_ENDPOINT, files=files)

        if response.status_code == 200:
            png_data = response.json().get('png_data', '')
            if png_data:
                png_path = heic_path.lower().replace('.heic', '.png')
                with open(png_path, 'wb') as png_file:
                    png_file.write(png_data.encode('latin-1'))
                heic_file.close()
                os.remove(heic_path)
                print(f"File converted and replaced: {heic_path} -> {png_path}")
            else:
                print(f"Error converting file: {heic_path}, {response.json()}")
        else:
            print(f"Error communicating with the API: {response.status_code}, {response.text}")

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DOWNLOADS_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
