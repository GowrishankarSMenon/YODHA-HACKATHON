from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

print("=== SERVER INFO ===")
print("Client address:", client.address)

print("\n=== DATABASES VISIBLE TO PYTHON ===")
print(client.list_database_names())

db = client["medscan_emr"]

print("\n=== COLLECTIONS IN medscan_emr ===")
print(db.list_collection_names())

patients = db["patients"]

print("\n=== ALL DOCUMENTS IN patients ===")
docs = list(patients.find())
print(docs)
