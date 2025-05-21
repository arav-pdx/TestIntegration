from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


fake_db = {}

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = fake_db.get(item_id)
    if item:
        return item
    return {"error ": "Item not found"}

@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item):
    fake_db[item_id] = item
    return {"message" : "item has been created", "item": item}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id in fake_db:
       return {"error" : "item not found"}
    fake_db[item_id] = item
    return {"message" : "item updated", "Item" : item}

@app.delete("/items/{item.id}")
def delete_item(item_id: int, item: Item):
    if item_id in fake_db:
        del fake_db[item_id]
        return {"message" : f"Item {item_id} deleted"}
    return {"error" : "Item not found"}



@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


