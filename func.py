import json

def save_tasks(users):
  with open("users.json", "w") as file:
    json.dump(users, file)

def read_tasks():
  try:
    with open("users.json", "r") as file:
      users = json.load(file)
    return users
  except FileNotFoundError:
    return {}