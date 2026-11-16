import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/pokemon/{name_or_id}")
def poke_info(name_or_id: str) -> dict:
    if not isinstance(data, dict):
        return {"error" : data}
    
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
        
    response2 = requests.get(url2)
    data2 = response2.json()
    moves = [i['move']['name'].capitalize() for i in data2['moves']]
    
    return({"id" : data2['id'], "name" : data2['name'].capitalize(), "height" : data2['height'], "weight": data2['weight'], "moves" : moves})