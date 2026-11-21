import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

def get_poke_data():
    url = "https://pokeapi.co/api/v2/pokemon?offset=0&limit=1351"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return(f"{response.status_code}")
        
    except requests.exceptions.RequestException as e:
        return(f"{e}")

data = get_poke_data()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def poke_info_home():
    search_roots = [BASE_DIR, BASE_DIR.parent]
    for root in search_roots:
        if root.exists():
            matches = list(root.rglob("PokeInfo.html"))
            if matches:
                return FileResponse(matches[0])

    raise HTTPException(
        status_code=500,
        detail=f"PokeInfo.html nicht gefunden. BASE_DIR={BASE_DIR}",
    )

@app.get("/pokemon/")
def empty_poke_info() -> dict:    
    return{"error" : "Name or ID is invalid. Please enter a valid name or ID."}

@app.get("/pokemon/{name_or_id}")
def poke_info(name_or_id: str) -> dict:
    
    global data
    if not isinstance(data, dict):
        data = get_poke_data()
    if not isinstance(data, dict):
        return{"error" : data}
    
    if not name_or_id or not name_or_id.strip():
        return{"error" : "Name or ID is invalid. Please enter a valid name or ID."}
    
    Pokemons = {data["results"][i]["name"] : data["results"][i]["url"] for i in range(len(data["results"]))}
    name_or_id = name_or_id.replace(",", ".")

    if name_or_id.replace(".", "").isnumeric() == True and name_or_id.count(".") <= 1:
        id = float(name_or_id)
        if id < 1 or (id > 1025 and id < 10001) or id > 10326 or int(id) != id:
            return{"error" : "ID is invalid. Please enter a valid name or ID."}
        url2 = f"https://pokeapi.co/api/v2/pokemon/{int(id)}"
    
    else:
        name = name_or_id.lower()
        if not name in Pokemons:
            return{"error" : "Name is invalid. Please enter a valid name or ID."}
        url2 = Pokemons[name]
        
    try:
        response2 = requests.get(url2)
        if response2.status_code == 200:
            data2 = response2.json()
            moves = [i['move']['name'].capitalize() for i in data2['moves']]
            return{"id" : data2['id'], "name" : data2['name'].capitalize(), "height" : data2['height'], "weight": data2['weight'], "moves" : moves}
        else:
            return{"error" : f"{response2.status_code}"}
        
    except requests.exceptions.RequestException as e:
        return{"error" : f"{e}"}