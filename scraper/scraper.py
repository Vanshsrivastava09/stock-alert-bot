import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Callable, Optional, Any
import re


def check_product(url: str) -> Dict[str, Any]:
    """
    Fetch a product page and return price, in_stock status, and title.
    
    Args:
        url: Product page URL
        
    Returns:
        Dict with keys: price (float|None), in_stock (bool), title (str)
    """
    domain = urlparse(url).netloc
    
    # Try requests + BeautifulSoup first
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }, timeout=10)
        response.raise_for_status()
        
        # Check if page is JS-rendered (empty body or suspicious content)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to parse with domain-specific parser
        parser = DOMAIN_PARSERS.get(domain)
        if parser:
            result = parser(soup, url)
            if result['price'] is not None or result['title']:
                return result
        
        # Fallback to generic parsing if no domain-specific parser or it failed
        return generic_parser(soup, url)
        
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        # Fall back to Playwright for JS-rendered pages
        return check_product_playwright(url)


def check_product_playwright(url: str) -> Dict[str, Any]:
    """
    Fallback method using Playwright for JS-rendered pages.
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            
            # Wait for page to load
            page.wait_for_load_state('networkidle', timeout=5000)
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            domain = urlparse(url).netloc
            parser = DOMAIN_PARSERS.get(domain)
            if parser:
                result = parser(soup, url)
            else:
                result = generic_parser(soup, url)
            
            browser.close()
            return result
            
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return {'price': None, 'in_stock': False, 'title': ''}
    except Exception as e:
        print(f"Playwright failed for {url}: {e}")
        return {'price': None, 'in_stock': False, 'title': ''}


def parse_books_toscrape(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Parser for books.toscrape.com
    """
    # Extract title
    title_elem = soup.find('h1')
    title = title_elem.text.strip() if title_elem else ''
    
    # Extract price
    price_elem = soup.find('p', class_='price_color')
    price = None
    if price_elem:
        price_text = price_elem.text.strip()
        # Remove £ symbol and convert to float
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            price = float(price_match.group())
    
    # Extract stock status
    stock_elem = soup.find('p', class_='instock availability')
    in_stock = False
    if stock_elem:
        stock_text = stock_elem.text.strip().lower()
        in_stock = 'in stock' in stock_text
    
    return {'price': price, 'in_stock': in_stock, 'title': title}


def generic_parser(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Generic parser that attempts to extract common e-commerce patterns.
    """
    # Try to find title in common locations
    title = ''
    for selector in ['h1', 'h2.product-title', '.product-name', '[itemprop="name"]']:
        elem = soup.select_one(selector)
        if elem:
            title = elem.text.strip()
            break
    
    # Try to find price in common patterns
    price = None
    price_patterns = [
        r'[\$€£]\s*[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*[\$€£]',
        r'price[:\s]*[\$€£]?\s*[\d,]+\.?\d*',
    ]
    
    for pattern in price_patterns:
        matches = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
        for match in matches:
            price_match = re.search(r'[\d,]+\.?\d*', match)
            if price_match:
                price_str = price_match.group().replace(',', '')
                try:
                    price = float(price_str)
                    break
                except ValueError:
                    continue
        if price is not None:
            break
    
    # Try to find stock status
    in_stock = False
    stock_keywords = ['in stock', 'available', 'add to cart', 'buy now']
    stock_text = soup.get_text().lower()
    for keyword in stock_keywords:
        if keyword in stock_text:
            in_stock = True
            break
    
    return {'price': price, 'in_stock': in_stock, 'title': title}


# Domain-specific parser registry
DOMAIN_PARSERS: Dict[str, Callable[[BeautifulSoup, str], Dict[str, Any]]] = {
    'books.toscrape.com': parse_books_toscrape,
}
