from collections import deque
import time

config_json = {
  "spec_version": "1.0",
  "challenge_id": "vet_room_protocol_demo_v3_mixed_arrivals",
  "metadata": {
    "room_count": 1,
    "allowed_states": ["EMPTY", "DOGS", "CATS"],
    "queue_policy": "FIFO",
    "sign_change_latency": 0,
    "tie_breaker": ["arrival_time", "id"]
  },
  "room": {
    "initial_sign_state": "EMPTY"
  },
  "workload": {
    "time_unit": "ticks",
    "animals": [
      { "id": "D01", "species": "DOG", "arrival_time": 0,  "rest_duration": 6 },
      { "id": "D02", "species": "DOG", "arrival_time": 1,  "rest_duration": 5 },
      { "id": "D03", "species": "DOG", "arrival_time": 2,  "rest_duration": 7 },
      { "id": "D04", "species": "DOG", "arrival_time": 3,  "rest_duration": 4 },
      { "id": "C01", "species": "CAT", "arrival_time": 5,  "rest_duration": 6 },
      { "id": "C02", "species": "CAT", "arrival_time": 8,  "rest_duration": 3 },
      { "id": "C03", "species": "CAT", "arrival_time": 8,  "rest_duration": 5 },
      { "id": "D05", "species": "DOG", "arrival_time": 10, "rest_duration": 8 },
      { "id": "D06", "species": "DOG", "arrival_time": 11, "rest_duration": 4 },
      { "id": "D07", "species": "DOG", "arrival_time": 15, "rest_duration": 6 },
      { "id": "D08", "species": "DOG", "arrival_time": 15, "rest_duration": 3 },
      { "id": "C04", "species": "CAT", "arrival_time": 18, "rest_duration": 4 },
      { "id": "C05", "species": "CAT", "arrival_time": 20, "rest_duration": 7 },
      { "id": "C06", "species": "CAT", "arrival_time": 20, "rest_duration": 2 },
      { "id": "D09", "species": "DOG", "arrival_time": 22, "rest_duration": 5 },
      { "id": "C07", "species": "CAT", "arrival_time": 25, "rest_duration": 5 },
      { "id": "C08", "species": "CAT", "arrival_time": 25, "rest_duration": 6 },
      { "id": "C09", "species": "CAT", "arrival_time": 25, "rest_duration": 4 },
      { "id": "D10", "species": "DOG", "arrival_time": 26, "rest_duration": 9 },
      { "id": "D11", "species": "DOG", "arrival_time": 30, "rest_duration": 5 },
      { "id": "D12", "species": "DOG", "arrival_time": 31, "rest_duration": 4 },
      { "id": "D13", "species": "DOG", "arrival_time": 32, "rest_duration": 3 },
      { "id": "C10", "species": "CAT", "arrival_time": 35, "rest_duration": 8 },
      { "id": "C11", "species": "CAT", "arrival_time": 40, "rest_duration": 3 },
      { "id": "C12", "species": "CAT", "arrival_time": 40, "rest_duration": 5 },
      { "id": "D14", "species": "DOG", "arrival_time": 41, "rest_duration": 7 },
      { "id": "D15", "species": "DOG", "arrival_time": 55, "rest_duration": 4 },
      { "id": "D16", "species": "DOG", "arrival_time": 55, "rest_duration": 6 },
      { "id": "C13", "species": "CAT", "arrival_time": 60, "rest_duration": 7 },
      { "id": "C14", "species": "CAT", "arrival_time": 60, "rest_duration": 3 },
      { "id": "D17", "species": "DOG", "arrival_time": 68, "rest_duration": 5 }
    ]
  }
}

animals = config_json["workload"]["animals"]
animals.sort(key=lambda x: (x["arrival_time"], x["id"]))

queue_dogs = deque()
queue_cats = deque()
room = []
sign_state = config_json["room"]["initial_sign_state"]
tick = 0
consecutive_species = None
consecutive_count = 0
index = 0
MAX_CONSECUTIVOS = 3

print(f"{'TICK':<6} {'STATE':<8} {'ROOM':<40} {'DOGS_QUEUE':<25} {'CATS_QUEUE':<25}")
print("-" * 110)

while True:
    while index < len(animals) and animals[index]["arrival_time"] == tick:
        a = animals[index]
        if a["species"] == "DOG":
            queue_dogs.append(a.copy())
        else:
            queue_cats.append(a.copy())
        index += 1

    for a in room:
        a["rest_duration"] -= 1
    room = [a for a in room if a["rest_duration"] > 0]

    if not room:
        sign_state = "EMPTY"
        consecutive_count = 0

        if queue_dogs and queue_cats:
            if consecutive_species == "DOG":
                sign_state = "CATS"
                consecutive_species = "CAT"
            else:
                sign_state = "DOGS"
                consecutive_species = "DOG"
        elif queue_dogs:
            sign_state = "DOGS"
            consecutive_species = "DOG"
        elif queue_cats:
            sign_state = "CATS"
            consecutive_species = "CAT"

    if sign_state == "DOGS":
        while queue_dogs and consecutive_count < MAX_CONSECUTIVOS:
            room.append(queue_dogs.popleft())
            consecutive_count += 1
    elif sign_state == "CATS":
        while queue_cats and consecutive_count < MAX_CONSECUTIVOS:
            room.append(queue_cats.popleft())
            consecutive_count += 1

    print(f"{tick:<6} {sign_state:<8} {', '.join([a['id'] for a in room]):<40} "
          f"{', '.join([a['id'] for a in queue_dogs]):<25} {', '.join([a['id'] for a in queue_cats]):<25}")

    if not room and not queue_dogs and not queue_cats and index >= len(animals):
        break

    tick += 1
    time.sleep(0.5)