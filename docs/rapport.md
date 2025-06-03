# Partie 1 – Déploiement MongoDB en mode Standalone

## Objectif
Déployer MongoDB dans un conteneur Docker en mode standalone avec authentification, puis interagir avec la base via une application Python.

---

## Méthode de déploiement

J'ai utilisé **Docker** avec un fichier `docker-compose.yml` pour déployer une instance MongoDB en standalone.

```bash
cd mongo/standalone/
docker-compose up -d
```

## Création de l'utilisateur
Un script init-mongo.js est monté dans le conteneur au démarrage pour crée la base testdb, crée un utilisateur testuser avec mot de passe testpass et insère quelques documents dans une collection testCollection.
```js
db = db.getSiblingDB('testdb');

db.createUser({
  user: 'testuser',
  pwd: 'testpass',
  roles: [{ role: 'readWrite', db: 'testdb' }]
});

db.testCollection.insertMany([
  { name: "Alice", age: 28 },
  { name: "Bob", age: 34 },
  { name: "Charlie", age: 22 }
]);
```

## Connexion avec authentification sur la base testdb

```bash
 docker exec -it mongodb-standalone mongosh "mongodb://testuser:testpass@localhost:27017/testdb?authSource=testdb"
 ```
Réponse :
```
Current Mongosh Log ID: 683dd148c6b66c4a48d861df
Connecting to:          mongodb://<credentials>@localhost:27017/testdb?authSource=testdb&directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.0
Using MongoDB:          6.0.23
Using Mongosh:          2.5.0
```

## Tests Python – Insertion, lecture, mise à jour, suppression

J'ai réalisé un script Python permettant de tester toutes les opérations CRUD :

- Insertion de documents (`insert_many`)
- Requête simple avec `find()`
- Mise à jour d’un document (`update_one`)
- Suppression d’un document (`delete_one`)

Extrait du code :

```python
collection.insert_many([
    {"name": "David", "age": 40},
    {"name": "Emma", "age": 31}
])

collection.update_one({"name": "David"}, {"$set": {"age": 41}})

collection.delete_one({"name": "Emma"})
```
Réponse :
```
Insertion terminée
Contenu de la collection :
{'_id': ObjectId('683dd13f389415a16cd861e0'), 'name': 'Alice', 'age': 28}
{'_id': ObjectId('683dd13f389415a16cd861e1'), 'name': 'Bob', 'age': 34}
{'_id': ObjectId('683dd13f389415a16cd861e2'), 'name': 'Charlie', 'age': 22}
{'_id': ObjectId('683dd1faf9fb869d44d0fe68'), 'name': 'David', 'age': 40}
{'_id': ObjectId('683dd1faf9fb869d44d0fe69'), 'name': 'Emma', 'age': 31}
Mise à jour effectuée
Document mis à jour : {'_id': ObjectId('683dd1faf9fb869d44d0fe68'), 'name': 'David', 'age': 41}
Document supprimé
Documents restants :
{'_id': ObjectId('683dd13f389415a16cd861e0'), 'name': 'Alice', 'age': 28}
{'_id': ObjectId('683dd13f389415a16cd861e1'), 'name': 'Bob', 'age': 34}
{'_id': ObjectId('683dd13f389415a16cd861e2'), 'name': 'Charlie', 'age': 22}
{'_id': ObjectId('683dd1faf9fb869d44d0fe68'), 'name': 'David', 'age': 41}
```



---

# Partie 2 – Déploiement MongoDB en Replica Set

## Objectif

Déployer un Replica Set MongoDB avec trois instances dans des conteneurs Docker, puis vérifier la réplication entre les membres.

---

## Méthode de déploiement

J'ai utilisé **Docker Compose** pour lancer trois instances MongoDB (mongo1, mongo2, mongo3), chacune avec une configuration de réplication.

Chaque instance utilise un fichier `mongo.conf` spécifiant le nom du Replica Set `rs0`.

Extrait du `docker-compose.yml` :

```yaml
services:
  mongo1:
    image: mongo:6
    ports:
      - "27117:27017"
    volumes:
      - ./mongo1/mongo.conf:/etc/mongo/mongod.conf
      - ./init-replica.js:/init-replica.js
```
Extrait d’un fichier `mongo.conf` :
```yaml
replication:
  replSetName: "rs0"
net:
  bindIp: 0.0.0.0
```

