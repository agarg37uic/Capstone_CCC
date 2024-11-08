import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os

# Path to Brave browser
brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

def scrape_pw_trader(query="jetski", record_limit=20):
    """Scrape PWC Trader listings using Brave browser via Selenium."""
    url = f"https://www.pwctrader.com/pwcs-for-sale?keyword={query}"
    
    # Setup Brave options
    options = webdriver.ChromeOptions()
    options.binary_location = brave_path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Load the page
    driver.get(url)
    time.sleep(5)  # Allow time for initial load

    # Scroll to the bottom of the page to trigger lazy-loading of listings
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for new elements to load

    # Parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Extract listings
    listings = []
    listing_elements = soup.select(".search-card") or soup.select(".listing-item") or soup.select(".result-item")

    if not listing_elements:
        print("No listings found. Please inspect page structure further.")
        return None

    for listing in listing_elements[:record_limit]:
        title = listing.select_one(".title-wrapper").get_text(strip=True) if listing.select_one(".title-wrapper") else "N/A"
        price = listing.select_one(".price").get_text(strip=True) if listing.select_one(".price") else "N/A"
        location = listing.select_one(".location-wrapper").get_text(strip=True) if listing.select_one(".location-wrapper") else "N/A"
        engine_hours = listing.select_one(".mileage-wrapper").get_text(strip=True) if listing.select_one(".mileage-wrapper") else "N/A"
        
        listings.append({
            "Title": title,
            "Engine Hours": engine_hours,
            "Location": location,
            "Price": price
        })

    # Save data as DataFrame and CSV
    df_listings = pd.DataFrame(listings)
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_csv = os.path.join(desktop_path, "scraped_data_top20.csv")
    df_listings.to_csv(output_csv, index=False)
    print(f"CSV saved to {output_csv}")
    return df_listings

# Run the function
df = scrape_pw_trader(query="jetski", record_limit=20)
print("Scraping complete:", df)
