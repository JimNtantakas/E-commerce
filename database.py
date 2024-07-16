from pymongo import MongoClient

#client = MongoClient()   # same as: client = MongoClient("localhost", 27017)
client = MongoClient("localhost", 27017)

#create the database
db = client["test-database"]

#create a collection
collection = db["my collection"]

#insert data to the collection
document = {"name": "Alice", "age": 25, "city": "New York"}
collection.insert_one(document)

collection.delete_many({})