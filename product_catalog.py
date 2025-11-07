import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "https://www.shl.com/products/product-catalog/?start={}&type=1&type=1"
MAX_ITEMS = 500
MAX_WORKERS = 10

headers = {'User-Agent': 'Mozilla/5.0'}

def get_page_content(url):
    """Fetches the HTML content of the page."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

def extract_product_info(product_url, name, adaptive_support, remote_support, test_types):
    """Fetches product page and extracts duration and description."""
    duration = 0
    description = "N/A"

    content = get_page_content(product_url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')

        for p in soup.find_all('p'):
            if 'Approximate Completion Time in minutes' in p.get_text():
                match = re.search(r'(\d+)', p.get_text())
                if match:
                    duration = int(match.group(1))
                    break

        desc_tag = soup.find('h4', string='Description')
        if desc_tag:
            desc_paragraph = desc_tag.find_next('p')
            if desc_paragraph:
                description = desc_paragraph.get_text(strip=True)

    return {
        "url": product_url,
        "name": name,
        "adaptive_support": adaptive_support,
        "description": description,
        "duration": duration,
        "remote_support": remote_support,
        "test_type": ", ".join(test_types)
    }

def extract_data_from_page(page_content):
    """Extracts basic product info from catalog page (without visiting product pages)."""
    soup = BeautifulSoup(page_content, 'html.parser')
    rows = soup.find_all('tr', {'data-entity-id': True})
    products = []

    for row in rows:
        try:
            a_tag = row.find('a', href=True)
            product_url = "https://www.shl.com" + a_tag['href'] if a_tag else ""
            name = a_tag.get_text(strip=True) if a_tag else "N/A"
            adaptive_support = 'Yes' if row.find('span', class_='catalogue__circle -yes') else 'No'
            remote_support = 'Yes'
            test_types = [span.get_text(strip=True) for span in row.find_all('span', class_='product-catalogue__key')]

            products.append((product_url, name, adaptive_support, remote_support, test_types))
        except Exception as e:
            print(f"Error parsing row: {e}")
    return products

def extract_next_page_url(current_url):
    """Generates next page URL by incrementing the start value."""
    start_index = current_url.find('start=')
    if start_index == -1:
        return None
    start_value = int(current_url[start_index + 6:current_url.find('&', start_index)] 
                      if '&' in current_url[start_index:] else current_url[start_index + 6:])
    next_start = start_value + 12
    return f"https://www.shl.com/products/product-catalog/?start={next_start}&type=1&type=1"

def scrape_limited_products(max_items=500):
    """Scrapes product data with parallel product page requests."""
    all_data = []
    current_url = base_url.format(0)
    page_number = 0

    while len(all_data) < max_items:
        print(f"Scraping catalog page: {current_url} (Page {page_number + 1})")
        page_content = get_page_content(current_url)
        if not page_content:
            print("Failed to fetch catalog page content.")
            break

        products = extract_data_from_page(page_content)
        if not products:
            print("No more products found.")
            break
        remaining = max_items - len(all_data)
        products = products[:remaining]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(extract_product_info, *prod) for prod in products]
            for future in as_completed(futures):
                result = future.result()
                all_data.append(result)

        current_url = extract_next_page_url(current_url)
        if current_url:
            page_number += 1
            time.sleep(1)
        else:
            break

    return all_data

def save_to_csv(data, filename="product_catalog_parallel.csv"):
    """Saves scraped data to CSV with url first and name second."""
    df = pd.DataFrame(data)
    columns_order = ["url", "name", "adaptive_support", "description", "duration", "remote_support", "test_type"]
    df = df[columns_order]
    df.to_csv(filename, index=False)
    print(f"Saved {len(data)} rows to {filename}")

if __name__ == "__main__":
    limited_data = scrape_limited_products(MAX_ITEMS)
    save_to_csv(limited_data)
