import threading
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from itertools import product

# Path to the geckodriver executable
geckodriver_path = "./geckodriver.exe"

# Semaphore to limit the number of concurrent threads
max_threads = 5
semaphore = threading.Semaphore(max_threads)

# Queue to hold the listings
listings_queue = Queue()

def scrape_job_listings(search_query, location, radius, num_pages):
    listings = [] # List to store job information
    options = Options() # Set up the Firefox options
    options.add_argument("--headless") # Run Firefox in headless mode to avoid opening a browser window for better performance
    service = FirefoxService(executable_path=geckodriver_path) # Set up the geckodriver service
    driver = webdriver.Firefox(service=service, options=options) # Initialize the Firefox driver 
    
    visited_urls = set()

    for page in range(num_pages):
        # Construct the URL for the search query and page number
        url = f"https://ca.indeed.com/jobs?q={search_query}&l={location}&radius={radius}&start={page * 10}"
        
        # Check if the URL has already been visited
        if url in visited_urls:
            print(f"Skipping already visited page: {url}")
            continue

        # Add the URL to the set of visited URLs
        visited_urls.add(url)

        driver.get(url)

        # Wait for the job cards to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.job_seen_beacon'))
            )
        except Exception as e:
            print(f"Error waiting for job cards to load: {e}")
            continue

        # Extract job information from each job card
        job_cards = driver.find_elements(By.CSS_SELECTOR, '.job_seen_beacon')
        print(f"Found {len(job_cards)} job cards for '{search_query}' on page {page + 1}")

        # Loop through each job card and extract the job information
        for job_card in job_cards:
            try:
                job_url = job_card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                # Click on the job card to view the job listing details
                job_card.click()
                time.sleep(3)  # Adding a delay to ensure the page loads completely

                # Extracting information from the job listing
                job_title = driver.find_element(By.CSS_SELECTOR, 'h2.jobsearch-JobInfoHeader-title').text
                company_name = driver.find_element(By.CSS_SELECTOR, '.css-hon9z8').text
                company_rating = driver.find_element(By.CSS_SELECTOR, '.css-ppxtlp').text.split()[0]
                company_location = driver.find_element(By.CSS_SELECTOR, '.css-waniwe').text
                job_info_text = driver.find_element(By.ID, 'jobDescriptionText').text
                
                # Storing job information
                job_info = {
                    'Title': job_title,
                    'Company': company_name,
                    'Rating': company_rating,
                    'Location': company_location,
                    'Description': job_info_text,
                    'URL': job_url
                }
                listings.append(job_info)
            except Exception as e:
                print(f"Error extracting job information: {e}")

    # Close the browser
    driver.quit()
    
    # Add listings to the queue
    listings_queue.put(listings)

    # Release the semaphore
    semaphore.release()

def threaded_scrape(keywords1, keywords2, location, radius, num_pages):
    # Generate all combinations of keywords1 and keywords2
    search_queries = [' '.join([k1, k2]) for k1, k2 in product(keywords1, keywords2)]

    threads = []
    for search_query in search_queries:
        semaphore.acquire()  # Acquire a semaphore before starting a new thread
        thread = threading.Thread(target=scrape_job_listings, args=(search_query, location, radius, num_pages))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Gather all listings from the queue
    all_listings = []
    while not listings_queue.empty():
        all_listings.extend(listings_queue.get())

    # Save the job listings to an Excel file 
    df = pd.DataFrame(all_listings)
    output_path = "job_listings.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Job listings saved to {output_path}")

# Define your lists of keywords
keywords1 = ['Entry level ', 'Junior ', 'Graduate ', 'Intern ', 'Internship ', 'Co-op '] 
keywords2 = ['Data Analyst', 'Software Engineer', 'Software Developer', 'developer', 'Web Developer', 'back end', 'front end']

# Specify the location and radius
location = "Peterborough"  # City or location
radius = 100  # Radius in kilometers
num_pages = 5  # Number of pages to scrape per search query

# Call the function with the lists of keywords
threaded_scrape(keywords1, keywords2, location, radius, num_pages)
