from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def scrape_indeed(job_title, location, num_pages=1):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in the background
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = f"https://in.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+')}"

    jobs = []

    for page in range(num_pages):
        url = f"{base_url}&start={page * 10}"
        driver.get(url)
        print(f"Scraping: {driver.current_url}")  # Verify correct URL
        time.sleep(5)  # Allow page to load

        try:
            job_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))  # Updated class
            )
        except:
            print("No job postings found.")
            continue

        for job in job_cards:
            try:
                title = job.find_element(By.CSS_SELECTOR, "h2 a").text.strip()
                company = job.find_element(By.CLASS_NAME, "companyName").text.strip()
                location = job.find_element(By.CLASS_NAME, "companyLocation").text.strip()
                job_link = job.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")

                jobs.append({"Title": title, "Company": company, "Location": location, "Link": job_link})
            except:
                continue

        print(f"Scraped {len(jobs)} jobs from page {page + 1}")

    driver.quit()

    df = pd.DataFrame(jobs)
    df.to_csv("indeed_jobs.csv", index=False)
    print("Scraping completed, data saved to indeed_jobs.csv")

scrape_indeed("data analyst", "remote", num_pages=2)
