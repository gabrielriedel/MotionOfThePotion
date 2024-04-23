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

        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        num_dark_ml = connection.execute(sqlalchemy.text("SELECT num_dark_ml FROM global_inventory")).scalar_one()

    for potion in potions_delivered:
        if potion.potion_type == [50,50,0,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :x"),[{"x": num_red_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x"),[{"x": num_green_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])
        elif potion.potion_type == [50,0,50,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :x"),[{"x": num_red_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :x"),[{"x": num_blue_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])
                
        elif potion.potion_type == [50,0,0,50]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :x"),[{"x": num_red_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_dark_ml = :x"),[{"x": num_dark_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])
        elif potion.potion_type == [0,50,50,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x"),[{"x": num_green_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :x"),[{"x": num_blue_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])
                
        elif potion.potion_type == [0,50,0,50]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x"),[{"x": num_green_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_dark_ml = :x"),[{"x": num_dark_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])
        
        elif potion.potion_type == [0,0,50,50]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :x"),[{"x": num_blue_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_dark_ml = :x"),[{"x": num_dark_ml-50*potion.quantity}])
                connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                   WHERE potions.type = :y"""),[{"x": potion.quantity, "y": potion.potion_type}])

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    bottles = []

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        num_dark_ml = connection.execute(sqlalchemy.text("SELECT num_dark_ml FROM global_inventory")).scalar_one()
        types = connection.execute(sqlalchemy.text("SELECT id, type FROM potions"))

    for row in types:
        red_quant = num_red_ml//50
        green_quant = num_green_ml//50
        blue_quant = num_blue_ml//50
        dark_quant = num_dark_ml//50

        if num_red_ml >= row.type[0] and num_green_ml >= row.type[1] and num_blue_ml >= row.type[2] and num_dark_ml >= row.type[3]:
            if row.id == 4 and num_green_ml < 50 and num_blue_ml < 50 and num_dark_ml < 50:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": num_red_ml//100,
                })
                num_red_ml -= row.type[0]
                print(row.type[0])
            if row.id == 5:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(red_quant, green_quant),
                })
                num_red_ml -= row.type[0]
                num_green_ml -= row.type[1]
            if row.id == 6:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(red_quant, blue_quant),
                })
                num_red_ml -= row.type[0]
                num_blue_ml -= row.type[2]
            if row.id == 7:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(red_quant, dark_quant),
                })
                num_red_ml -= row.type[0]
                num_dark_ml -= row.type[3]
            if row.id == 8:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(green_quant, blue_quant),
                })
                num_green_ml -= row.type[1]
                num_blue_ml -= row.type[2]
            if row.id == 9:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(green_quant, dark_quant),
                })
                num_green_ml -= row.type[1]
                num_dark_ml -= row.type[3]
            if row.id == 10:
                bottles.append({
                    "potion_type": row.type,
                    "quantity": min(blue_quant, dark_quant),
                })
                num_blue_ml -= row.type[2]
                num_dark_ml -= row.type[3]
            

    return bottles
    
    

if __name__ == "__main__":
    print(get_bottle_plan())
