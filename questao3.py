import json
from collections import deque

config_json = {
    "specversion": "1.0",
    "challengeid": "vetroomprotocoldemo",
    "metadata": {
        "room_count": 1,
        "allowed_states": ["EMPTY", "DOGS", "CATS"],
        "queue_policy": "FIFO",
        "sign_change_latency": 0,
        "tiebreaker": ["arrival_time", "id"],
    },
    "room": {
        "initial_signstate": "EMPTY"
    },
    "workload": {
        "time_unit": "ticks",
        "animals": [
            {"id": "D01", "species": "DOG", "arrival_time": 0, "rest_duration": 5},
            {"id": "C01", "species": "CAT", "arrival_time": 1, "rest_duration": 4},
            {"id": "D02", "species": "DOG", "arrival_time": 2, "rest_duration": 6},
            {"id": "C02", "species": "CAT", "arrival_time": 3, "rest_duration": 2},
            {"id": "D03", "species": "DOG", "arrival_time": 4, "rest_duration": 3}
        ]
    }
}

MAX_CONSECUTIVOS = 3  
fila_dogs = deque()
fila_cats = deque()
sala_estado = config_json["room"]["initial_signstate"]
consecutivos = 0
animais_em_atendimento = []

animais = sorted(config_json["workload"]["animals"], key=lambda x: (x["arrival_time"], x["id"]))

tempo = 0

while fila_dogs or fila_cats or animais or animais_em_atendimento:
    print(f"Tempo {tempo}:")

    while animais and animais[0]["arrival_time"] == tempo:
        animal = animais.pop(0)
        fila = fila_dogs if animal["species"] == "DOG" else fila_cats
        fila.append({
            "id": animal["id"],
            "species": animal["species"],
            "rest": animal["rest_duration"]
        })
        print(f"  Chegou: {animal['species']} {animal['id']} -> fila de {animal['species'].lower()}s")

    novos_em_atendimento = []
    for a in animais_em_atendimento:
        a["rest"] -= 1
        if a["rest"] <= 0:
            print(f"  >>> Atendimento finalizado: {a['species']} {a['id']}")
            consecutivos -= 1
        else:
            novos_em_atendimento.append(a)
    animais_em_atendimento = novos_em_atendimento

    if sala_estado == "EMPTY":
        if fila_dogs:
            sala_estado = "DOGS"
            consecutivos = 0
        elif fila_cats:
            sala_estado = "CATS"
            consecutivos = 0

    if sala_estado == "DOGS":
        while fila_dogs and consecutivos < MAX_CONSECUTIVOS:
            a = fila_dogs.popleft()
            animais_em_atendimento.append(a)
            consecutivos += 1
    elif sala_estado == "CATS":
        while fila_cats and consecutivos < MAX_CONSECUTIVOS:
            a = fila_cats.popleft()
            animais_em_atendimento.append(a)
            consecutivos += 1

    if not animais_em_atendimento:
        sala_estado = "EMPTY"
        consecutivos = 0

    print(f"  Sala: {sala_estado}")
    print(f"  Fila cães: {[d['id'] for d in fila_dogs]}")
    print(f"  Fila gatos: {[c['id'] for c in fila_cats]}")
    print(f"  Em atendimento: {[a['id'] for a in animais_em_atendimento]}")
    print("--------------------")
    
    tempo += 1