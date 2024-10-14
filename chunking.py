import os
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)

INITIAL_CHUNK_SIZE = 5 * 1024 * 1024 
MAX_CHUNK_SIZE = 10 * 1024 * 1024  
MIN_CHUNK_SIZE = 128 * 1024
PARALLEL_UPLOAD_THREADS = 4

class FileUploader:
    def __init__(self, file_path, server_url):
        self.file_path = file_path
        self.server_url = server_url
        self.chunk_size = INITIAL_CHUNK_SIZE
        self.lock = threading.Lock()

    def finalize_upload(self):
        finalize_url = f'{self.server_url.rsplit("/", 1)[0]}/finalize'
        response = requests.post(finalize_url, headers={
            'Original-Filename': os.path.basename(self.file_path)
        })
        if response.status_code == 200:
            logging.info("File upload completed and assembled successfully!")
        else:
            logging.error(f"Error in finalizing the file upload. Status code: {response.status_code} - {response.text}")

    def get_file_size(self):
        return os.path.getsize(self.file_path)

    def upload_chunk(self, chunk_index, chunk_data):
        if len(chunk_data) == 0:
            logging.warning(f"Chunk {chunk_index} is empty. Skipping upload.")
            return False

        logging.info(f"Uploading chunk {chunk_index} with size: {len(chunk_data)} bytes")
        response = requests.post(self.server_url, data=chunk_data, headers={
            'Content-Type': 'application/octet-stream',
            'Chunk-Index': str(chunk_index),
            'Original-Filename': os.path.basename(self.file_path),
            'Content-Disposition': f'attachment; filename="{os.path.basename(self.file_path)}"'
        })

        logging.info(f"Server response for chunk {chunk_index}: {response.content}")

        if response.status_code == 200:
            return True
        else:
            logging.error(f"Failed to upload chunk {chunk_index}. Status code: {response.status_code} - {response.text}")
            return False

    def adaptive_chunk_size(self, upload_speed):
        with self.lock:
            if upload_speed > 1 * 1024 * 1024:  # More than 1 MB/s
                self.chunk_size = min(self.chunk_size * 1.2, MAX_CHUNK_SIZE)
            else:
                self.chunk_size = max(self.chunk_size * 0.8, MIN_CHUNK_SIZE)
            self.chunk_size = int(self.chunk_size)

    def upload_file_in_chunks(self):
        file_size = self.get_file_size()
        total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size

        with open(self.file_path, 'rb') as file:
            with ThreadPoolExecutor(max_workers=PARALLEL_UPLOAD_THREADS) as executor:
                futures = []
                for chunk_index in range(total_chunks):
                    file.seek(int(chunk_index * self.chunk_size))

                    if chunk_index == total_chunks - 1:
                        chunk_data = file.read(file_size % self.chunk_size or self.chunk_size)
                    else:
                        chunk_data = file.read(self.chunk_size)

                    if chunk_data:
                        futures.append(executor.submit(self.upload_chunk_parallel, chunk_index, chunk_data))
                    else:
                        logging.info(f"Chunk {chunk_index} is empty. Skipping upload.")

                for future in futures:
                    future.result()

    def upload_chunk_parallel(self, chunk_index, chunk_data, retry_count=0):
        MAX_RETRIES = 3
        start_time = time.time()
        success = self.upload_chunk(chunk_index, chunk_data)

        upload_duration = time.time() - start_time

        if success:
            logging.info(f"Chunk {chunk_index} uploaded successfully.")
            upload_speed = len(chunk_data) / upload_duration
            self.adaptive_chunk_size(upload_speed)
        else:
            if retry_count < MAX_RETRIES:
                logging.warning(f"Chunk {chunk_index} failed to upload. Retrying...")
                self.upload_chunk_parallel(chunk_index, chunk_data, retry_count + 1)
            else:
                logging.error(f"Chunk {chunk_index} failed after {MAX_RETRIES} attempts.")

if __name__ == "__main__":
    # The script is now ready to receive the file_path from the frontend.
    # You can set up your backend to receive this file path via an HTTP request.
    # For example, you can pass the file path as a parameter from the frontend
    # and then use the FileUploader class to handle the file upload.
    pass
