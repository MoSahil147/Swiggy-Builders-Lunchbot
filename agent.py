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
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search for restaurants. Use this when you need to find restaurants based on cuisine preferences from the team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuisine": {
                        "type": "string",
                        "description": "Cuisine type to search for e.g. Biryani, Pizza, Chinese"
                    },
                    "location": {
                        "type": "string",
                        "description": "Delivery location, default is Panvel"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_menu",
            "description": "Get the menu for a specific restaurant. Use this after picking a restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {
                        "type": "string",
                        "description": "The ID of the restaurant"
                    }
                },
                "required": ["restaurant_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_cart",
            "description": "Add a food item to the group cart for a specific user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "item_name": {"type": "string"},
                    "price": {"type": "number"},
                    "quantity": {"type": "integer"},
                    "user": {"type": "string", "description": "Name of the team member ordering this"},
                    "restaurant_id": {"type": "string"}
                },
                "required": ["item_id", "item_name", "price", "quantity", "user", "restaurant_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "Check what's currently in the group cart."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place the final group order once everyone has picked their items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "Name of the restaurant being ordered from"
                    }
                },
                "required": ["restaurant_name"]
            }
        }
    }
]

# now map time, maps tool name strings to actual python functions
TOOL_MAP = {
    "search_restaurants": search_restaurants,
    "search_menu": search_menu,
    "update_cart": update_cart,
    "get_cart": get_cart,
    "place_order": place_order,
}

SYSTEM_PROMPT = """You are LunchBot, a friendly group lunch coordinator for a team.

Your job:
1. Greet the team and ask everyone what they're in the mood for
2. Once you have a sense of preferences, search for restaurants that work for the group
3. Suggest a restaurant and show the menu
4. Help each person pick their items and add to cart
5. Once everyone has ordered, place the final group order and share the summary

Rules:
- Always address people by their name
- Be friendly, casual, and quick — nobody wants a slow lunch bot
- If preferences conflict, find a restaurant with variety (North Indian places usually work for everyone)
- Always confirm before placing the final order
- Keep responses concise, this is a chat not an essay
- When showing menus, format them cleanly with prices
- After placing order, show a clean summary with each person's items and the total"""

def run_agent(conversation_history: list) -> str:
    # build messages array with system prompt + full history (history is imp)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    # first LLM call
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.7,  # slight creativity, keeps responses feeling natural
        max_tokens=1024
    )
    
    # tool call loop, groq might need multiple rounds to complete a task
    # e.g. search restaurants then pick one then get menu then add items then place order

    while response.choices[0].finish_reason =="tool_calls":
        tool_calls = response.choices[0].message.tool_calls

        # add assistant's tool call message to history
        messages.append(response.choices[0].message)
        
        # execute each tool call and add results back
        for tc in tool_calls:
            fn_name=tc.function.name
            fn_args=json.loads(tc.function.arguments)
            
            print(f"[tool call] {fn_name}({fn_args})")  # helpful for debugging

            # call the actual mock function
            result = TOOL_MAP[fn_name](**fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })
            
        # call LLM again with tool results included
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024
        )

    return response.choices[0].message.content