## Initialisation du Replica Set

Une fois les conteneurs lancés avec :

```bash
docker-compose up -d
```
Ont fait :
```bash
docker exec -it mongo1 mongosh
```

J'ai initialisé le Replica Set via le fichier `init-replica.js` :

```js
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" }
  ]
})
```
Chargement dans le shell :

```js
load("/init-replica.js")
```

## Vérification de l'état du Replica Set

Resultat dans le shell :
```bash
rs0 [direct: secondary] test> rs.status()
...
{
  set: 'rs0',
  date: ISODate('2025-06-02T15:01:52.536Z'),
  myState: 1,
  term: Long('1'),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long('2000'),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 3,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
    lastCommittedWallTime: ISODate('2025-06-02T15:01:43.943Z'),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
    appliedOpTime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
    durableOpTime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
    lastAppliedWallTime: ISODate('2025-06-02T15:01:43.943Z'),
    lastDurableWallTime: ISODate('2025-06-02T15:01:43.943Z')
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1748876483, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'electionTimeout',
    lastElectionDate: ISODate('2025-06-02T14:59:43.871Z'),
    electionTerm: Long('1'),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 1748876372, i: 1 }), t: Long('-1') },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1748876372, i: 1 }), t: Long('-1') },
    numVotesNeeded: 2,
    priorityAtElection: 1,
    electionTimeoutMillis: Long('10000'),
    numCatchUpOps: Long('0'),
    newTermStartDate: ISODate('2025-06-02T14:59:43.919Z'),
    wMajorityWriteAvailabilityDate: ISODate('2025-06-02T14:59:44.473Z')
  },
  members: [
    {
      _id: 0,
      name: 'mongo1:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 159,
      optime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2025-06-02T15:01:43.000Z'),
      lastAppliedWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      lastDurableWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1748876383, i: 1 }),
      electionDate: ISODate('2025-06-02T14:59:43.000Z'),
      configVersion: 1,
      configTerm: 1,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 1,
      name: 'mongo2:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 139,
      optime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
      optimeDurable: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2025-06-02T15:01:43.000Z'),
      optimeDurableDate: ISODate('2025-06-02T15:01:43.000Z'),
      lastAppliedWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      lastDurableWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      lastHeartbeat: ISODate('2025-06-02T15:01:51.955Z'),
      lastHeartbeatRecv: ISODate('2025-06-02T15:01:50.960Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'mongo1:27017',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 1,
      configTerm: 1
    },
    {
      _id: 2,
      name: 'mongo3:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 139,
      optime: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
      optimeDurable: { ts: Timestamp({ t: 1748876503, i: 1 }), t: Long('1') },
      optimeDate: ISODate('2025-06-02T15:01:43.000Z'),
      optimeDurableDate: ISODate('2025-06-02T15:01:43.000Z'),
      lastAppliedWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      lastDurableWallTime: ISODate('2025-06-02T15:01:43.943Z'),
      lastHeartbeat: ISODate('2025-06-02T15:01:51.954Z'),
      lastHeartbeatRecv: ISODate('2025-06-02T15:01:50.960Z'),
      pingMs: Long('0'),
      lastHeartbeatMessage: '',
      syncSourceHost: 'mongo1:27017',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 1,
      configTerm: 1
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1748876503, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1748876503, i: 1 })
}
```

tests de réplication :
```bash
rs0 [primary] test> use testdb
switched to db testdb
rs0 [primary] testdb> db.replicatest.insertOne({ message: "Hello from primary" })
{
  acknowledged: true,
  insertedId: ObjectId('683e99bbe4fe9f7fe5d861e0')
}

rs0 [direct: secondary] testdb> db.replicatest.find()
[
  {
    _id: ObjectId('683e99bbe4fe9f7fe5d861e0'),
    message: 'Hello from primary'
  }
]
```
Erreur rencontrée :

en faisant `docker exec -it mongo1 mongosh` ça me connectait au secondary, pour réglé le problème il fallait écrire :
`docker exec -it mongo1 mongosh "mongodb://mongo1:27017/?replicaSet=rs0"`

# Intégration dans une application

## Objectif

Créer une application Python capable de se connecter à MongoDB (Replica Set), effectuer des opérations de type CRUD, et tester l’intégration automatiquement.

