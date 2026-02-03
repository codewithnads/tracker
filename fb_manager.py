import os
import json
from csv import excel

from pyairtable import Api

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Robust Firebase credentials loader
firebase_cred_json = os.getenv("FIREBASE_CREDENTIALS")
cred = None
print(f"FIREBASE_CREDENTIALS: {firebase_cred_json}")
def _load_cred_from_env(value):
    v = value.strip()
    # If it looks like JSON, try to parse
    if v.startswith("{"):
        try:
            data = json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("FIREBASE_CREDENTIALS is set but not valid JSON")
        if "private_key" in data:
            data["private_key"] = data["private_key"].replace("\\n", "\n")
        return credentials.Certificate(data)
    # If it looks like a path, try to load file from that path
    if os.path.exists(v):
        return credentials.Certificate(v)
    # Not JSON and not a valid path
    raise ValueError("FIREBASE_CREDENTIALS must be JSON content or a valid filesystem path")

# If running on Vercel and env var missing, fail fast with guidance
if not firebase_cred_json and os.path.dirname(__file__).startswith("/var/task"):
    raise ValueError(
        "FIREBASE_CREDENTIALS environment variable is not set in Vercel. "
        "Set FIREBASE_CREDENTIALS to the minified JSON (escape newlines as \\n) in Vercel Project → Environment Variables."
    )

if firebase_cred_json:
    cred = _load_cred_from_env(firebase_cred_json)
else:
    # Local development fallback: try app_data/Cert.json in repo
    cert_path = os.path.join(os.path.dirname(__file__), "app_data", "Cert.json")
    if os.path.exists(cert_path):
        cred = credentials.Certificate(cert_path)
    else:
        default_path = os.path.join(os.getcwd(), "app_data", "Cert.json")
        if os.path.exists(default_path):
            cred = credentials.Certificate(default_path)
        else:
            raise ValueError(
                "Firebase credentials not found. Set FIREBASE_CREDENTIALS env var (minified JSON) "
                "or place app_data/Cert.json in the project root."
            )

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


def update_records(user, records):
    success = True
    db = firestore.client()
    batch = db.batch()
    for key in records:
        bank, acc, k = key.split('~')
        db_ref = db.collection(user).document(bank).collection(acc).document(k)
        batch.set(db_ref,records[key],merge=True)
    try:
        batch.commit()
        success = True
    except Exception as e:
        success = False
        print(f"\n\nError : {e}")

    return success


def import_all_from_xml(records,stash):
    success = True

    db = firestore.client()
    record_batch = db.batch()
    stash_batch = db.batch()
    for item in records:
        path = item[0]
        json = item[1]
        record_ref = db.document(path)
        record_batch.set(record_ref,json)

    for item in stash:
        path = item[0]
        json = item[1]
        stash_ref = db.document(path)
        stash_batch.set(stash_ref,json)

    try:
        record_batch.commit()
        rec_success = True
    except Exception as e:
        rec_success = False
        print(f"\n\nRec Error : {e}")

    try:
        stash_batch.commit()
        sts_success = True
    except Exception as e:
        sts_success = False
        print(f"\n\nsts Error : {e}")

    return sts_success and rec_success

def get_all_records(user='Nadeem'):
    json = {}

    for bank in db.collection(user).list_documents():
        bank_name = bank.get().id
        for acc in bank.collections():
            id = acc.id
            for transaction in acc.stream():
                if transaction.exists:
                    # print(f"\n\nDocument data: {transaction.to_dict()},{transaction}")
                    if bank_name not in json:
                        json[bank_name] = {}
                        json[bank_name][id] = {}
                    if id not in json[bank_name]:
                        json[bank_name][id] = {}
                    json[bank_name][id][transaction.id] = transaction.to_dict()
                else:
                    print("No such document!")
    return json


def add_to_stash(path,data):

    db.document(path).set(data)

    return True

def add_record(path, data):

    db.document(path).set(data)

    return True


if __name__ == '__main__':
    ## Show getting certain records
    print("Started")