import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).parent.parent/"data"/"products.json"

def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,'r',encoding='utf-8') as file:
        data = json.load(file)
        if not isinstance(data, list):
            return []
        return data
    
def get_all_products() -> List[Dict]:
    return load_products()

def save_product(products : List[Dict]) -> None:
    with open(DATA_FILE, "w", encoding = "utf-8") as f:
        json.dump(products, f, indent = 2, ensure_ascii=False)

def add_product(product : Dict) -> Dict:
    print(f"DATA_FILE path: {DATA_FILE}")
    print(f"File exists: {DATA_FILE.exists()}")

    products = get_all_products()

    print(f"Loaded {len(products)} products")

    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists")
    
    products.append(product)
    save_product(products)
    return product

def remove_product(id : str) -> None :
    products = get_all_products()

    for idx,p in enumerate(products):
        if p["product_id"] == str(id):
            deleted = products.pop(idx)
            save_product(products)
            return {"message" : "Product deleted successfully",
                    "data" : deleted}
    raise ValueError(f"Product with id={id} not found")


def change_product(product_id: str, update_data: dict):
    products = get_all_products()

    for index, product in enumerate(products):

        # To reacch to theh product whose info needs to be updated
        if product["product_id"] != product_id:
            continue

        for key, value in update_data.items():
            if value is None:
                continue

            # For nested dicts like dimensions_cm and seller: merge, don't replace
            if isinstance(value, dict) and isinstance(product.get(key), dict):
                product[key].update(value)
            else:
                product[key] = value

        # Recompute final_price if price or discount changed
        if "price" in update_data or "discount_percent" in update_data:
            price = product.get("price", 0)
            discount = product.get("discount_percent", 0)
            product["final_price"] = round(price * (1 - discount / 100), 2)

        # Recompute volume_c3 if dimensions changed
        if "dimensions_cm" in update_data:
            d = product.get("dimensions_cm", {})
            if d.get("length") and d.get("width") and d.get("height"):
                product["volume_c3"] = round(d["length"] * d["width"] * d["height"], 2)

        products[index] = product
        # now save the full list
        save_product(products)
        return product
    
    raise ValueError("Product not found.!!")