import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).parent.parent/"data"/"dummy.json"

def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,'r',encoding='utf-8') as file:
        data = json.load(file)
        if not isinstance(data, list):   # ← guard against malformed file
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
