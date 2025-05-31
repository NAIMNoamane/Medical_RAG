import os 
from google.cloud import storage
import json


key_path = "quantum-monitor-460814-i9-b30dff14ec0c.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path




def uploadParentDoc(parent_id,parent_article, bucket_name="gale-parent-docs"):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{parent_id}.json")

    payload = {
        "parent_id": parent_id,
        "content": parent_article
    }

    blob.upload_from_string(json.dumps(payload), content_type="application/json")
    print(f"Uploaded: {parent_id}")



def getParentDocFromGCS(parent_id, bucket_name="gale-parent-docs"):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{parent_id}.json")

    if blob.exists():
        data = blob.download_as_text()
        return json.loads(data)
    else:
        raise FileNotFoundError(f"Parent doc {parent_id} not found.")

