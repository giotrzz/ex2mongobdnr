import os
from pymongo import MongoClient

db = MongoClient(os.getenv("MONGO_URI") or input("URI: ")).mercado_livre
for c in ["usuario", "vendedor", "produto", "compra"]:
    db[c].delete_many({})
print("Coleções limpas.")