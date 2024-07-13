import boto3
import os
import json
def handler(event, context):
    s3 = boto3.client('s3')
    print("Received event data format: " + json.dumps(event))

# When iterating, each record is a single dictionary repreesenting an s3 event
    for record in event['Records']:  
        source_bucket = record['s3']['bucket']['name']
        source_file = record['s3']['object']['key']
        destination_bucket = os.environ['DESTINATION_BUCKET']
        destination_file = 'data/' + source_file.split('/')[-1]
        s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': source_bucket, 'Key': source_file}, Key=destination_file)