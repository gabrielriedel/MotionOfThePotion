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
        results = connection.execute(sqlalchemy.text("SELECT inventory, sku, name, type, price FROM potions"))
    for row in results:
        catalog.append({
            "sku": row.sku, 
            "name": row.name, 
            "quantity": row.inventory,
            "price": row.price,
            "potion_type": row.type
            })
    
    return catalog
    # if num_red_potions > 0:

    #     return [
    #             {
    #                 "sku": "RED_POTION_0",
    #                 "name": "red potion",
    #                 "quantity": num_red_potions,
    #                 "price": 30,
    #                 "potion_type": [100, 0, 0, 0],
    #             }
    #         ]
    
    # if num_green_potions > 0:

    #     return [
    #             {
    #                 "sku": "GREEN_POTION_0",
    #                 "name": "green potion",
    #                 "quantity": num_green_potions,
    #                 "price": 30,
    #                 "potion_type": [0, 100, 0, 0],
    #             }
    #         ]
    
    # if num_blue_potions > 0:

    #     return [
    #             {
    #                 "sku": "BLUE_POTION_0",
    #                 "name": "blue potion",
    #                 "quantity": num_blue_potions,
    #                 "price": 30,
    #                 "potion_type": [0, 0, 100, 0],
    #             }
    #         ]
    
    
