import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.scraper import check_product


def main():
    """
    Test the scraper with public demo e-commerce sites.
    """
    # Test URLs from public demo/sandbox e-commerce sites
    test_urls = [
        # books.toscrape.com - A dedicated web scraping test site
        'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html',
        'http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html',
        'http://books.toscrape.com/catalogue/soumission_998/index.html',
    ]
    
    print("Testing product scraper with demo sites...\n")
    print("=" * 70)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 70)
        
        result = check_product(url)
        
        print(f"Title: {result['title']}")
        print(f"Price: {'£' + str(result['price']) if result['price'] is not None else 'N/A'}")
        print(f"In Stock: {result['in_stock']}")
        
    print("\n" + "=" * 70)
    print("Test complete!")


if __name__ == '__main__':
    main()
