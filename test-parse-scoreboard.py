from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

url = "http://5.75.163.243:5001/scoreboard"

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(url)


wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "otherrow")))

soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.find_all("tr", class_="otherrow")

for row in rows:
    [score, gain] = row.find("td", class_="team-score").text.strip().split(" ")
    team_name = row.find("div", class_="team-name").find("a").text.strip()
    print(team_name, score, gain[2:-1])

driver.quit()
