from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.encoders import jsonable_encoder
from schema.product import Products
import json
from services.products import get_all_products, add_product, remove_product
from uuid import uuid4, UUID
from datetime import datetime

app = FastAPI()

@app.get('/')
def root():
    return {"message":"Welcome to FastAPI."}

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

@app.get("/produucts")
def list_products(

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
    products = get_all_products()
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
