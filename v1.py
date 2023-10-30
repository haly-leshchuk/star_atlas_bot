# Automated bot for Star Atlas game to mine the game currency units

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


def print_sorted_fleet_array(sorted_fleet_array):
    for fleet_name, fleet_button, chances, timestamp in sorted_fleet_array:
        collected_sdus_var = (' | Collected SDUs at: {}'.format(timestamp)) if timestamp else ''
        print(fleet_name, ' | Chances: {}% '.format(chances), collected_sdus_var)
    return print('\n')


def collect_response(fleet, sorted_fleet_array):

    wait = WebDriverWait(driver, 10)
    sdu_mining_reaction = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-gkSfol cgLkbv']")))

    fleet[2] = 0

    percentage_str = re.findall(r'\d+\.\d+%', sdu_mining_reaction.text)
    if percentage_str:
        fleet[2] = float(percentage_str[0][:-1])

    print('Percentage received: ', fleet[2])

    fleet[3] = time.time() if ['SUCCESS'] in sdu_mining_reaction.text.split() else None

    print('SDUs found: ', bool(fleet[3]))
    print('\n')


def close_popup():
    close_button = driver.find_element(By.XPATH, "//button[@class='sc-ipEyDJ ehasQg']")
    close_button.click()


def scan(x, y, sorted_fleet_array):

    for i in range(y):

        print('Cycle {}. Order by chance %: '.format(i))
        print_sorted_fleet_array(sorted_fleet_array)

        # Every round wait for 1 min
        for fleet in sorted_fleet_array:

            # We skip the ships which mined SDUs X seconds before
            if fleet[3] is not None:
                if time.time() - fleet[3] < x:
                    continue

            fleet[1].click()

            print('Starting collect response for', fleet[0])

            try:
                collect_response(fleet, sorted_fleet_array)
            except:
                print('No response received. Skipping this cycle.')
                continue

            time.sleep(3)
            close_popup()

            time.sleep(5)

        sorted_fleet_array = list(reversed(sorted(sorted_fleet_array, key=lambda x: x[2])))

        print('Cycle end. Going to sleep for 1 min.')
        print('\n')
        time.sleep(60)


# Set Chrome options to connect to an existing browser instance
options = Options()
options.debugger_address = "127.0.0.1:9222"

# Create a new ChromeDriver instance using the options
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Locate the button START SCAN for all fleets
chipmunk_fleet_button = driver.find_element(By.XPATH, "//button[@class='sc-ipEyDJ fpplsb'][ancestor::tr[@role='row'][child::td[@role='cell'][text()='Chipmunk Fleet']]]")
bustard_fleet_button = driver.find_element(By.XPATH, "//button[@class='sc-ipEyDJ fpplsb'][ancestor::tr[@role='row'][child::td[@role='cell'][text()='Bustard Fleet']]]")


# Create an array of all fleets
all_fleet_array = [
    ['Chipmunk Fleet', chipmunk_fleet_button, 0, None],
    ['Bustard Fleet', bustard_fleet_button, 0, None]
]

sorted_fleet_array = sorted(all_fleet_array, key=lambda x: x[2])

# x - number in SECONDS how much time to wait before clicking on a button after SDUs are mined
# y - custom number of cycles
scan(20, 3, sorted_fleet_array)
