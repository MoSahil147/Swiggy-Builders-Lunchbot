# thsi is the brain of the bot! 
# using groq, always helped me to do better things! Love you Groq
# will use convo history passed from main.py so the agent will have the full context

# os and json ke upar nothing!
import json
import os
from groq import Groq
from dotenv import load_dotenv
from swiggy import search_resturants, search_menu, update_cart, get_cart, place_order

load_dotenv()

# Groq time
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

# below will be a tool scheme, in short tool scheme is sexy, tells the LLM what functions it can call and what args they need!
TOOLS=[
    {
        # search resturent function
        "type":"function",
        "function":{
            "name":"search_resturants",
            'description': "Search for restaurants. Use this when you need to find restaurants based on cuisine preferences from the team.",
            "parameters":{
                "type":"object",
                "properties":{
                    "cusine":{
                        "type":"string",
                        "description":"Cusine type to search for eg Biryani, Pizza or Chinese"
                    },
                    "location":{
                        "type":"string",
                        "description":"Delivery location, default is Panvel"
                    }
                }
            }
        }
    },
    # search menu, update cart, get cart, place order will write down properly! in same fasion
]