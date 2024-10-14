from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_chunks'
ASSEMBLED_FOLDER = 'assembled_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ASSEMBLED_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@app.route('/upload', methods=['POST'])
def upload_chunk():
    chunk_index = request.headers.get('Chunk-Index')
    original_filename = request.headers.get('Original-Filename')
    chunk_data = request.data

    logging.info(f"Received Chunk-Index: {chunk_index}, Original-Filename: {original_filename}")

    if chunk_index is None:
        return jsonify({'error': 'Chunk index not provided!'}), 400

    if original_filename is None:
        return jsonify({'error': 'Original filename not provided!'}), 400

    chunk_file_path = os.path.join(UPLOAD_FOLDER, f'{original_filename}_chunk_{chunk_index}.part')

    try:
        with open(chunk_file_path, 'wb') as f:
            f.write(chunk_data)
        return jsonify({'message': f'Chunk {chunk_index} uploaded successfully'}), 200
    except Exception as e:
        logging.error(f"Error saving chunk {chunk_index}: {e}")
        return jsonify({'error': 'Failed to save chunk!'}), 500

@app.route('/finalize', methods=['POST'])
def finalize_upload():
    original_filename = request.headers.get('Original-Filename')

    if original_filename is None:
        return jsonify({'error': 'Original filename not provided!'}), 400

    final_file_path = os.path.join(ASSEMBLED_FOLDER, original_filename)

    chunk_files = sorted(
        [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(original_filename)],
        key=lambda x: int(x.split('_chunk_')[1].split('.')[0])
    )
    
    total_chunks = len(chunk_files)

    if total_chunks == 0:
        return jsonify({'error': 'No chunks found!'}), 400

    total_written = 0
    try:
        with open(final_file_path, 'wb') as final_file:
            for chunk_file in chunk_files:
                chunk_path = os.path.join(UPLOAD_FOLDER, chunk_file)
                with open(chunk_path, 'rb') as chunk:
                    chunk_data = chunk.read()
                    final_file.write(chunk_data)
                    total_written += len(chunk_data)

        expected_total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) for f in chunk_files)

        if total_written == expected_total_size:
            # for chunk_file in chunk_files:
            #     os.remove(os.path.join(UPLOAD_FOLDER, chunk_file))
            return jsonify({'message': f'File {original_filename} assembled successfully with {total_chunks} chunks!'}), 200
        else:
            return jsonify({'error': 'Warning: Final file size does not match the total size of chunks!'}), 500
    except Exception as e:
        logging.error(f"Error finalizing upload: {e}")
        return jsonify({'error': 'Failed to assemble the final file!'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
