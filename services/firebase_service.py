import firebase_admin
from firebase_admin import credentials, firestore

db = None

def init_firebase():
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    global db
    db = firestore.client()




