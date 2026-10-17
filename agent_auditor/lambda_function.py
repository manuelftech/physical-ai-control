from services.audit_image import audit_image
import urllib.parse

def lambda_handler(event, context):
        """
        Processes Images to verify and audit if the objects were properly detected
        """
        # Extract data to obtain the bucket and object keys that triggered this event
        s3_record = event['Records'][0]['s3']
        image_path = urllib.parse.unquote_plus(s3_record['object']['key'])
        bucket_name = s3_record['bucket']['name']
        audit_image(image_path=image_path, bucket_name=bucket_name)