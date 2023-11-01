import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from scipy.stats import norm

url = "https://ctftime.org/event/2040"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36"
}
scoreboard = requests.get(url, headers=headers)
soup = BeautifulSoup(scoreboard.content, "html.parser")
points_html = soup.find_all("td", class_="points")
points = [float(p.text) for p in points_html]


# If a json scoreboard file exists, it takes precedence over the ctftime scoreboard
json_path = "C:/Users/janni/Downloads/scoreboard_enowars7/scoreboard478.json"
if os.path.exists(json_path):
    print("Using local scoreboard\n")
    with open(json_path, "r") as f:
        data = json.load(f)

teams = data["teams"]
attack_points = dict()

for team in teams:
    team_name = team["teamName"]
    team_attack_points = team["attackScore"]
    attack_points[team_name] = team_attack_points

points = sorted([float(p) for p in list(attack_points.values())])


MEAN = sum(points) / len(points)
STANDARD_DEVIATION = (sum([(p - MEAN) ** 2 for p in points]) / len(points)) ** 0.5


plt.hist(points, bins=100)
plt.title("Attack points distribution")
plt.show()

print(f"Normal Distribution:\nStandard deviation: {STANDARD_DEVIATION}\nMean: {MEAN}\n")

plt.plot(points, norm.pdf(points, MEAN, STANDARD_DEVIATION))
plt.title("Attempting to fit a normal distribution")
plt.show()

POINTS_PER_FLAG = 1
PARTICIPATING_TEAMS = len(points)
TOTAL_FLAGSTORES = 10  # in enowars7 there were 6 services with a total of 10 flagstores
TOTAL_ROUNDS = 8 * 60  # 8 hours with one round per minute
POINTS_PER_ROUND_PER_FLAGSTORE = (PARTICIPATING_TEAMS - 1) * POINTS_PER_FLAG
HIGH_SCORE = points[-1]

# these values represent the percentage of achieved points compared to the mean score of all teams
NOOB_AVERAGE_POINTS_NORM = max(
    (MEAN - 3 * STANDARD_DEVIATION + MEAN - 2 * STANDARD_DEVIATION) / 2, 0
)
BEGINNER_AVERAGE_POINTS_NORM = max(
    (MEAN - 2 * STANDARD_DEVIATION + MEAN - 1 * STANDARD_DEVIATION) / 2, 0
)
INTERMEDIATE_AVERAGE_POINTS_NORM = max(
    (MEAN - 1 * STANDARD_DEVIATION + MEAN + 1 * STANDARD_DEVIATION) / 2, 0
)
ADVANCED_AVERAGE_POINTS_NORM = max(
    (MEAN + 1 * STANDARD_DEVIATION + MEAN + 2 * STANDARD_DEVIATION) / 2, 0
)
PROFESSIONAL_AVERAGE_POINTS_NORM = max(
    (MEAN + 3 * STANDARD_DEVIATION + MEAN + 2 * STANDARD_DEVIATION) / 2, 0
)


NOOB_AVERAGE_POINTS = max((0 * HIGH_SCORE + 0.2 * HIGH_SCORE) / 2, 0)
BEGINNER_AVERAGE_POINTS = max((0.2 * HIGH_SCORE + 0.4 * HIGH_SCORE) / 2, 0)
INTERMEDIATE_AVERAGE_POINTS = max((0.4 * HIGH_SCORE + 0.6 * HIGH_SCORE) / 2, 0)
ADVANCED_AVERAGE_POINTS = max((0.6 * HIGH_SCORE + 0.8 * HIGH_SCORE) / 2, 0)
PROFESSIONAL_AVERAGE_POINTS = max((0.8 * HIGH_SCORE + 1 * HIGH_SCORE) / 2, 0)


def points_to_exp_normal_dist(score):
    exp = "NOOB"
    if MEAN - 2 * STANDARD_DEVIATION < score <= MEAN - 1 * STANDARD_DEVIATION:
        exp = "BEGINNER"
    elif MEAN - 1 * STANDARD_DEVIATION < score <= MEAN + 1 * STANDARD_DEVIATION:
        exp = "INTERMEDIATE"
    elif MEAN + 1 * STANDARD_DEVIATION < score <= MEAN + 2 * STANDARD_DEVIATION:
        exp = "ADVANCED"
    elif MEAN + 2 * STANDARD_DEVIATION < score:
        exp = "PROFESSIONAL"
    return exp


def points_to_exp_percent_max(score):
    exp = "NOOB"
    if 0.2 * HIGH_SCORE < score <= 0.4 * HIGH_SCORE:
        exp = "BEGINNER"
    elif 0.4 * HIGH_SCORE < score <= 0.6 * HIGH_SCORE:
        exp = "INTERMEDIATE"
    elif 0.6 * HIGH_SCORE < score <= 0.8 * HIGH_SCORE:
        exp = "ADVANCED"
    elif 0.8 * HIGH_SCORE < score:
        exp = "PROFESSIONAL"
    return exp


