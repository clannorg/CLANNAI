import requests
import pandas as pd
import os
import time
import random
from requests.exceptions import RequestException, JSONDecodeError
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_next_url(link_header):
    """
    Extracts the next URL from the link header, handling potential encoding issues.

    Args:
        link_header (str): The link header value.

    Returns:
        str: The URL for the next page, or None if there is no next page.
    """
    if not link_header:
        return None

    links = link_header.split(',')
    for link in links:
        if 'rel="next"' in link:
            # Use regex to extract the URL correctly
            match = re.search(r'<(.*?)>', link)
            if match:
                next_url = match.group(1)

                # Remove potentially problematic characters in cursor
                next_url = next_url.replace("%2F%2F%2F%2F", "")
                next_url = next_url.replace("%2F", "")
                logging.info(f"Next URL: {next_url}")
                return next_url
            else:
                logging.error(f"Could not extract next URL from link: {link}")
                return None
    return None

def fetch_club_data(api_url, headers, output_csv='data/veo_clubs_2.csv'):
    """Fetches club data from the Veo API and saves clubs with 10+ recordings to a CSV."""
    clubs = []
    processed_clubs = set()
    current_url = api_url
    session = requests.Session()
    session.headers.update(headers)

    page_count = 0
    try:
        while current_url:
            page_count += 1
            retries = 0
            max_retries = 10
            while retries < max_retries:
                try:
                    response = session.get(current_url, verify=True)
                    response.raise_for_status()
                    logging.info(f"Fetched data for page {page_count}: {response.text}")  # Log the response
                    break
                except RequestException as e:
                    if response and response.status_code == 429:
                        delay = min(32, (2 ** retries) + random.uniform(0, 1))
                        logging.info(f"Rate limit exceeded on page {page_count}. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        retries += 1
                    else:
                        logging.error(f"Network error on page {page_count}: {e}")
                        return
            if retries == max_retries:
                logging.error(f"Max retries reached for page {page_count}. Exiting.")
                break

            try:
                data = response.json()
                if isinstance(data, list):
                    club_list = data
                elif 'clubs' in data:
                    club_list = data['clubs']
                else:
                    logging.error(f"Unexpected data structure on page {page_count}. Skipping.")
                    break

                for club in club_list:
                    recordings = club.get('match_count', 0)
                    club_name = club.get('title', 'Unknown')
                    club_id = club.get('slug', 'Unknown')

                    if club_name == "River Plate":
                        print(f"Full API response for River Plate: {club}")

                    if recordings >= 10 and club_id not in processed_clubs:
                        clubs.append({
                            'Club Name': club_name,
                            'Recordings': recordings,
                            'Club Identifier': club_id,
                        })
                        processed_clubs.add(club_id)

                logging.info(f"Fetched {len(club_list)} clubs in page {page_count}")

                if page_count % 100 == 0 and clubs:
                    df = pd.DataFrame(clubs)
                    df.to_csv(output_csv, index=False)
                    logging.info(f"Incremental save at page {page_count}: {len(clubs)} clubs")

                next_url = get_next_url(response.headers.get('link'))
                current_url = next_url
                time.sleep(random.uniform(0.1, 0.3))

            except JSONDecodeError as e:
                logging.error(f"JSON decoding error on page {page_count}: {e}")
                break
            except Exception as e:
                logging.error(f"Unexpected error on page {page_count}: {e}")
                break

    except KeyboardInterrupt:
        logging.info("Script interrupted by user. Saving progress...")
        if clubs:  # Check if clubs list is not empty
            df = pd.DataFrame(clubs)
            os.makedirs('data', exist_ok=True)
            df.to_csv(output_csv, index=False)
            logging.info(f"Saved {len(clubs)} clubs to {output_csv}")
        else:
            logging.info("No clubs to save.")
        exit(0)

    # Final save
    if clubs:  # Check if clubs list is not empty
        df = pd.DataFrame(clubs)
        os.makedirs('data', exist_ok=True)
        df.to_csv(output_csv, index=False)
        logging.info(f"Saved {len(clubs)} clubs to {output_csv}")

if __name__ == "__main__":
    api_url = "https://app.veo.co/api/app/clubs/?fields=title&fields=match_count&fields=slug"
    cookie = os.environ.get("VEO_COOKIE")
    if not cookie:
        logging.error("Error: VEO_COOKIE environment variable not set.")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://app.veo.co/all-clubs/",
            "Cookie": cookie,
            "veo-app-id": "<redacted>"  # Replace with your app ID
        }
        fetch_club_data(api_url, headers)