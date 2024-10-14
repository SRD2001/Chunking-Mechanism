import hashlib
import time
import requests
import os
class FileUploader:
    def __init__(self, file_path, upload_url, max_retries=3, initial_chunk_size=1024 * 1024):
        self.file_path = file_path
        self.upload_url = upload_url
        self.max_retries = max_retries
        self.chunk_size = initial_chunk_size

    def calculate_md5(self, chunk_data):
        """Calculates the MD5 checksum for a given chunk of data."""
        md5_hash = hashlib.md5()
        md5_hash.update(chunk_data)
        return md5_hash.hexdigest()

    def set_chunk_size(self, file_size):
        """Dynamically adjusts the chunk size based on file size."""
        if file_size < 10 * 1024 * 1024:  
            self.chunk_size = 512 * 1024  
        elif file_size > 100 * 1024 * 1024: 
            self.chunk_size = 5 * 1024 * 1024 

    def upload_chunk_with_retries(self, chunk_data, chunk_number, retries=0):
        """Uploads a chunk of data, retrying if it fails."""
        md5_checksum = self.calculate_md5(chunk_data)
        headers = {'Content-MD5': md5_checksum}

        try:
            response = requests.post(self.upload_url, headers=headers, data=chunk_data)
            response.raise_for_status()
        except requests.RequestException as e:
            if retries < self.max_retries:
                retries += 1
                print(f"Retry {retries}/{self.max_retries} for chunk {chunk_number}")
                time.sleep(2 ** retries)  
                return self.upload_chunk_with_retries(chunk_data, chunk_number, retries)
            else:
                print(f"Failed to upload chunk {chunk_number} after {retries} retries. Error: {e}")
                return False

        return True

    def show_progress(self, uploaded_bytes, total_bytes):
        """Shows the progress of the upload."""
        progress_percentage = (uploaded_bytes / total_bytes) * 100
        print(f"Upload Progress: {progress_percentage:.2f}%")

    def upload_file(self):
        """Handles the entire file upload process."""
        try:
            file_size = self.get_file_size(self.file_path)
            self.set_chunk_size(file_size)

            uploaded_bytes = 0
            chunk_number = 0

            with open(self.file_path, 'rb') as f:
                while True:
                    chunk_data = f.read(self.chunk_size)
                    if not chunk_data:
                        break

                    chunk_number += 1
                    success = self.upload_chunk_with_retries(chunk_data, chunk_number)
                    if not success:
                        print(f"Upload failed for chunk {chunk_number}. Aborting.")
                        return False

                    uploaded_bytes += len(chunk_data)
                    self.show_progress(uploaded_bytes, file_size)

            print("Upload completed successfully!")
            return True

        except FileNotFoundError:
            print("File not found. Please check the file path.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_file_size(self, file_path):
        """Returns the size of the file."""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            print(f"Error getting file size: {e}")
            return 0


file_path = "C:\\Users\\sharad.pandey\\Pictures\\Camera Roll\\WIN_20241010_17_35_06_Pro.mp4"
server_url = "http://127.0.0.1:5000/upload"
uploader = FileUploader(file_path, server_url)
uploader.upload_file()