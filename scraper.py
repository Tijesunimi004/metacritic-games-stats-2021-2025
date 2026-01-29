import requests
import pandas as pd
import time
import random
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Constants
API_URL = "https://backend.metacritic.com/finder/metacritic/web"
BASE_URL = "https://www.metacritic.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.metacritic.com",
    "Referer": "https://www.metacritic.com/"
}

def get_game_details(slug):
    """
    Fetches the game details page and extracts:
    - Platform (JSON-LD)
    - Publisher (JSON-LD)
    - Genre (JSON-LD)
    - User Review Count (HTML Regex)
    """
    url = f"{BASE_URL}/game/{slug}/"
    details = {
        "Platform": "Unknown",
        "Publisher": "Unknown",
        "Genre": "Unknown",
        "User_Review_Count": 0
    }
    
    try:
        # Add a small random delay to be polite
        time.sleep(random.uniform(0.1, 0.3))
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Extract from JSON-LD
            script = soup.find('script', type='application/ld+json')
            if script:
                try:
                    data = json.loads(script.string)
                    
                    # Platform
                    if 'gamePlatform' in data:
                        platforms = data['gamePlatform']
                        if isinstance(platforms, list):
                            details["Platform"] = ", ".join(platforms)
                        else:
                            details["Platform"] = str(platforms)
                            
                    # Publisher
                    if 'publisher' in data:
                        pubs = data['publisher']
                        if isinstance(pubs, list):
                            pub_names = [p.get('name') for p in pubs if 'name' in p]
                            details["Publisher"] = ", ".join(pub_names)
                        elif isinstance(pubs, dict):
                            details["Publisher"] = pubs.get('name', "Unknown")
                            
                    # Genre
                    if 'genre' in data:
                        genres = data['genre']
                        if isinstance(genres, list):
                            details["Genre"] = ", ".join(genres)
                        else:
                            details["Genre"] = str(genres)
                            
                except json.JSONDecodeError:
                    pass
            
            # 2. Extract User Review Count from HTML using Regex
            # Pattern: "Based on 1,234 User Ratings"
            match = re.search(r"Based on\s+([0-9,]+)\s+User Ratings", html, re.IGNORECASE)
            if match:
                count_str = match.group(1).replace(',', '')
                try:
                    details["User_Review_Count"] = int(count_str)
                except ValueError:
                    pass
                    
    except Exception as e:
        print(f"Error fetching details for {slug}: {e}", flush=True)
    
    return details

def fetch_games_by_year(year, page=1):
    """
    Fetches a list of games for a specific year and page from the API.
    """
    params = {
        "sortBy": "-metaScore",
        "productType": "games",
        "page": page,
        "releaseYearMin": year,
        "releaseYearMax": year,
        "offset": (page - 1) * 24,
        "limit": 24,
        "componentName": "finder-list",
        "componentDisplayName": "Finder List",
        "componentType": "FinderList"
    }
    
    try:
        print(f"Fetching Year: {year}, Page: {page}...", flush=True)
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'items' in data['data']:
                return data['data']['items'], data['data'].get('totalResults', 0)
            else:
                print(f"Unexpected JSON structure for Year {year}, Page {page}", flush=True)
                return [], 0
        else:
            print(f"Failed to fetch Year {year}, Page {page}. Status: {response.status_code}", flush=True)
            return [], 0
            
    except Exception as e:
        print(f"Error fetching Year {year}, Page {page}: {e}", flush=True)
        return [], 0

def process_game_item(item):
    """
    Extracts relevant fields from a game item API response and merges with detail page data.
    """
    # 1. Basic Info from API
    title = item.get('title')
    slug = item.get('slug')
    url = f"{BASE_URL}/game/{slug}/" if slug else None
    
    # Release Date
    release_date = item.get('releaseDate') # Keep as string or format if needed
    
    # Metascore
    metascore = None
    critic_review_count = 0
    if 'criticScoreSummary' in item:
        css = item['criticScoreSummary']
        if css:
            metascore = css.get('score')
            critic_review_count = css.get('reviewCount', 0)
            
    # User Score (API)
    user_score = None
    if 'userScore' in item:
        us = item['userScore']
        if us:
            score_val = us.get('score')
            if score_val and str(score_val).lower() != 'tbd':
                try:
                    user_score = float(score_val)
                except ValueError:
                    pass

    # Rating
    rating = item.get('rating', 'Not Rated')
    if rating is None:
        rating = 'Not Rated'

    # 2. Detailed Info from Page
    details = get_game_details(slug) if slug else {}
    
    return {
        'Title': title,
        'Platform': details.get('Platform', 'Unknown'),
        'Release_Date': release_date,
        'Metascore': metascore,
        'User_Score': user_score,
        'Critic_Review_Count': critic_review_count,
        'User_Review_Count': details.get('User_Review_Count', 0),
        'Publisher': details.get('Publisher', 'Unknown'),
        'Genre': details.get('Genre', 'Unknown'),
        'Rating': rating,
        'URL': url
    }

def main():
    print("Starting Metacritic API Scraper (Enhanced)...", flush=True)
    
    all_games = []
    years = range(2021, 2026) # 2021 to 2025
    
    for year in years:
        print(f"\n--- Processing Year: {year} ---", flush=True)
        page = 1
        while True:
            items, total_results = fetch_games_by_year(year, page)
            
            if not items:
                break
                
            print(f"Found {len(items)} games on page {page}. Fetching details...", flush=True)
            
            for item in items:
                try:
                    game_data = process_game_item(item)
                    all_games.append(game_data)
                except Exception as e:
                    print(f"Error processing item '{item.get('title', 'Unknown')}': {e}", flush=True)
                    # Optional: print traceback for debugging
                    # import traceback
                    # traceback.print_exc()
                    continue
            
            # Pagination check
            if len(items) < 24:
                break
            
            # Safety break removed for full scrape
            # if page >= 1: 
            #      print("Reached page limit (1) for testing. Moving to next year.", flush=True)
            #      break
            
            page += 1
            time.sleep(1) # Delay between pages

    print(f"\nScraping Complete. Total games collected: {len(all_games)}", flush=True)
    
    if all_games:
        print("Saving data to metacritic_games_data.csv...", flush=True)
        df = pd.DataFrame(all_games)
        
        # Reorder columns as requested
        cols = [
            'Title', 'Platform', 'Release_Date', 'Metascore', 'User_Score',
            'Critic_Review_Count', 'User_Review_Count', 'Publisher', 'Genre', 'Rating'
        ]
        # Add URL at the end if useful
        cols.append('URL')
        
        # Ensure all columns exist
        for c in cols:
            if c not in df.columns:
                df[c] = None
                
        df = df[cols]
        
        df.to_csv("metacritic_games_data.csv", index=False)
        print("Done!", flush=True)
        print(df.head())
    else:
        print("No games found.", flush=True)

if __name__ == "__main__":
    main()
