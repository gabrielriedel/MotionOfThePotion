from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    """
    Each unique item combination must have only a single price.
    """
    catalog = []
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("SELECT inventory, sku, name, type, price, id FROM potions"))
    for row in results:

        if row.inventory > 0 and row.id !=10:
            catalog.append({
                "sku": row.sku, 
                "name": row.name, 
                "quantity": row.inventory,
                "price": row.price,
                "potion_type": row.type
                })
            
    return catalog
    
    
