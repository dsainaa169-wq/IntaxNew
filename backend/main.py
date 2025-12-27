from bson import ObjectId

@app.get("/acceptance")
def list_acceptance():
    docs = list(collection.find())

    # ObjectId-г string болгоно
    for d in docs:
        d["_id"] = str(d["_id"])

    return docs
