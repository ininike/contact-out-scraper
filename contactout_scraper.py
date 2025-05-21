import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pickle

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

class ContactOutScraper:
    def __init__(self, email: str, password: str):
        """
        Initializes the ContactOutScraper with Selenium WebDriver.
        """
        self.email = email
        self.password = password
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(f"user-agent={USER_AGENT}")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=self.chrome_options)
        
    def __del__(self):
        """
        Ensures the WebDriver is properly closed when the object is deleted.
        """
        self.driver.quit()
        
    
    def search(self, name: str, pages_amount: int = 5) -> list:
        """
        Searches for a given name on the ContactOut website.
        
        Args:
            name (str): The search name.
            
        Returns:
            list: A list of dictionaries containing search result details.
        """
        search_url = f"https://contactout.com/search?login=success"
        try:
            self.driver.get(search_url)
            self._load_cookies()
            self.driver.get(search_url)
            if self.driver.current_url == "https://contactout.com/login":
                self._login()
                self.driver.get(search_url)
            self._run_search(name)
            page_sources = self._get_pages(pages_amount)
            print("Extracting search results...")
            results = [ self._extract_search_results(page) for page in page_sources ]
            results = [ result for sublist in results for result in sublist ]
        except Exception as e:
            print(f"Error occurred: {e}")
            return []
        return results
    
    def _login(self):
        """
        Logs into the ContactOut website using the provided email and password.
        """
        print("Logging in...")
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']"))).send_keys(self.email)
        self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(self.password)
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit)
        pickle.dump( self.driver.get_cookies() , open(f"contactout-{self.email}-cookies.pkl","wb"))
        
    def _load_cookies(self):
        """
        Loads cookies from a file to maintain the session.
        """
        try:
            cookies = pickle.load(open(f"contactout-{self.email}-cookies.pkl", "rb"))
        except FileNotFoundError: 
            self._login()
            return
        for cookie in cookies:
            self.driver.add_cookie(cookie)
            
    def _run_search(self, search_string: str):
        """
        Performs a search on the ContactOut website.
        """
        print("Searching...")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nm']")))
        time.sleep(2)
        search = self.driver.find_element(By.CSS_SELECTOR, "input[name='nm']")
        search.send_keys(search_string)
        search = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", search)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, Selectors.name)))
    
    def _get_pages(self, pages_amount: int):
        """
        Retrieves the specified number of pages from the search results.
        """
        print("scraping pages...")
        pages = []
        for i in range(pages_amount):
            try:
                for button in self.driver.find_elements(By.CSS_SELECTOR, Selectors.load_more):
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                    except Exception as e:
                        continue
                pages.append(self.driver.page_source)
                print(f"Scraped page {i+1}")
                if i < pages_amount - 1:
                    self.driver.find_element(By.CSS_SELECTOR, Selectors.next_page).click()
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, Selectors.result_divs)))
                continue
            except Exception as e:
                print(f"Error occurred while scraping page {i+1}: {e}")
                continue
        print("Finished scraping pages.")
        return pages
    
    def _extract_search_results(self, html: str) -> list:
        """
        Extracts search results from the HTML content.
        """
        soup = BeautifulSoup(html, "html.parser")
        results = [
            {
                "profile_pic": result.select_one(Selectors.profile_pic).get("src") if result.select_one(Selectors.profile_pic) else None,
                "name": result.select_one(Selectors.name).text.strip() if result.select_one(Selectors.name) else None,
                "linkedin_profile_url": result.select_one(Selectors.linkedin_ptofile_url).get("href") if result.select_one(Selectors.linkedin_ptofile_url) else None,
                "github_profile_url": result.select_one(Selectors.github_profile_url).get("href") if result.select_one(Selectors.github_profile_url) else None,
                "twitter_profile_url": result.select_one(Selectors.twitter_profile_url).get("href") if result.select_one(Selectors.twitter_profile_url) else None,
                "facebook_profile_url": result.select_one(Selectors.facebook_profile_url).get("href") if result.select_one(Selectors.facebook_profile_url) else None,
                "location": result.select_one(Selectors.location).text.strip() if result.select_one(Selectors.location) else None,
                "text": ", ".join([ line.text.strip() for line in  soup.select(Selectors.divs_in_result_div)[1:] ]) if result.select_one(Selectors.divs_in_result_div) else None,              
            }
            for result in soup.select("#page-content > div.flex.flex-row.max-sm\:flex-col.h-full.bg-white > div > div.overflow-x-hidden.flex-grow > div.max-sm\:pt-0.min-md\:overflow-y-auto.overflow-x-hidden > div")
        ]
        return results

    
@dataclass(frozen=True)
class Selectors:
    result_divs = ".css-1yxaelb"
    divs_in_result_div = ".css-1yxaelb > div"
    profile_pic = "div.flex.mb-3.items-start > div.flex.align-start.cursor-pointer > img"
    name = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div > div:nth-child(1) > span"
    linkedin_ptofile_url = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div > div:nth-child(1) > div > a:nth-child(1)"
    github_profile_url = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div > div:nth-child(1) > div > a:nth-child(2)"
    twitter_profile_url = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div > div:nth-child(1) > div > a:nth-child(3)"
    facebook_profile_url = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div > div:nth-child(1) > div > a:nth-child(4)"
    location = "div.flex.mb-3.items-start > div.flex.relative.flex-col > div"
    
    next_page = "#page-content > div.flex.flex-row.max-sm\:flex-col.h-full.bg-white > div > div.overflow-x-hidden.flex-grow > div.md\:relative.z-10.flex.justify-center.shadow-inner.bg-white > div > button.w-8.h-8.flex.items-center.justify-center.rounded-r-md.border-t.border-b.border-r.border-solid.border-gray-300.text-sm.space-x-1.hover\:bg-gray-100.hover\:text-gray-500.focus\:outline-none.text-gray-500.css-1d7tuus"
    load_more = "button[aria-label='profile-card-more']"



    

