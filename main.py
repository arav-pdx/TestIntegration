from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

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



#### CSHARP CODE BELOW


# --- NEW: Models for interacting with C# API ---
class CSharpBusinessRequest(BaseModel):
    input_data: str # Maps to C#'s InputData (Pydantic automatically handles snake_case to PascalCase for JSON)
    process_id: int # Maps to C#'s ProcessId

class CSharpBusinessResponse(BaseModel):
    success: bool
    result_data: str | None = None # Allow None if C# might not return it
    message: str


# Configuration for C# API URL
# It's good practice to get this from environment variables
CSHARP_API_BASE_URL = os.getenv("CSHARP_API_URL", "http://localhost:5202")
# Make sure the port matches where your C# API is running!

@app.post("/invoke-csharp-process", response_model=CSharpBusinessResponse)
async def invoke_csharp_process(request_data: CSharpBusinessRequest):
    """
    An endpoint in Python FastAPI that calls the C# business logic API.
    """
    async with httpx.AsyncClient() as client:
        try:
            csharp_payload = { # Python dict will be serialized to JSON
                "InputData": request_data.input_data, # Explicitly PascalCase if C# expects it strictly
                "ProcessId": request_data.process_id
            }
            # If your C# API expects camelCase, then:
            # csharp_payload = request_data.model_dump()

            response = await client.post(
                f"{CSHARP_API_BASE_URL}/process",
                json=csharp_payload # httpx will serialize this dict to JSON
            )

            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()

            # Deserialize C# response
            csharp_response_data = response.json()
            return CSharpBusinessResponse(**csharp_response_data)

        except httpx.HTTPStatusError as exc:
            # Error from the C# API (e.g., 400 Bad Request, 500 Internal Server Error)
            # You might want to log exc.response.text for more details
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from C# service: {exc.response.text}"
            )
        except httpx.RequestError as exc:
            # Network error, C# service unreachable, etc.
            raise HTTPException(
                status_code=503, # Service Unavailable
                detail=f"Could not connect to C# service: {str(exc)}"
            )

@app.get("/check-csharp-health")
async def check_csharp_health():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CSHARP_API_BASE_URL}/health")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"C# service unreachable: {str(exc)}")
        except httpx.HTTPStatusError as exc:
             raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from C# health check: {exc.response.text}"
            )


# --- Your existing FastAPI endpoints (read_root, read_item, etc.) ---
# These are independent of the C# calls unless you modify them to call C#
@app.get("/")
async def read_root():
    return {"message": "Hello World from Python FastAPI"}

# ... (other endpoints like create_item, update_item, delete_item, say_hello)
# Make sure to fix the issues in update_item and delete_item as pointed out previously
# if you intend to keep them.
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in fake_db:
       raise HTTPException(status_code=404, detail="Item not found")
    fake_db[item_id] = item
    return {"message" : "item updated", "Item" : item}

@app.delete("/items/{item_id}") # Corrected path
def delete_item(item_id: int): # Removed unused item body
    if item_id in fake_db:
        del fake_db[item_id]
        return {"message" : f"Item {item_id} deleted"}
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


