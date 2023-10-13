import requests
from bs4 import BeautifulSoup

url = "http://5.75.163.243:5001/scoreboard"
r = requests.get(url)
print(r.text)
soup = BeautifulSoup(r.text, "html.parser")
print(soup)

rows = soup.find_all("td", class_="otherrow")

for row in rows:
    score = row.find("td", class_="team-score").text.strip()
    team_name = row.find("div", class_="team-name").find("a").text.strip()
    print(score, team_name)
