from collections import Counter

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

url = "https://ctftime.org/event/2040"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36"
}
scoreboard = requests.get(url, headers=headers)
soup = BeautifulSoup(scoreboard.content, "html.parser")
points_html = soup.find_all("td", class_="points")
points = [float(p.text) for p in points_html]


# these percentages were adjusted to model a normal distribution
# they represent the percentage of achieved points compared to the highest score in the competition
NOOB = 0
BEGINNER = 0.22
INTERMEDIATE = 0.35
ADVANCED = 0.52
PROFESSIONAL = 0.73


best = max(points)


def points_to_exp(score):
    percent_of_max = score / best
    exp = "NOOB"
    if percent_of_max > BEGINNER:
        exp = "BEGINNER"
    if percent_of_max > INTERMEDIATE:
        exp = "INTERMEDIATE"
    if percent_of_max > ADVANCED:
        exp = "ADVANCED"
    if percent_of_max > PROFESSIONAL:
        exp = "PROFESSIONAL"
    return exp


distribution = Counter([points_to_exp(p) for p in points])

plt.plot(points)
plt.show()

total_teams = len(points)
noob_teams = distribution["NOOB"]
beginner_teams = distribution["BEGINNER"]
intermediate_teams = distribution["INTERMEDIATE"]
advanced_teams = distribution["ADVANCED"]
professional_teams = distribution["PROFESSIONAL"]

print(
    f"Total teams: {total_teams}\n"
    + f"Noob Teams: {noob_teams} ({100 * (noob_teams/total_teams):.2f}%)\n"
    + f"Beginner Teams: {beginner_teams} ({100 * (beginner_teams/total_teams):.2f}%)\n"
    + f"Intermediate Teams: {intermediate_teams} ({100 * (intermediate_teams/total_teams):.2f}%)\n"
    + f"Advanced Teams: {advanced_teams} ({100 * (advanced_teams/total_teams):.2f}%)\n"
    + f"Professional Teams: {professional_teams} ({100 * (professional_teams/total_teams):.2f}%)"
)
plt.plot(list(reversed(distribution.keys())), list(reversed(distribution.values())))
plt.show()
