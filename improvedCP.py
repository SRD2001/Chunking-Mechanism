import os
import aiohttp
import asyncio
import hashlib
import logging
import time

logging.basicConfig(level=logging.INFO)

CHUNK_SIZES = {
    'small': 128 * 1024,       
    'medium': 1 * 1024 * 1024,
    'large': 5 * 1024 * 1024, 
    'xl': 10 * 1024 * 1024,
    'xxl': 20 * 1024 * 1024, 
    'giant': 50 * 1024 * 1024 
}
MIN_CHUNK_SIZE = CHUNK_SIZES['small']
MAX_RETRIES = 3

class AsyncFileUploader:
    def __init__(self, file_path, server_url):
        self.file_path = file_path
        self.server_url = server_url
        self.chunk_size = self.set_initial_chunk_size()
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

    def get_file_size(self):
        return os.path.getsize(self.file_path)

    async def finalize_upload(self):
        finalize_url = f'{self.server_url.rsplit("/", 1)[0]}/finalize'
        async with aiohttp.ClientSession() as session:
            async with session.post(finalize_url, headers={
                'Original-Filename': os.path.basename(self.file_path)
            }) as response:
                if response.status == 200:
                    logging.info("File upload completed and assembled successfully!")
                else:
                    logging.error(f"Error in finalizing the file upload. Status: {response.status}, Text: {await response.text()}")

    async def upload_chunk(self, chunk_index, chunk_data, chunk_md5):
        headers = {
            'Content-Type': 'application/octet-stream',
            'Chunk-Index': str(chunk_index),
            'Original-Filename': os.path.basename(self.file_path),
            'Content-Disposition': f'attachment; filename="{os.path.basename(self.file_path)}"',
            'Content-MD5': chunk_md5
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url, data=chunk_data, headers=headers) as response:
                if response.status == 200:
                    logging.info(f"Chunk {chunk_index} uploaded successfully.")
                    return True
                else:
                    logging.error(f"Failed to upload chunk {chunk_index}. Status: {response.status}, Text: {await response.text()}")
                    return False

    async def upload_chunk_with_retries(self, chunk_index, chunk_data, retry_count=0):
        chunk_md5 = self.calculate_md5(chunk_data)
        start_time = time.time()

        success = await self.upload_chunk(chunk_index, chunk_data, chunk_md5)

        upload_duration = time.time() - start_time
        if success:
            upload_speed = len(chunk_data) / upload_duration
            self.adjust_chunk_size_based_on_speed(upload_speed)
        else:
            if retry_count < MAX_RETRIES:
                delay = 2 ** retry_count  
                logging.warning(f"Retrying chunk {chunk_index} after {delay} seconds...")
                await asyncio.sleep(delay)
                return await self.upload_chunk_with_retries(chunk_index, chunk_data, retry_count + 1)
            else:
                logging.error(f"Chunk {chunk_index} failed after {MAX_RETRIES} attempts.")
                return False

    def adjust_chunk_size_based_on_speed(self, upload_speed):
        if upload_speed > 1 * 1024 * 1024: 
            self.chunk_size = min(self.chunk_size * 1.2, CHUNK_SIZES['giant'])
        else:
            self.chunk_size = max(self.chunk_size * 0.8, MIN_CHUNK_SIZE)
        self.chunk_size = int(self.chunk_size)
        logging.info(f"Adjusted chunk size to: {self.chunk_size} bytes")

    def calculate_md5(self, chunk_data):
        """Calculate MD5 checksum for the chunk"""
        md5_hash = hashlib.md5()
        md5_hash.update(chunk_data)
        return md5_hash.hexdigest()

    async def upload_file_in_chunks(self):
        total_chunks = (self.file_size + self.chunk_size - 1) // self.chunk_size

        async with aiohttp.ClientSession() as session:
            tasks = []
            with open(self.file_path, 'rb') as file:
                for chunk_index in range(total_chunks):
                    file.seek(int(chunk_index * self.chunk_size))

                    if chunk_index == total_chunks - 1:
                        chunk_data = file.read(self.file_size % self.chunk_size or self.chunk_size)
                    else:
                        chunk_data = file.read(self.chunk_size)

                    if chunk_data:
                        task = asyncio.ensure_future(self.upload_chunk_with_retries(chunk_index, chunk_data))
                        tasks.append(task)
                    else:
                        logging.info(f"Chunk {chunk_index} is empty. Skipping upload.")

            await asyncio.gather(*tasks)

if __name__ == "__main__":
    file_path = "C:\\Users\\sharad.pandey\\Pictures\\Camera Roll\\WIN_20241010_17_35_06_Pro.mp4"
    server_url = "http://127.0.0.1:5000/upload"

    uploader = AsyncFileUploader(file_path, server_url)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(uploader.upload_file_in_chunks())
    loop.run_until_complete(uploader.finalize_upload())
