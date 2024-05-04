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
        results = connection.execute(sqlalchemy.text("""SELECT sku, name, type, price, id 
                                                     FROM catalog"""))
        for row in results:
            inventory = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS potion_tot
                                                        FROM potion_ledger 
                                                        WHERE potion_type = :x"""),[{"x": row.type}]).scalar_one()

            if inventory > 0:
                catalog.append({
                    "sku": row.sku, 
                    "name": row.name, 
                    "quantity": inventory,
                    "price": row.price,
                    "potion_type": row.type
                    })
            
    return catalog
    
    
