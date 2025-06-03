from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import time

uri = (
    "mongodb://testuser:testpass@mongo1:27017,mongo2:27017,mongo3:27017/"
    "?replicaSet=rs0&authSource=testdb"
)

for i in range(10):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        ismaster = client.admin.command("hello")
        if ismaster.get("isWritablePrimary", False):
            print("PRIMARY détecté")
            break
    except ServerSelectionTimeoutError:
        print("En attente d’un PRIMARY...")
        time.sleep(2)
else:
    print("Aucun PRIMARY détecté après 10 tentatives")
    exit(1)

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    db = client["testdb"]
    collection = db["appCollection"]

    # Insertion
    collection.insert_one({"name": "ReplicaApp", "version": 1})
    print("Document inséré")

    # Requête avec filtre
    result = collection.find_one({"name": "ReplicaApp"})
    print("Résultat :", result)

    # Mise à jour
    collection.update_one({"name": "ReplicaApp"}, {"$set": {"version": 2}})
    print("Document mis à jour")

    # Suppression
    collection.delete_one({"name": "ReplicaApp"})
    print("Document supprimé")

except ServerSelectionTimeoutError as e:
    print("Connexion échouée :", e)
finally:
    client.close()
