import pymongo

# Database
client = pymongo.MongoClient('mongodb+srv://admin:<password>@cluster0.nctcpir.mongodb.net/?retryWrites=true&w=majority')
db = client.tisbakery_db
print(client)