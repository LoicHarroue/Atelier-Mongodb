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
