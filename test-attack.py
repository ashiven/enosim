import jsons
import requests

r = requests.get(f"http://78.47.121.160:5001/scoreboard/attack.json")
print(r.content)
attack_info = jsons.loads(r.content)
first_service = list(attack_info["services"].values())[0]
first_team = list(first_service.values())[0]
prev_round = list(first_team.keys())[0]
current_round = list(first_team.keys())[1]
print(first_service)
print(first_team)
print(prev_round)
print(current_round)
