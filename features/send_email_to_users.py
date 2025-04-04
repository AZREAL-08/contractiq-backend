import google.generativeai as genai
import json
import os
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional
from email_notification import ContractNotificationManager
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("..\\firebase_credentials.json")  # Replace with your service account key path
firebase_admin.initialize_app(cred)
db = firestore.client()

class LicenseAgreement(BaseModel):
    parties: Dict[str, str]
    licensing_terms: Dict[str, object]
    financial_terms: Dict[str, object]
    usage_restrictions: Dict[str, List[str]]
    intellectual_property: Dict[str, str]
    legal_compliance: Dict[str, str]
    contract_termination: Dict[str, object]

    @classmethod
    def check_parties(cls, v):
        if "licensor" not in v or "licensee" not in v:
            raise ValueError("Both 'licensor' and 'licensee' must be specified.")
        return v

class LicenseAgreementExtractor:
    def __init__(self):
        self.notification_manager = ContractNotificationManager()

    def schedule_notifications(self, data: Dict, email: str, contract_id: str = None):
        success = self.notification_manager.schedule_notifications(data, email, contract_id)
        if success:
            print(f"Notification scheduled successfully for {email}")
        else:
            print("Failed to schedule notification")
        return success

def extract_data_from_firebase(user_id, document_id):
    """
    Extracts contract data and user email from Firestore and schedules notifications.
    """
    try:
        doc_ref = db.collection('users').document(user_id).collection('documents').document(document_id)
        doc = doc_ref.get()
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()

        if doc.exists and user.exists:
            doc_data = doc.to_dict()
            user_data = user.to_dict()
            user_email = user_data.get('email')

            if user_email:
                try:
                    validated_data = LicenseAgreement.model_validate(doc_data).model_dump()
                    file_name = document_id
                    contract_id = f"{file_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    extractor = LicenseAgreementExtractor()
                    extractor.schedule_notifications(validated_data, user_email, contract_id)
                    print(validated_data)
                    return validated_data

                except ValidationError as ve:
                    print("Validation Error:", ve.model_dump_json(indent=2))
                    return None
            else:
                print(f"User email not found for user {user_id}")
                return None

        else:
            if not doc.exists:
                print(f"Document {document_id} not found.")
            if not user.exists:
                print(f"User {user_id} not found.")
            return None

    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        return None

def check_notifications():
    notification_manager = ContractNotificationManager()
    notification_manager.send_scheduled_notifications()

def process_all_users_contracts():
    """Process all contracts for all users."""
    try:
        users_ref = db.collection('users').stream()

        for user in users_ref:
            user_id = user.id
            docs_ref = db.collection('users').document(user_id).collection('documents').stream()

            for doc in docs_ref:
                extract_data_from_firebase(user_id, doc.id)

    except Exception as e:
        print(f"Error processing users and their contracts: {e}")

if __name__ == '__main__':
    process_all_users_contracts()
    # check_notifications()