---

## Connexion à MongoDB (Replica Set)

Connexion via URI sécurisée avec utilisateur `testuser` (créé dans la base `testdb`) et `authSource=testdb`.

```python
uri = (
    "mongodb://testuser:testpass@mongo1:27017,mongo2:27017,mongo3:27017/"
    "?replicaSet=rs0&authSource=testdb"
)
client = MongoClient(uri)
```
Attente de l’élection du PRIMARY (boucle hello)
```python
from pymongo.errors import ServerSelectionTimeoutError
import time

for i in range(10):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        hello = client.admin.command("hello")
        if hello.get("isWritablePrimary", False):
            print("✅ PRIMARY détecté")
            break
    except ServerSelectionTimeoutError:
        print("⏳ En attente d’un PRIMARY...")
        time.sleep(2)
else:
    print("❌ Aucun PRIMARY détecté après 10 tentatives")
    exit(1)
```

Script principal :
```python
from pymongo import MongoClient
import time

uri = (
    "mongodb://testuser:testpass@mongo1:27017,mongo2:27017,mongo3:27017/"
    "?replicaSet=rs0&authSource=testdb"
)

client = MongoClient(uri)

db = client["testdb"]
collection = db["appCollection"]

collection.insert_one({"name": "ReplicaApp", "version": 1})
print("✅ Insertion effectuée")

result = collection.find_one({"name": "ReplicaApp"})
print("🔍 Résultat trouvé :", result)

collection.update_one({"name": "ReplicaApp"}, {"$set": {"version": 2}})
print("✏️ Mise à jour réussie")

collection.delete_one({"name": "ReplicaApp"})
print("🗑️ Document supprimé")

client.close()
```

Tests automatisés :
```python
import unittest
from pymongo import MongoClient

class TestMongoDBIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        uri = (
            "mongodb://testuser:testpass@mongo1:27017,mongo2:27017,mongo3:27017/"
            "?replicaSet=rs0&authSource=testdb"
        )
        cls.client = MongoClient(uri)
        cls.db = cls.client["testdb"]
        cls.col = cls.db["test_tests"]

    def test_insert(self):
        result = self.col.insert_one({"name": "TestUser", "score": 100})
        self.assertTrue(result.acknowledged)

    def test_find(self):
        doc = self.col.find_one({"name": "TestUser"})
        self.assertIsNotNone(doc)
        self.assertEqual(doc["score"], 100)

    def test_update(self):
        self.col.update_one({"name": "TestUser"}, {"$set": {"score": 200}})
        doc = self.col.find_one({"name": "TestUser"})
        self.assertEqual(doc["score"], 200)

    def test_delete(self):
        self.col.delete_one({"name": "TestUser"})
        doc = self.col.find_one({"name": "TestUser"})
        self.assertIsNone(doc)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

if __name__ == "__main__":
    unittest.main()
```

# Intégration avec Docker
Dockerfile pour l’application Python
```
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```
Ajout dans docker-compose.yml
```
  app:
    build: ../../integration/python
    container_name: mongo-python-app
    depends_on:
      - mongo1
      - mongo2
      - mongo3
    networks:
      - mongo-cluster
```
## Commandes pour les tests

`docker-compose up -d `

`docker exec -it mongo1 mongosh --eval "load('/init-replica.js')"`

ensuite comme de base il se connecte à un secondary il faut :

rentrer dans mongosh : `docker exec -it mongo1 mongosh "mongodb://mongo1:27017/?replicaSet=rs0"`

puis ecrire ce bout de code :
```JS
db = db.getSiblingDB("testdb");

db.createUser({
  user: "testuser",
  pwd: "testpass",
  roles: [{ role: "readWrite", db: "testdb" }]
});
```

ensuite ont peux faire :

`docker-compose up --build app`


ont obtient : 
```
mongo-python-app  | PRIMARY détecté
mongo-python-app  | Document inséré
mongo-python-app  | Résultat : {'_id': ObjectId('683eaee0020fdb9f239e5175'), 'name': 'ReplicaApp', 'version': 1}                                                                    
mongo-python-app  | Document mis à jour                                                                                                                                             
mongo-python-app  | Document supprimé
mongo-python-app exited with code 0
```

