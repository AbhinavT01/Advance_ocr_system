from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import vision_v1
import google.auth.credentials

# Paste your service account JSON here as a Python dictionary
service_account_info = {
    "type": "service_account",
    "project_id": "aerobic-botany-464022-t6",
    "private_key_id": "6ac5f02a7707e8251b35ffc296fe5c80c97bb406",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8V5kX0oF5bpad\nzgEWCO4KtU0oWbWlXYYnMySml5CCaeZgFSEXefKaOH2cgC8zgLc+VVaeheReTSdS\nuIMkhDV/cWJEAOkLUtNr6cD2QdMFYnY3KOTg2Tbmoc8EEsoX/QqOSPY6sWpZgnC1\nbpCZ3s8aPUhFWq7fGkYNt882vBRL3t1U091pNDV3il8R9/ZVu80d6S/WnYlYng48\nn8HX4kHqM80Tiae61HwyUeXNbLML+AOoyLI+HCefFkuMDM8EBhXVzmvKwyJFJlwP\n+L49FpeeL0JTnkseDrkCB1IhmUhu1JDQHLYyf+lMd17EWlY1oOu2NDLS889PmREX\n1LQcoOJrAgMBAAECggEAPQUge6BfBGm48J2aqnnwLZX5zpXqDQ6U9URTnonCbw5C\nbmTKGOIQoLimsbqyEDymodJiQu/cQlU65UkUbBNNheHFVYT5/Ao0p2TPeLlw1fDF\nni9ooBSf/e70tDwmL8lyzxCCfheW/jMNsyqEPOX8MWMjdBziRTQs+CrSPsiGxuF5\nQ/tX18Y222/jUsFKpOFzH8EIeTc59Bszl8Y6hnt8Kvcy3eBxJiU3veqAvTNkl26R\n7id2+sDAnI1+TUYuIGuo4rbFv7byfYWRYe1wHHltPfhD+qwaSzSisUB3D+6eWOQd\n7ALZY+pbtX0OFeuchuZ1JxW4+VQrJrU/hEsnRtp08QKBgQD69fhjh/Ipd2the5vi\nQgPrX7QjJca7wI0amat8cNoS9mE4FAnUWUw5wmVhFukYmM8/emgpRp/tArUHSVAb\nAA+Bfho9Bp/zB0H9NUh0AVZTMGcGAGjo3sK7wd5EBzmrjsFlHlAQ7rZqk/VKuqNB\n6aVCLcZJ2HUi71pAJ8V8fLmCgwKBgQDAH77FbQGuOkYLjaW3SVuA1z9CRIyj6PPp\nJcJv5+TWXcvtwjMGMWKrBwoobzu2McYXA5hbH+Diz21AtO6yj7oisQxS26nqbbI6\nVBoQHwNwSU31CNRpgG2Rg2YR/hehgs+I6lkdBuEw4m6ftxUIIzIGeLV6W4ywg00s\nSOvcMtR7+QKBgCbswdMGQfxGhoQ/POVyIdN/K5yL/nAepIQss5mAk4J/boLZMNEb\n7KPE0B6oBA2JnhOVc9R7HNERK2zu5Rra/oyyN3Whsmtqg8S3X/6GOpJ6nnAi3iLI\ncmHW5xecG0jNwpdhhT+rFuYe/tvRaQMPL0+9c9T+WuTJRTFQOeReIBPrAoGBALxR\noZ5FJiOQbT4/3tLU7gNReWlMZgr4ebTr1TX5uP5CvHTWKUuFtvBrmxJdTctd6IyA\ncqPHkJjht3Z4o4yVg18j6i+Br4Dhe5TfARkSPT2gLPDlccfkIgJDKRaz2Jfw79qF\n00m3h55yJPsa61upnAxp34ELIdGXMlsZM1AI5uyJAoGAWkJh+iKmBVlOEM+mcYn4\nDFmiG1nvexdbOUYpRvj6ft7ObilBZ7ZIm8dYzWckSdsrj2zbomTMtBuS8IIrRTaQ\nC/i6e9RTz5xAPVsHXrD4AWFKWx14EMqkcmswTEG6DJsRhBVdGhvkhzeBNLLZhrMn\nu7bo0JVeiTy2T9vwej46WoY=\n-----END PRIVATE KEY-----\n",
    "client_email": "advanceocr@aerobic-botany-464022-t6.iam.gserviceaccount.com",
    "client_id": "112282222414363959436",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/advanceocr%40aerobic-botany-464022-t6.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Step 1: Generate credentials and access token
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(Request())
access_token = credentials.token
print("✅ Access Token:", access_token)

# Step 2: Create minimal Credentials class using access token
class SimpleTokenCredentials(google.auth.credentials.Credentials):
    def __init__(self, token):
        super().__init__()
        self._token = token

    @property
    def expired(self):
        return False

    @property
    def valid(self):
        return True

    def refresh(self, request):
        pass

    @property
    def token(self):
        return self._token

# Step 3: Use token to make Vision API call
manual_token_creds = SimpleTokenCredentials(access_token)
client = vision_v1.ImageAnnotatorClient(credentials=manual_token_creds)

def detect_document_text(image_path):
    """Detects full document text using access token."""
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision_v1.Image(content=content)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"❌ Vision API error: {response.error.message}")

    annotations = response.full_text_annotation

    if annotations and annotations.text:
        print("\n📄 Detected Document Text:\n")
        print(annotations.text)
        return annotations.text
    else:
        print("⚠️ No text detected.")
        return ""

# # Example usage
# if __name__ == "__main__":
#     result = detect_document_text("images1.jpg")  # Replace with your image
