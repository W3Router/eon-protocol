import os
import json
import base64
from flask import Flask, request
from google.cloud import storage
import logging
from eon.cli import main as eon_main

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

@app.route('/', methods=['POST'])
def handle_pubsub_message():
    try:
        envelope = request.get_json()
        if not envelope:
            raise ValueError("No Pub/Sub message received")

        if not isinstance(envelope, dict) or 'message' not in envelope:
            raise ValueError("Invalid Pub/Sub message format")

        # Extract message data
        pubsub_message = envelope['message']
        if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
            data = base64.b64decode(pubsub_message['data']).decode('utf-8')
            message_data = json.loads(data)
            
            bucket_name = message_data['bucket']
            file_name = message_data['file']
            
            # Create temporary directories for processing
            os.makedirs('/tmp/input', exist_ok=True)
            os.makedirs('/tmp/output', exist_ok=True)
            
            input_file = f'/tmp/input/{file_name}'
            encrypted_file = f'/tmp/output/encrypted_{file_name}'
            
            # Download file from GCS
            logger.info(f"Downloading file {file_name} from bucket {bucket_name}")
            download_from_gcs(bucket_name, file_name, input_file)
            
            # Perform FHE encryption using eon-protocol
            logger.info("Starting FHE encryption")
            try:
                # Initialize EON protocol with the input file
                eon_main(['encrypt', 
                         '--input', input_file,
                         '--output', encrypted_file])
                
                # Upload encrypted file back to GCS
                logger.info("Uploading encrypted file to GCS")
                upload_to_gcs(bucket_name, 
                            encrypted_file, 
                            f'encrypted/{file_name}')
                
                # Clean up temporary files
                os.remove(input_file)
                os.remove(encrypted_file)
                
                return ('', 204)
                
            except Exception as e:
                logger.error(f"Encryption failed: {str(e)}")
                raise
                
        return ('', 204)
        
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080
    app.run(host='0.0.0.0', port=PORT)
