import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

service = Service(r"C:\Users\HP\Desktop\selenium prj\chromedriver-win64\chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument('--lang=fr')
chrome_options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(60)

base_urls = [
    "https://www.mubawab.ma/fr/st/casablanca/appartements-a-vendre",
    "https://www.mubawab.ma/fr/st/casablanca/appartements-a-vendre:p:2"
]

results = []
all_links = set()

for base_url in base_urls:
    print(f"\nLoading page: {base_url}")
    driver.get(base_url)
    time.sleep(2)

    # Scroll to bottom to load all listings
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)  # Wait for AJAX

    # Collect all <a> elements with href containing '/pa/'
    a_tags = driver.find_elements(By.TAG_NAME, "a")
    page_links = set()
    for a in a_tags:
        href = a.get_attribute("href")
        if href and "/pa/" in href:
            page_links.add(href)

    print(f"Found {len(page_links)} listing hrefs on {base_url}")
    all_links.update(page_links)

print(f"\nTotal unique listing hrefs collected: {len(all_links)}")

# Step 2: Loop over each unique link and scrape details
for idx, link in enumerate(all_links):
    print(f"\nScraping detail page {idx+1}: {link}")
    driver.get(link)
    time.sleep(2)

    # Try to close cookie warning if present
    try:
        cookie_btn = driver.find_element(By.CSS_SELECTOR, ".cookieWarning button, .cookieWarning .close")
        cookie_btn.click()
        time.sleep(1)
    except Exception:
        pass

    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(2)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except Exception as e:
        print(f"Name not found: {e}")
        name = "N/A"

    try:
        location = driver.find_element(By.CSS_SELECTOR, "h3.greyTit").text.strip()
    except Exception as e:
        print(f"Location not found: {e}")
        location = "N/A"

    try:
        price = driver.find_element(By.CSS_SELECTOR, "h3.orangeTit").text.strip()
    except Exception as e:
        print(f"Price not found: {e}")
        price = "N/A"

    superficie = "N/A"
    try:
        ad_details = driver.find_element(By.CSS_SELECTOR, "div.disFlex.adDetails")
        spans = ad_details.find_elements(By.TAG_NAME, "span")
        for span in spans:
            text = span.text.strip()
            if "m²" in text:
                superficie = text
                break
    except Exception as e:
        print(f"Superficie not found: {e}")

    main_features = {}
    main_feature_boxes = driver.find_elements(By.CSS_SELECTOR, "div.adMainFeature")
    for box in main_feature_boxes:
        try:
            label = box.find_element(By.CSS_SELECTOR, ".adMainFeatureContentLabel").text.strip()
            value = box.find_element(By.CSS_SELECTOR, ".adMainFeatureContentValue").text.strip()
            main_features[label] = value
        except Exception:
            continue

    additional_features = []
    feature_boxes = driver.find_elements(By.CSS_SELECTOR, "div.adFeature")
    for box in feature_boxes:
        try:
            feature = box.find_element(By.CSS_SELECTOR, "span.fSize11.centered").text.strip()
            additional_features.append(feature)
        except Exception:
            continue

    result = {
        "Name": name,
        "Location": location,
        "Price": price,
        "Superficie": superficie,
        **main_features
    }
    for feature in additional_features:
        result[feature] = "Oui"

    results.append(result)
    print(f"Appended result for: {name}")

# Save to Excel
output_path = os.path.join("data", "real_estate_casa_detail.xlsx")
df = pd.DataFrame(results)
df.to_excel(output_path, index=False)
print(f"\nSaved details for {len(results)} unique listings to {output_path}")

driver.quit()

# Read the HTML from the file
with open('outer html.txt', 'r', encoding='utf-8') as file:
    html = file.read()

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Extract all hrefs from <a> tags
hrefs = [a.get('href') for a in soup.find_all('a') if a.get('href')]

# Print or save the results
for href in hrefs:
    print(href)