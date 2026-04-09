import json
import boto3
import urllib.request
from datetime import datetime

def lambda_handler(event, context):

    # Step 1: Get ISS location from free API
    url = "https://api.open-notify.org/iss-now.json"
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())
    print("ISS location:", data)

    # Step 2: Assume role in Account B using STS
    # This generates temporary credentials valid for 1 hour
    # No permanent access keys stored anywhere
    sts = boto3.client("sts")
    creds = sts.assume_role(
        RoleArn="arn:aws:iam::ACCOUNT_B_ID:role/ISS-CrossAccount-Role",
        RoleSessionName="ISSTrackerSession"
    )["Credentials"]

    # Step 3: Write to Account B S3 using temporary credentials
    s3 = boto3.client("s3",
        region_name="eu-west-1",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"]
    )

    filename = f"iss-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"

    s3.put_object(
        Bucket="YOUR_BUCKET_NAME",
        Key=filename,
        Body=json.dumps(data)
    )

    print(f"Saved to Account B S3: {filename}")

    return {
        "status": "saved",
        "file": filename,
        "location": data
    }
