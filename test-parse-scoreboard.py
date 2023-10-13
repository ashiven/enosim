from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

url = "http://5.75.163.243:5001/scoreboard"

options = Options()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
driver.get(url)


wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "otherrow")))

soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.find_all("tr", class_="otherrow")


team_scores = dict()
for row in rows:
    [points, gain] = row.find("td", class_="team-score").text.strip().split(" ")
    team_name = row.find("div", class_="team-name").find("a").text.strip()
    team_scores[team_name] = (float(points), float(gain[2:-1]))

print(team_scores)
driver.quit()
