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

        for potion in potions_delivered:
            connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            for i in range(len(potion.potion_type)):
                  if potion.potion_type[i] != 0:
                        potion_type_list = [0] * 4
                        potion_type_list[i] = 1
                        connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": potion_type_list, "y": -potion.quantity*potion.potion_type[i], "z": "Potion Bottled"}])
            num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
                                                    WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
                        

            
            # if potion.potion_type == [100,0,0,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [1,0,0,0], "y": -potion.quantity*100, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            # elif potion.potion_type == [0,0,100,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,1,0], "y": -potion.quantity*100, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            # elif potion.potion_type == [50,50,0,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [1,0,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,1,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            # elif potion.potion_type == [50,0,50,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [1,0,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,1,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
                    
            # elif potion.potion_type == [50,0,0,50]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [1,0,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,0,1], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            # elif potion.potion_type == [0,50,50,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,1,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,1,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
                    
            # elif potion.potion_type == [0,50,0,50]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,1,0,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,0,1], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            
            # elif potion.potion_type == [0,0,50,50]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,1,0], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,0,1], "y": -potion.quantity*50, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])
            # elif potion.potion_type == [34,33,33,0]:
            #         connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": potion.potion_type, "y": potion.quantity, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,0,1,0], "y": -potion.quantity*33, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [0,1,0,0], "y": -potion.quantity*33, "z": "Potion Bottled"}])
            #         connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
            #                                VALUES (:x, :y, :z)"""),
            #                                [{"x": [1,0,0,0], "y": -potion.quantity*34, "z": "Potion Bottled"}])
            #         num_potions = connection.execute(sqlalchemy.text("SELECT inventory FROM potions WHERE potions.type = :x"),[{"x": potion.potion_type}]).scalar_one()
            #         connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x
            #                                         WHERE potions.type = :y"""),[{"x": num_potions+potion.quantity, "y": potion.potion_type}])

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

        red_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS red_ml
                                                     FROM ml_ledger
                                                    WHERE potion_type = :x"""),[{"x": [1,0,0,0]}]).scalar_one()
        green_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS green_ml
                                                     FROM ml_ledger
                                                    WHERE potion_type = :x"""),[{"x": [0,1,0,0]}]).scalar_one()
        blue_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS blue_ml
                                                     FROM ml_ledger
                                                    WHERE potion_type = :x"""),[{"x": [0,0,1,0]}]).scalar_one()
        dark_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS dark_ml
                                                     FROM ml_ledger
                                                    WHERE potion_type = :x"""),[{"x": [0,0,0,1]}]).scalar_one()
        ml = [red_ml, green_ml, blue_ml, dark_ml]
        
        types = connection.execute(sqlalchemy.text("SELECT id, type FROM potions ORDER BY id ASC"))

        pot_cap = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(potion_cap), 0) 
                                                     FROM capacity""")).scalar_one()
        num_pot = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS potion_tot
                                                     FROM potion_ledger""")).scalar_one()

    for row in types:
        quant = 100000
        for i in range(len(row.type)):
            if row.type[i] != 0:
                quant = min(ml[i]//row.type[i], quant)

        quant = min(quant, (pot_cap-num_pot), 100)
        print((pot_cap-num_pot))
        print(quant)
        print(ml)
        if num_pot < pot_cap and quant > 0:
              bottles.append({
                     "potion_type": row.type,
                     "quantity": quant,
                 })
              num_pot += quant
              for i in range(len(row.type)):
                    ml[i] -= quant*row.type[i]





    # for row in types:
    #     red_quant = red_ml//50
    #     green_quant = green_ml//50
    #     blue_quant = blue_ml//50
    #     dark_quant = dark_ml//50
    #     if red_ml >= row.type[0] and green_ml >= row.type[1] and blue_ml >= row.type[2] and dark_ml >= row.type[3] and num_pot < pot_cap:
    #         if row.id == 4 and green_ml < 50 and blue_ml < 50 and dark_ml < 50:
    #             quant = red_ml//100
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             red_ml -= row.type[0]*quant
    #         elif row.id == 1:
    #             quant = blue_ml//100
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             blue_ml -= row.type[2]*quant
    #         elif row.id == 5:
    #             quant = min(red_quant, green_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             red_ml -= row.type[0]*quant
    #             green_ml -= row.type[1]*quant
    #         elif row.id == 6:
    #             quant = min(red_quant, blue_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             red_ml -= row.type[0]*quant
    #             blue_ml -= row.type[2]*quant
    #         elif row.id == 7:
    #             quant = min(red_quant, dark_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             red_ml -= row.type[0]*quant
    #             dark_ml -= row.type[3]*quant
    #         elif row.id == 8:
    #             quant = min(green_quant, blue_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             green_ml -= row.type[1]*quant
    #             blue_ml -= row.type[2]*quant
    #         elif row.id == 9:
    #             quant = min(green_quant, dark_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             green_ml -= row.type[1]*quant
    #             dark_ml -= row.type[3]*quant
    #         elif row.id == 10:
    #             quant = min(blue_quant, dark_quant)
    #             bottles.append({
    #                 "potion_type": row.type,
    #                 "quantity": min(quant,(pot_cap-num_pot)),
    #             })
    #             num_pot += min(quant,(pot_cap-num_pot))
    #             blue_ml -= row.type[2]*quant
    #             dark_ml -= row.type[3]*quant
            

    return bottles
    
    

if __name__ == "__main__":
    print(get_bottle_plan())
