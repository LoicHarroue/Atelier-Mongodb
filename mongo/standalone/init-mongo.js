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
