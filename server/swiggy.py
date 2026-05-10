# here we will pretend to be the SWIGGY API
# when we will get real Swiggy API will replace these functions
# will try to match what real Swiggy MCP tools would return

import random

# 1 searching resturant

def search_restaurants(cuisine=None, location="Panvel"):
    # for now just returning hardcoded list of returants
    resturants=[
        {"id":"r1", "name":"Biryani Baba", "cuisine":"Biryani", "rating":4.5, "eta":"30 mins", "min_order":200},
        {"id":"r2", "name":"Punjabi Tagda", "cuisine":"North Indian", "rating":4.2, "eta":"35 mins", "min_order":250},
        {"id":"r3", "name":"Seedhe Pizza", "cuisine":"Pizza", "rating":4.7, "eta":"25 mins", "min_order":300},
        {"id":"r4", "name":"China Wok", "cuisine":"Chinese", "rating":4.3, "eta":"40 mins", "min_order":200},
        {"id":"r5", "name":"Anna Idli", "cuisine":"South Indian", "rating":4.4, "eta":"20 mins", "min_order":100},
    ]
    
    # will filter by cuisine if provided
    if cuisine:
        filtered=[r for r in resturants if cuisine.lower() in r["cuisine"].lower()]
        # if nothing matches just return everything, agent will handle it
        return filtered if filtered else resturants
    return resturants

def search_menu(restaurant_id):
    # will return menu items for a given resturant
    # each item will have enough info for the agent to make decesion
    menus={
        "r1":[
            {"item_id": "r1_i1", "name": "Chicken Biryani", "price": 280, "veg": False, "calories": 650},
            {"item_id": "r1_i2", "name": "Veg Biryani", "price": 220, "veg": True, "calories": 520},
            {"item_id": "r1_i3", "name": "Mutton Biryani", "price": 320, "veg": False, "calories": 720},
            {"item_id": "r1_i4", "name": "Raita", "price": 60, "veg": True, "calories": 80},
            {"item_id": "r1_i5", "name": "Gulab Jamun", "price": 80, "veg": True, "calories": 200},
        ],
        "r2":[
            {"item_id": "r2_i1", "name": "Butter Chicken", "price": 320, "veg": False, "calories": 600},
            {"item_id": "r2_i2", "name": "Dal Makhani", "price": 240, "veg": True, "calories": 400},
            {"item_id": "r2_i3", "name": "Paneer Butter Masala", "price": 280, "veg": True, "calories": 450},
            {"item_id": "r2_i4", "name": "Garlic Naan", "price": 50, "veg": True, "calories": 150},
            {"item_id": "r2_i5", "name": "Jeera Rice", "price": 120, "veg": True, "calories": 300},
        ],
        "r3": [
            {"item_id": "r3_i1", "name": "Margherita Pizza", "price": 299, "veg": True, "calories": 700},
            {"item_id": "r3_i2", "name": "Pepperoni Pizza", "price": 349, "veg": False, "calories": 850},
            {"item_id": "r3_i3", "name": "BBQ Chicken Pizza", "price": 379, "veg": False, "calories": 900},
            {"item_id": "r3_i4", "name": "Garlic Bread", "price": 99, "veg": True, "calories": 300},
            {"item_id": "r3_i5", "name": "Coke", "price": 60, "veg": True, "calories": 140},
        ],
        "r4": [
            {"item_id": "r4_i1", "name": "Chicken Fried Rice", "price": 220, "veg": False, "calories": 550},
            {"item_id": "r4_i2", "name": "Veg Hakka Noodles", "price": 180, "veg": True, "calories": 450},
            {"item_id": "r4_i3", "name": "Chilli Chicken", "price": 260, "veg": False, "calories": 500},
            {"item_id": "r4_i4", "name": "Veg Manchurian", "price": 200, "veg": True, "calories": 380},
            {"item_id": "r4_i5", "name": "Spring Rolls", "price": 140, "veg": True, "calories": 280},
        ],
        "r5": [
            {"item_id": "r5_i1", "name": "Masala Dosa", "price": 120, "veg": True, "calories": 350},
            {"item_id": "r5_i2", "name": "Idli Sambar (3 pcs)", "price": 90, "veg": True, "calories": 250},
            {"item_id": "r5_i3", "name": "Vada (2 pcs)", "price": 80, "veg": True, "calories": 200},
            {"item_id": "r5_i4", "name": "Uttapam", "price": 130, "veg": True, "calories": 380},
            {"item_id": "r5_i5", "name": "Filter Coffee", "price": 60, "veg": True, "calories": 80},
        ],
    }
    
    return menus.get(restaurant_id,[])

# we need a cart in memory during the session
# gets reset when /reset will be called
cart=[]

#now updation of cart
def update_cart(item_id, item_name, price, quantity, user, restaurant_id):
    # will add or maybe update the item in the shared group cart
    # will check if same user already added the same item, then we will update the quantity instead of duplicating that
    for item in cart:
        if item["item_id"]==item_id and item["user"]==user:
            item["quantity"]+=quantity
            return {"status":"updated", "item":item_name, "quantity":item["quantity"], "user":user}

    cart.append({
        "item_id":item_id,
        "item_name":item_name,
        "price":price,
        "quantity":quantity,
        "user":user,
        "restaurant_id":restaurant_id,
    })

    return {"status":"added", "item":item_name, "quantity":quantity, "user":user}
    
# state of the cart
def get_cart():
    # agent can check the state of of the cart anytime
    total=sum(item["price"]*item["quantity"] for item in cart)
    return {"items":cart, "total":total, "item_count":len(cart)}

# final step of placing order
def place_order(restaurant_name):
    # finalise the order
    if not cart:
        return {"status":"error", "message":"Cart is empty!"}
    
    total=sum(item["price"]*item["quantity"] for item in cart)
    
    order={
        # SWG is for Swiggy 
        "order_id":f"SWG{random.randint(100000, 999999)}",
        "restaurant":restaurant_name,
        "status":"confirmed",
        "items":cart.copy(),
        "total":total,
        #hard coding the ETA. will figue out how to show in real time!
        "eta":"35 mins",
        "message":"Order placed successfully! Food is being prepared!"
    }
    
    # clear cart as order placed
    cart.clear()
    
    return order

def reset_cart():
    cart.clear()
    return{"status":"cart cleared"}

