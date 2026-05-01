# here we will pretend to be the SWIGGY API
# when we will get real Swiggy API will replace these functions
# will try to match what real Swiggy MCP tools would return

# 1 searching resturant

def search_resturants(cuisine=None, location="Panvel"):
    # for now just returning hardcoded list of returants
    resturants=[
        {"id":"r1", "name":"Biryani Baba", "cuisine":"Biryani", "rating":4.5, "eta":"30 mins", "min_order":200},
        {"id":"r2", "name":"Burger Shurger", "cuisine":"Burger", "rating":4.2, "eta":"25 mins", "min_order":250},
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
        