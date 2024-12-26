import functions_framework
from google.cloud import storage
from google.cloud import pubsub_v1
import os
import json

@functions_framework.http
def handle_upload(request):
    """HTTP Cloud Function that triggers FHE encryption process."""
    if request.method != 'POST':
        return ('Please use POST method', 405)

    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or 'bucket' not in request_json or 'file' not in request_json:
            return ('Invalid request data', 400)

        bucket_name = request_json['bucket']
        file_name = request_json['file']

        # Publish message to start encryption
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.getenv('PROJECT_ID'), 'fhe-encryption-tasks')
        
        message_data = {
            'bucket': bucket_name,
            'file': file_name
        }
        
        # Publish the message
        future = publisher.publish(
            topic_path, 
            data=json.dumps(message_data).encode('utf-8')
        )
        
        return {
            'status': 'success',
            'message': f'Encryption process started for {file_name}',
            'message_id': future.result()
        }

    except Exception as e:
        return (f'Error: {str(e)}', 500)