team_distribution_normal = Counter([points_to_exp_normal_dist(p) for p in points])
team_distribution_percent_max = Counter([points_to_exp_percent_max(p) for p in points])

total_teams = len(points)

noob_teams_normal = team_distribution_normal["NOOB"]
beginner_teams_normal = team_distribution_normal["BEGINNER"]
intermediate_teams_normal = team_distribution_normal["INTERMEDIATE"]
advanced_teams_normal = team_distribution_normal["ADVANCED"]
professional_teams_normal = team_distribution_normal["PROFESSIONAL"]

noob_teams_percent_max = team_distribution_percent_max["NOOB"]
beginner_teams_percent_max = team_distribution_percent_max["BEGINNER"]
intermediate_teams_percent_max = team_distribution_percent_max["INTERMEDIATE"]
advanced_teams_percent_max = team_distribution_percent_max["ADVANCED"]
professional_teams_percent_max = team_distribution_percent_max["PROFESSIONAL"]


def exploit_probability(points_from_exploiting):
    points_per_flagstore = points_from_exploiting / TOTAL_FLAGSTORES
    rounds_to_reach_points_from_exploiting = (
        points_per_flagstore / POINTS_PER_ROUND_PER_FLAGSTORE
    )
    exploit_probability = rounds_to_reach_points_from_exploiting / TOTAL_ROUNDS
    return exploit_probability * 100


print("Normal distribution:")
print(
    f"{'EXPERIENCE':<15}{'NUMBER OF TEAMS':<25}{'PERCENTAGE':<20}{'EXPLOIT PROBABILITY':<22}{'AVERAGE POINTS':<20}\n"
    + f"Noob              {noob_teams_normal:<20}{100 * (noob_teams_normal/total_teams):>10.2f}%           {exploit_probability(NOOB_AVERAGE_POINTS_NORM):>10.2f}%           {NOOB_AVERAGE_POINTS_NORM:>10.2f}\n"
    + f"Beginner          {beginner_teams_normal:<20}{100 * (beginner_teams_normal/total_teams):>10.2f}%           {exploit_probability(BEGINNER_AVERAGE_POINTS_NORM):>10.2f}%           {BEGINNER_AVERAGE_POINTS_NORM:>10.2f}\n"
    + f"Intermediate      {intermediate_teams_normal:<20}{100 * (intermediate_teams_normal/total_teams):>10.2f}%           {exploit_probability(INTERMEDIATE_AVERAGE_POINTS_NORM):>10.2f}%           {INTERMEDIATE_AVERAGE_POINTS_NORM:>10.2f}\n"
    + f"Advanced          {advanced_teams_normal:<20}{100 * (advanced_teams_normal/total_teams):>10.2f}%           {exploit_probability(ADVANCED_AVERAGE_POINTS_NORM):>10.2f}%           {ADVANCED_AVERAGE_POINTS_NORM:>10.2f}\n"
    + f"Professional      {professional_teams_normal:<20}{100 * (professional_teams_normal/total_teams):>10.2f}%           {exploit_probability(PROFESSIONAL_AVERAGE_POINTS_NORM):>10.2f}%           {PROFESSIONAL_AVERAGE_POINTS_NORM:>10.2f}\n"
)

print("Percent max distribution:")
print(
    f"{'EXPERIENCE':<15}{'NUMBER OF TEAMS':<25}{'PERCENTAGE':<20}{'EXPLOIT PROBABILITY':<22}{'AVERAGE POINTS':<20}\n"
    + f"Noob              {noob_teams_percent_max:<20}{100 * (noob_teams_percent_max/total_teams):>10.2f}%           {exploit_probability(NOOB_AVERAGE_POINTS):>10.2f}%           {NOOB_AVERAGE_POINTS:>10.2f}\n"
    + f"Beginner          {beginner_teams_percent_max:<20}{100 * (beginner_teams_percent_max/total_teams):>10.2f}%           {exploit_probability(BEGINNER_AVERAGE_POINTS):>10.2f}%           {BEGINNER_AVERAGE_POINTS:>10.2f}\n"
    + f"Intermediate      {intermediate_teams_percent_max:<20}{100 * (intermediate_teams_percent_max/total_teams):>10.2f}%           {exploit_probability(INTERMEDIATE_AVERAGE_POINTS):>10.2f}%           {INTERMEDIATE_AVERAGE_POINTS:>10.2f}\n"
    + f"Advanced          {advanced_teams_percent_max:<20}{100 * (advanced_teams_percent_max/total_teams):>10.2f}%           {exploit_probability(ADVANCED_AVERAGE_POINTS):>10.2f}%           {ADVANCED_AVERAGE_POINTS:>10.2f}\n"
    + f"Professional      {professional_teams_percent_max:<20}{100 * (professional_teams_percent_max/total_teams):>10.2f}%           {exploit_probability(PROFESSIONAL_AVERAGE_POINTS):>10.2f}%           {PROFESSIONAL_AVERAGE_POINTS:>10.2f}\n"
)
