# brain of the bot
# uses groq + llama-3.3-70b-versatile
# conversation history passed in from main.py on every request

import json
import os
from groq import Groq, BadRequestError
from dotenv import load_dotenv
from swiggy import search_restaurants, search_menu, update_cart, get_cart, place_order

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

# FIX: removed search_restaurants from TOOLS entirely.
# llama-3.3-70b-versatile falls back to a text-based <function=...> format when the
# conversation is long or involves chaining multiple searches (e.g. Chinese + South Indian
# + North Indian all in one turn). Groq rejects that format with a 400 error.
# Instead, we pre-load all restaurant data into the system prompt so the model already
# knows what's available — no tool call needed for search.
# Only search_menu, update_cart, get_cart, and place_order remain as tools since
# those are simpler single-argument calls that work reliably.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_menu",
            "description": "Get the full menu for a restaurant by its ID. Call this once the group has agreed on a restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {
                        "type": "string",
                        "description": "Restaurant ID from the list e.g. r1, r2, r3, r4, r5"
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
            "description": "Add an item to the group cart for a specific person.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id":       {"type": "string"},
                    "item_name":     {"type": "string"},
                    "price":         {"type": "number"},
                    "quantity":      {"type": "integer"},
                    "user":          {"type": "string", "description": "Name of the person ordering"},
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
            "description": "Check everything currently in the group cart.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place the final group order after everyone has picked their items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "Name of the restaurant"
                    }
                },
                "required": ["restaurant_name"]
            }
        }
    }
]

TOOL_MAP = {
    "search_menu":  search_menu,
    "update_cart":  update_cart,
    "get_cart":     get_cart,
    "place_order":  place_order,
}

# Pre-load restaurant list into the system prompt so the model never needs to call search_restaurants.
# This avoids the <function=...> format bug entirely for the search step.
def build_system_prompt():
    restaurants = search_restaurants()
    restaurant_lines = "\n".join(
        f"  - {r['name']} (ID: {r['id']}, Cuisine: {r['cuisine']}, Rating: {r['rating']}, ETA: {r['eta']}, Min order: Rs.{r['min_order']})"
        for r in restaurants
    )

    return f"""You are LunchBot, a friendly group lunch coordinator for a team of 3: Fernandes, Ila, and Shaikh.

Available restaurants on Swiggy (Panvel):
{restaurant_lines}

Your job:
1. Collect everyone's cuisine preferences — wait until all 3 have shared what they want
2. Based on their preferences, suggest the best matching restaurant from the list above (you already know all the restaurants, no need to search)
3. If preferences differ, suggest the restaurant that best covers the most people, or ask the group to vote
4. Once a restaurant is agreed on, call search_menu to get the menu and show it to the group
5. Help each person pick their items and call update_cart for each item
6. Once everyone has ordered, call get_cart to confirm, then call place_order
7. Show a final summary with each person's items and the grand total

Rules:
- Always address people by their name
- You already have the restaurant list above — never say you need to search for restaurants
- Match restaurant suggestions to what people actually asked for
- Keep responses short and friendly
- Format menus cleanly with item name and price in Rs.
- Always confirm the cart before placing the final order"""


SYSTEM_PROMPT = build_system_prompt()


def _groq_call(messages, use_tools=True):
    if use_tools:
        return client.chat.completions.create(
            model=MODEL, messages=messages,
            tools=TOOLS, tool_choice="auto",  # type: ignore[arg-type]
            temperature=0.7, max_tokens=1024
        )
    return client.chat.completions.create(
        model=MODEL, messages=messages,
        temperature=0.7, max_tokens=1024
    )


def run_agent(conversation_history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    try:
        response = _groq_call(messages)
    except BadRequestError:
        # model generated malformed <function=...> syntax — retry as plain text
        return _groq_call(messages, use_tools=False).choices[0].message.content

    # tool call loop — handles chained calls like search_menu -> update_cart -> place_order
    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)

        for tc in tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments) or {}

            print(f"[tool call] {fn_name}({fn_args})")

            result = TOOL_MAP[fn_name](**fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })

        try:
            response = _groq_call(messages)
        except BadRequestError:
            return _groq_call(messages, use_tools=False).choices[0].message.content

    return response.choices[0].message.content
