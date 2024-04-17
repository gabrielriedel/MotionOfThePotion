from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db



router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        new_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        new_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        new_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        new_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        new_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        new_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()

    for potion in potions_delivered:
        if potion.potion_type == [100,0,0,0]:
            new_red_ml -= 100*potion.quantity
            new_red_potions += potion.quantity
        if potion.potion_type == [0,100,0,0]:
            new_green_ml -= 100*potion.quantity
            new_green_potions += potion.quantity
        if potion.potion_type == [0,0,100,0]:
            new_blue_ml -= 100*potion.quantity
            new_blue_potions += potion.quantity
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :x").bindparams(x=new_red_ml))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :x").bindparams(x=new_red_potions))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x").bindparams(x=new_green_ml))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :x").bindparams(x=new_green_potions))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :x").bindparams(x=new_blue_ml))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :x").bindparams(x=new_blue_potions))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()

    red_bottle_quant = num_red_ml//100
    green_bottle_quant = num_green_ml//100
    blue_bottle_quant = num_blue_ml//100

    if red_bottle_quant > 0:
        return [
                {
                    "potion_type": [100, 0, 0, 0],
                 "quantity": red_bottle_quant,
                }
         ]
    if green_bottle_quant > 0:
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                 "quantity": green_bottle_quant,
                }
         ]
    if blue_bottle_quant > 0:
        return [
                {
                    "potion_type": [0, 0, 100, 0],
                 "quantity": blue_bottle_quant,
                }
         ]
    
    return []

if __name__ == "__main__":
    print(get_bottle_plan())
