import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.crud import DatabaseManager

def main():
    print("Setting up test data for scheduler testing...")
    
    # Force use of SQLite for testing
    original_db_url = os.environ.get('DATABASE_URL')
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    db = DatabaseManager('test_stock_alerts.db')
    
    # Restore original DATABASE_URL if it existed
    if original_db_url:
        os.environ['DATABASE_URL'] = original_db_url
    
    # Clean up any existing test data
    session = db.get_session()
    from db.models import Subscription, Product
    session.query(Subscription).delete()
    session.query(Product).delete()
    session.commit()
    session.close()
    
    # Add a test product with a high initial price
    test_url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    product = db.add_product_if_new(test_url, title="Test Book for Scheduler")
    
    # Set initial high price
    db.update_product_status(product.id, price=100.0, in_stock=True)
    
    print(f"✅ Created test product: {product.title} with price £100.0")
    
    # Subscribe a test user (replace with your actual chat_id from Telegram)
    test_chat_id = "YOUR_TELEGRAM_CHAT_ID"  # Replace this with your actual chat_id
    subscription = db.subscribe(test_chat_id, product.id)
    
    print(f"✅ Subscribed chat_id: {test_chat_id}")
    print(f"✅ Product ID: {product.id}")
    
    print("\nNow you can:")
    print("1. Start the bot with: python main.py")
    print("2. Manually update the price in the DB to simulate a price drop")
    print("3. Wait for the scheduler to run (every 10 minutes) or run scheduler/monitor.py directly")
    
    print("\nTo manually update the price in the DB, you can:")
    print("- Use the test_db.py script to update the product")
    print("- Or manually edit the SQLite database")
    print("- Or wait for the next scheduler cycle which will scrape the actual price")

if __name__ == '__main__':
    main()
