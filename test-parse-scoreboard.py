from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

url = "http://5.75.163.243:5001/scoreboard"
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)


wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "otherrow")))

soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.find_all("td", class_="otherrow")

print(rows)

for row in rows:
    score = row.find("td", class_="team-score").text.strip()
    team_name = row.find("div", class_="team-name").find("a").text.strip()
    print(score, team_name)

driver.quit()
