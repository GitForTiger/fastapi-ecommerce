from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Path, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from schema.product import Products, ProductUpdate
import json, os
from services.products import get_all_products, add_product, remove_product, change_product, load_products
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict

load_dotenv()

app = FastAPI()

# About FastAPI Middleware
# @app.middleware("http")
# async def lifecycle(request : Request, call_next):
#     print("Before request")
#     response = await call_next(request)
#     print("After request")
#     return response

def commonLogic():
    return "Hi there!"

@app.get('/', response_model=dict) # this statement creates what is known as a route in FastAPI.
# response_model determines what data type the function on the route will return.
def root(dep = Depends(commonLogic)): # now the function "commonLogic" is a technical "dependency", "injected" on the root function.

    DB_PATH = os.getenv("BASE_URL")
    #return {"message":"Welcome to FastAPI.","dependency" : dep, "data path" : DB_PATH}
    return JSONResponse(
        status_code=200,
        content={
            "message":"Welcome to FastAPI.",
            "dependency" : dep,
            "data path" : DB_PATH
        }
    )
    # This second method basically allows us to give a custom status code.

# FETCHING THE DATA FROM ANOTHER FILE IN THE SAME PRODUCT FOLDER

# M1
# @app.get("/products")
# def Get_products():
#     return get_all_products()

#M2
# @app.get('/products/{product_id}')
# def get_products(product_id:str):
#     with open("../data/products.json", "r") as file:
#         products = json.load(file)

#     for product in products:
#         if product["product_id"] == product_id:
#             return product

#     raise HTTPException(status_code=404, detail="Product not found")

# @app.get("/products")
# def list_products(name:str):
#     return name
# Here the name:str does not make any sense,
# bcz the line 30 does not fetch data dynamically, so we need a query to make it work


@app.get("/products")
def list_products(
    dep = Depends(load_products),

    name:str = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Search by product name (case insensitive)",
        example="Energy bar"
    ),
    sort_by_price : bool = Query(
        default=False,
        description="Sort products by price"
    ),
    order : str = Query(
        default="asc",
        description="Sort order when sort_by_price=true (asc,desc)"
    ),
    limit : int = Query(
        default=5,
        ge=1,
        le=100,
        description="number of items to return",
    ),
    offset : int = Query(
        default=0,
        le=100,
        description="pagination offset",
    )
    ):
    # products = load_products()
    products = dep
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name","").lower()]

    if not products:
        raise HTTPException(
            status_code=404,detail=f"No product matching with name={name}"
            )
    
    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key = lambda p : p.get("price",0), reverse = reverse)

    total=len(products)

    products = products[offset:offset+limit]

    return {
        "total" : total,
        "offset" : offset,
        "limit" : limit,
        "items" : products
    }

@app.get("/products/{product_id}")
def get_product_by_id(product_id : str = Path(
    ...,
    min_length=36,
    max_length=36,
    description="UUID of the product",
    example="11110000-aaaa-2222-bbbb-333344445554"
)):
    products = get_all_products()
    for product in products:
        if (product["product_id"] == product_id):
            return product
    raise HTTPException(status_code=404,detail="Product not found!")

@app.post("/products", status_code=201)
def create_product(product: Products):
    product_dict = jsonable_encoder(product)   # ← handles AnyUrl, UUID, datetime properly
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return product_dict

@app.delete("/products/{product_id}")
def delete_product(product_id : UUID = Path(
    ...,
    description = "Product UUID"
)):
    try:
        data = remove_product(str(product_id))
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.put("/products/{product_id}")
def update(product_id : UUID = Path(
    ...,
    description = "Product UUID"
), payload : ProductUpdate = ... ):
        
    try:
        update_product = change_product(str(product_id), payload.model_dump(mode = "json", exclude_unset=True))
        # The exclude_unset=True ensures to not care about the values that do not have been given a value in the update section
        return update_product
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
