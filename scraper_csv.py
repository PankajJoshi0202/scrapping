import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from login import psw
from login import email
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

print("\n")
print("  Initialisation   ")

path_recherche = input("Enter the path link: ")
pays = input("Enter the country: ")

options = webdriver.ChromeOptions()
options.add_argument("--new-window")
options.add_experimental_option("detach", True)

s = Service("D:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=s, options=options)

driver.get(path_recherche)
time.sleep(5)
print("scrapping process: START")
print(" --> Open window")

sign_in = driver.find_element(By.PARTIAL_LINK_TEXT, "Sign in")
sign_in.click()
time.sleep(2)

print("Authentication")

email_login = driver.find_element(By.ID, "username")
email_login.send_keys(email)
time.sleep(2)

password = driver.find_element(By.ID, "password")
password.send_keys(psw)
time.sleep(5)

password.send_keys(Keys.ENTER)
time.sleep(10)

# results_list = driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
try:
    results_list = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
    )
    print("Job search results list found.")
except TimeoutException:
    print("Timeout: Unable to locate the job search results list.")
    driver.quit()
    exit()

nb_page = 4
page_act = 1
total_element = 25

# Create an empty list to store job details
jobs_data = []

n = 1  # Initialize the job counter

while page_act < nb_page:
    print("   page:  ", page_act)
    for i in range(total_element):
        try:
            css_selector = f".jobs-search-two-pane__job-card-container--viewport-tracking-{i}"
            element_to_click = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            try:
                element_to_click.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element_to_click)
            time.sleep(5)

            css_selector_text = f".jobs-search__job-details--container"
            element_to_click = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector_text)))
            title_element = driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title h1.t-24")
            company_element = driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name a")
            description_element = driver.find_element(By.CSS_SELECTOR, "#job-details")

            title = title_element.text
            company = company_element.text
            description = description_element.text

            if title and company and description:
                # Append the job details to the list
                jobs_data.append({
                    'Title': title,
                    'Company': company,
                    'Description': description
                })
                
                print("job -", n, " | ", title[:30])
                print("Company:", company)
                
                driver.execute_script("arguments[0].scrollBy(0,500);", results_list)
                time.sleep(2)
                n += 1
            else:
                print("   SKIP----not complete")
        except NoSuchElementException:
            print("  SKIP--- downloading")

    try:
        xpath_expression = f'//li[@data-test-pagination-page-btn="{page_act + 1}"]'
        next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
        try:
            next_page.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", next_page)
        time.sleep(5)
    except (NoSuchElementException, TimeoutException):
        try:
            xpath_expression2 = f'//button[@aria-label="Page {page_act + 1}"]'
            next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_expression2)))
            try:
                next_page.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", next_page)
                time.sleep(5)
        except (NoSuchElementException, TimeoutException):
            print(f"The page {page_act + 1} is missing !!!")
            break
    page_act += 1

# Step to save job data to CSV file
df = pd.DataFrame(jobs_data)
csv_file = f"jobs_data_{pays}.csv"
df.to_csv(csv_file, index=False)
print(f"Data successfully saved to {csv_file}")
