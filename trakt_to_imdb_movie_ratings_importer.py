"""
IMDb Ratings Importer from Trakt
Automatically adds ratings from your Trakt export to IMDb
"""

import json
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
LOGIN_TIME_SECONDS = 60


class IMDbRatingsImporter:
    def __init__(self, json_file_path, progress_file='imdb_import_progress.json'):
        self.json_file = Path(json_file_path)
        self.progress_file = Path(progress_file)
        self.driver = None
        self.movies = []
        self.processed = {}
        
        # Load existing progress if available
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.processed = json.load(f)
    
    def load_movies(self):
        """Load the Trakt ratings JSON file"""
        print(f"📥 Loading movies from {self.json_file}...")
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.movies = json.load(f)
        # Reverse to process oldest first (most recent last)
        self.movies.reverse()
        print(f"✓ Loaded {len(self.movies)} movies (reversed order)")
    
    def init_driver(self):
        """Initialize Selenium WebDriver - let Selenium manage Chrome directly"""
        print("⏳ Launching Chrome...")
        
        try:
            # Configure Chrome options
            options = webdriver.ChromeOptions()
            
            # Keep Chrome window visible so you can see what's happening
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Let Selenium manage Chrome directly
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            print("✓ Chrome launched successfully!")
            print("📍 Opening IMDb...")
            self.driver.get("https://www.imdb.com/registration/signin/?subPageType=sign_in")
            time.sleep(2)
            return True
                
        except Exception as e:
            print(f"✗ Failed to launch Chrome: {e}")
            return False
    
    def save_progress(self):
        """Save progress to resume later"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.processed, f, indent=2)
    
    def rate_movie(self, imdb_id, rating, title):
        """Navigate to IMDb movie and add rating"""
        try:
            url = f"https://www.imdb.com/title/{imdb_id}/"
            print(f"  📍 Opening: {url}")
            
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            time.sleep(1)  # Extra wait for dynamic content
            
            # First, click the main Rate button to open the rating popover
            try:
                open_rating_button = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//div[@data-testid='hero-rating-bar__user-rating__unrated']]"))
                )
                print(f"  🖱️  Opening rating dialog...")
                self.driver.execute_script("arguments[0].click();", open_rating_button)
                time.sleep(1)
            except TimeoutException:
                print(f"  ⚠ Could not find Rate button to open dialog for {title}")
                return False
            
            # Then, find and click the star for the rating
            # The buttons have aria-label like "Rate 9"
            try:
                star_xpath = f"//button[contains(@class, 'ipc-starbar__rating__button')][@aria-label='Rate {rating}']"
                star_element = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, star_xpath))
                )
                print(f"  ⭐ Clicking {rating}-star rating...")
                self.driver.execute_script("arguments[0].click();", star_element)
                time.sleep(1)
            except TimeoutException:
                print(f"  ⚠ Could not find {rating}-star button for {title}")
                return False
            
            # Then click the "Rate" button to save the rating
            try:
                rate_button = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ipc-rating-prompt__rate-button')]"))
                )
                print(f"  🖱️  Clicking Rate button to save...")
                self.driver.execute_script("arguments[0].click();", rate_button)
                time.sleep(2)  # Wait for rating to be saved
                return True
            except TimeoutException:
                print(f"  ⚠ Could not find Rate button for {title}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
    
    def run(self):
        """Main execution loop"""
        self.load_movies()
        
        if not self.init_driver():
            print("\n❌ Could not initialize driver. Exiting.")
            return
        
        # Wait for user to confirm they're on IMDb
        print("\n" + "="*60)
        print("⚠️  IMPORTANT - PLEASE READ")
        print("="*60)
        print(f"Chrome is open. You have {LOGIN_TIME_SECONDS} seconds to:")
        print("1. Log into IMDb (if not already logged in)")
        print("2. Leave the tab open")
        print("\nThe script will navigate automatically from here.")
        print("="*60 + "\n")
        
        for i in range(LOGIN_TIME_SECONDS, 0, -1):
            print(f"Starting in {i}s...", end='\r')
            time.sleep(1)
        
        print("                  ")  # Clear the line
        print("🚀 STARTING IMPORT PROCESS...\n")
        time.sleep(1)
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        try:
            for i, movie in enumerate(self.movies, 1):
                imdb_id = movie['movie']['ids'].get('imdb')
                rating = movie['rating']
                title = movie['movie']['title']
                year = movie['movie']['year']
                
                if not imdb_id:
                    print(f"[{i}/{len(self.movies)}] ⊘ Skipping '{title}' (no IMDb ID)")
                    skip_count += 1
                    continue
                
                # Skip if already processed
                if imdb_id in self.processed:
                    status = self.processed[imdb_id]
                    if status == 'success':
                        print(f"[{i}/{len(self.movies)}] ✓ Already rated: {title} ({year})")
                        success_count += 1
                        continue
                    elif status == 'failed':
                        print(f"[{i}/{len(self.movies)}] 🔄 Retrying: {title} ({year}) - Rating: {rating}/10")
                    else:
                        continue
                
                print(f"[{i}/{len(self.movies)}] Adding rating for '{title}' ({year}) - {rating}/10")
                
                if self.rate_movie(imdb_id, rating, title):
                    self.processed[imdb_id] = 'success'
                    success_count += 1
                    print(f"  ✓ SUCCESS")
                else:
                    self.processed[imdb_id] = 'failed'
                    fail_count += 1
                    print(f"  ✗ FAILED")
                
                # Save progress after each movie
                self.save_progress()
                
                # Polite delay between requests
                time.sleep(3)
        
        except KeyboardInterrupt:
            print("\n\n⛔ Interrupted by user")
        
        finally:
            # Print summary
            print("\n" + "="*60)
            print("IMPORT SUMMARY")
            print("="*60)
            print(f"✓ Successfully rated: {success_count}")
            print(f"✗ Failed: {fail_count}")
            print(f"⊘ Skipped: {skip_count}")
            print(f"📊 Total processed: {success_count + fail_count + skip_count}/{len(self.movies)}")
            print(f"💾 Progress saved to: {self.progress_file}")
            print("="*60)
            
            if self.driver:
                print("Keeping Chrome open. Close it manually when done.")
                # Don't close - keep browser open


if __name__ == "__main__":
    json_path = Path(__file__).parent / "ratings-movies.json"
    
    if not json_path.exists():
        print(f"❌ Error: {json_path} not found!")
        sys.exit(1)
    
    importer = IMDbRatingsImporter(json_path)
    importer.run()
