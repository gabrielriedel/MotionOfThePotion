from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
    
    if num_red_potions > 0:

        return [
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": num_red_potions,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
            ]
    
    if num_green_potions > 0:

        return [
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num_green_potions,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            ]
    
    if num_blue_potions > 0:

        return [
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": num_blue_potions,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                }
            ]
    
    return []
