import os
from google.oauth2 import service_account

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GS_BUCKET_NAME = 'muconfi-bucket'
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "media"
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "static"
        },
    },
}

# No fine-grained control -> uniform access buckets require following settings:
GS_DEFAULT_ACL = None
GS_QUERYSTRING_AUTH = False

# Add an unique ID to a file name if same file name exists
GS_FILE_OVERWRITE = False

if not os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Not needed if deployed on CR
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR, 'gcpCredentials.json'),
    )