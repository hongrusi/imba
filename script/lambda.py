import boto3
import os
import json
from datetime import datetime

def handler(event, context):
    s3 = boto3.client('s3')
    print("Received event data format: " + json.dumps(event))

    for record in event['Records']:  
        source_bucket = record['s3']['bucket']['name']
        source_file = record['s3']['object']['key']
        destination_bucket = os.environ['DESTINATION_BUCKET']

        # Get current timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')

        # Add timestamp to the destination file name
        file_name = source_file.split('/')[-1]
        destination_file = f"data/{file_name}_{timestamp}"
        
        # Copy the file to the destination bucket with the new file name
        s3.copy_object(
            Bucket=destination_bucket,
            CopySource={'Bucket': source_bucket, 'Key': source_file},
            Key=destination_file
        )
