import os
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)

CHUNK_SIZES = {
    'small': 128 * 1024,       
    'medium': 1 * 1024 * 1024, 
    'large': 5 * 1024 * 1024,  
    'xl': 10 * 1024 * 1024,    
    'xxl': 20 * 1024 * 1024,   
    'giant': 50 * 1024 * 1024 
}
MAX_PARALLEL_THREADS = 10
MIN_CHUNK_SIZE = CHUNK_SIZES['small']
MAX_RETRIES = 3

class FileUploader:
    def __init__(self, file_path, server_url):
        self.file_path = file_path
        self.server_url = server_url
        self.chunk_size = self.set_initial_chunk_size()
        self.lock = threading.Lock()
        self.file_size = self.get_file_size()

    def set_initial_chunk_size(self):
        """Set initial chunk size based on file size"""
        file_size = self.get_file_size()
        if file_size < 1 * 1024 * 1024:  
            return CHUNK_SIZES['small']
        elif file_size < 10 * 1024 * 1024:  
            return CHUNK_SIZES['medium']
        elif file_size < 50 * 1024 * 1024: 
            return CHUNK_SIZES['large']
        elif file_size < 100 * 1024 * 1024:
            return CHUNK_SIZES['xl']
        elif file_size < 200 * 1024 * 1024:
            return CHUNK_SIZES['xxl']
        else:  
            return CHUNK_SIZES['giant']

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

        try:
            logging.info(f"Uploading chunk {chunk_index} with size: {len(chunk_data)} bytes")
            response = requests.post(self.server_url, data=chunk_data, headers={
                'Content-Type': 'application/octet-stream',
                'Chunk-Index': str(chunk_index),
                'Original-Filename': os.path.basename(self.file_path),
                'Content-Disposition': f'attachment; filename="{os.path.basename(self.file_path)}"'
            })
            
            if response.status_code == 200:
                return True
            else:
                logging.error(f"Failed to upload chunk {chunk_index}. Status code: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logging.error(f"Exception during chunk upload {chunk_index}: {e}")
            return False

    def adaptive_chunk_size(self, upload_speed):
        with self.lock:
            if upload_speed > 1 * 1024 * 1024:
                self.chunk_size = min(self.chunk_size * 1.2, CHUNK_SIZES['giant'])
            else:
                self.chunk_size = max(self.chunk_size * 0.8, MIN_CHUNK_SIZE)
            self.chunk_size = int(self.chunk_size)

    def upload_file_in_chunks(self):
        total_chunks = (self.file_size + self.chunk_size - 1) // self.chunk_size

        with open(self.file_path, 'rb') as file:
            with ThreadPoolExecutor(max_workers=MAX_PARALLEL_THREADS) as executor:
                futures = []
                for chunk_index in range(total_chunks):
                    file.seek(int(chunk_index * self.chunk_size))

                    if chunk_index == total_chunks - 1:
                        chunk_data = file.read(self.file_size % self.chunk_size or self.chunk_size)
                    else:
                        chunk_data = file.read(self.chunk_size)

                    if chunk_data:
                        futures.append(executor.submit(self.upload_chunk_parallel, chunk_index, chunk_data))
                    else:
                        logging.info(f"Chunk {chunk_index} is empty. Skipping upload.")

                for future in futures:
                    future.result()

    def upload_chunk_parallel(self, chunk_index, chunk_data, retry_count=0):
        start_time = time.time()
        success = self.upload_chunk(chunk_index, chunk_data)

        upload_duration = time.time() - start_time

        if success:
            logging.info(f"Chunk {chunk_index} uploaded successfully.")
            upload_speed = len(chunk_data) / upload_duration
            self.adaptive_chunk_size(upload_speed)
        else:
            if retry_count < MAX_RETRIES:
                delay = 2 ** retry_count
                logging.warning(f"Retrying chunk {chunk_index} after {delay} seconds...")
                time.sleep(delay)
                self.upload_chunk_parallel(chunk_index, chunk_data, retry_count + 1)
            else:
                logging.error(f"Chunk {chunk_index} failed after {MAX_RETRIES} attempts.")

if __name__ == "__main__":
    file_path = "C:\\Users\\sharad.pandey\\Downloads\\15_Apr_2024_CIPL_Presentation_UPSC.pptx"
    server_url = "http://127.0.0.1:5000/upload"

    uploader = FileUploader(file_path, server_url)
    uploader.upload_file_in_chunks()
    uploader.finalize_upload()