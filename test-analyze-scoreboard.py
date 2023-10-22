from collections import Counter

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

url = "https://ctftime.org/event/2040"

POINTS_PER_FLAG = 1  # the number of points gained from submitting one flag
PARTICIPATING_TEAMS = 99  # the number of teams participating in the competition
TOTAL_FLAGSTORES = 10  # in enowars7 there were 6 services with a total of 10 flagstores
TOTAL_ROUNDS = 8 * 60  # 8 hours with one round per minute
POINTS_PER_ROUND_PER_FLAGSTORE = PARTICIPATING_TEAMS * POINTS_PER_FLAG


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36"
}
scoreboard = requests.get(url, headers=headers)
soup = BeautifulSoup(scoreboard.content, "html.parser")
points_html = soup.find_all("td", class_="points")

# TODO:
# - this currently only takes into account the total number of points reached by exploiting and defending and sla combined
# - instead, i should do these calculations only with the points gained through attacking
points = [float(p.text) for p in points_html]
highest_score = max(points)


# TODO:
# - these values have to be adjusted in such a way that the second graph models a bell curve
# these percentages were adjusted to model a normal distribution
# they represent the percentage of achieved points compared to the highest score in the competition
NOOB = 0
BEGINNER = 0.22
INTERMEDIATE = 0.35
ADVANCED = 0.52
PROFESSIONAL = 0.73

# these are the average points for each experience level
# they were calculated by taking the average of the lowest and highest score for each experience level
NOOB_AVERAGE_POINTS = (NOOB * highest_score + BEGINNER * highest_score) / 2
BEGINNER_AVERAGE_POINTS = (BEGINNER * highest_score + INTERMEDIATE * highest_score) / 2
INTERMEDIATE_AVERAGE_POINTS = (
    INTERMEDIATE * highest_score + ADVANCED * highest_score
) / 2
ADVANCED_AVERAGE_POINTS = (ADVANCED * highest_score + PROFESSIONAL * highest_score) / 2
PROFESSIONAL_AVERAGE_POINTS = (PROFESSIONAL * highest_score + highest_score) / 2


def points_to_exp(score):
    percent_of_max = score / highest_score
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


plt.plot(list(reversed(distribution.keys())), list(reversed(distribution.values())))
plt.show()


def exploit_probability(points_from_exploiting):
    points_per_flagstore = points_from_exploiting / TOTAL_FLAGSTORES
    rounds_to_reach_points_from_exploiting = (
        points_per_flagstore / POINTS_PER_ROUND_PER_FLAGSTORE
    )
    exploit_probability = rounds_to_reach_points_from_exploiting / TOTAL_ROUNDS
    return exploit_probability * 100


total_teams = len(points)
noob_teams = distribution["NOOB"]
beginner_teams = distribution["BEGINNER"]
intermediate_teams = distribution["INTERMEDIATE"]
advanced_teams = distribution["ADVANCED"]
professional_teams = distribution["PROFESSIONAL"]

print(
    f"{'EXPERIENCE':<15}{'NUMBER OF TEAMS':<25}{'PERCENTAGE':<20}{'EXPLOIT PROBABILITY':<22}{'AVERAGE POINTS':<20}\n"
    + f"Noob              {noob_teams:<20}{100 * (noob_teams/total_teams):>10.2f}%           {exploit_probability(NOOB_AVERAGE_POINTS):>10.2f}%           {NOOB_AVERAGE_POINTS:>10.2f}\n"
    + f"Beginner          {beginner_teams:<20}{100 * (beginner_teams/total_teams):>10.2f}%           {exploit_probability(BEGINNER_AVERAGE_POINTS):>10.2f}%           {BEGINNER_AVERAGE_POINTS:>10.2f}\n"
    + f"Intermediate      {intermediate_teams:<20}{100 * (intermediate_teams/total_teams):>10.2f}%           {exploit_probability(INTERMEDIATE_AVERAGE_POINTS):>10.2f}%           {INTERMEDIATE_AVERAGE_POINTS:>10.2f}\n"
    + f"Advanced          {advanced_teams:<20}{100 * (advanced_teams/total_teams):>10.2f}%           {exploit_probability(ADVANCED_AVERAGE_POINTS):>10.2f}%           {ADVANCED_AVERAGE_POINTS:>10.2f}\n"
    + f"Professional      {professional_teams:<20}{100 * (professional_teams/total_teams):>10.2f}%           {exploit_probability(PROFESSIONAL_AVERAGE_POINTS):>10.2f}%           {PROFESSIONAL_AVERAGE_POINTS:>10.2f}\n"
)
