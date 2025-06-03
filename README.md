# Atelier MongoDB – Groupe Ynov Campus

Projet d'intégration et de déploiement de MongoDB en différents modes : **Standalone**, **Replica Set**, et (optionnellement) **Sharding**, avec une application Python connectée.

---

## Objectifs

- Déployer MongoDB en :
  - Mode Standalone
  - Mode Replica Set
  - Mode Sharded (bonus)
- Intégrer MongoDB dans une application Python
- Documenter toutes les étapes
- Tester les opérations CRUD via script et tests unitaires
- Versionner le projet avec Git

---

## Structure du projet
atelier-mongodb/
├── docs/
│ └── rapport.md 
├── mongo/
│ ├── standalone/
│ ├── replicaset/ 
│ └── sharding/ 
├── integration/
│ └── python/ 
│ ├── main.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── tests/
│   └── test_connection.py
└── README.md

---

## Lancement du projet

### MongoDB Standalone

```bash
cd mongo/standalone
docker-compose up -d
```

Par défaut :

    Utilisateur : testuser
    
    Mot de passe : testpass
    
    Base : testdb

Test de connexion possible avec mongosh

## MongoDB Replica Set + App Python

```
cd mongo/replicaset
docker-compose up --build -d
```
Attendre l’élection du PRIMARY (~5-10 sec).
Ensuite, exécuter l’app :

```
docker-compose up --build app
```
`Voir dans rapport pour la suite de l'execution de l'app`

## Méthodes de connexion (résumé)
Standalone :

```python
MongoClient("mongodb://testuser:testpass@localhost:27017/testdb?authSource=testdb")
```
Replica Set (dans Docker) :

```python
MongoClient("mongodb://testuser:testpass@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0&authSource=testdb")
```

