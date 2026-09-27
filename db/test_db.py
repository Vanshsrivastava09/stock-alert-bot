import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.crud import DatabaseManager
from db.models import Product, Subscription


def main():
    print("Testing SQLite persistence layer...\n")
    print("=" * 70)
    
    # Use a test database (local SQLite for testing)
    # Force use of SQLite by removing DATABASE_URL if present
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    db = DatabaseManager('test_stock_alerts.db')
    
    # Clean up any existing test data
    session = db.get_session()
    session.query(Subscription).delete()
    session.query(Product).delete()
    session.commit()
    session.close()
    
    print("\n1. Adding a fake product...")
    test_url = "http://example.com/test-product"
    test_title = "Test Product"
    product = db.add_product_if_new(test_url, title=test_title)
    print(f"   Added product: {product}")
    
    print("\n2. Getting all products...")
    products = db.get_all_products()
    print(f"   Total products: {len(products)}")
    for p in products:
        print(f"   - {p}")
    
    print("\n3. Subscribing a fake chat_id...")
    test_chat_id = "test_user_123"
    subscription = db.subscribe(test_chat_id, product.id)
    print(f"   Subscription created: {subscription}")
    
    print("\n4. Getting subscribers for product...")
    subscribers = db.get_subscribers_for_product(product.id)
    print(f"   Subscribers: {subscribers}")
    
    print("\n5. Updating product status (price and stock)...")
    updated_product = db.update_product_status(
        product.id, 
        price=99.99, 
        in_stock=True
    )
    print(f"   Updated product: {updated_product}")
    
    print("\n6. Getting product by URL...")
    product_by_url = db.get_product_by_url(test_url)
    print(f"   Product by URL: {product_by_url}")
    
    print("\n7. Getting product by ID...")
    product_by_id = db.get_product_by_id(product.id)
    print(f"   Product by ID: {product_by_id}")
    
    print("\n8. Testing duplicate subscription (should return existing)...")
    duplicate_subscription = db.subscribe(test_chat_id, product.id)
    print(f"   Duplicate subscription: {duplicate_subscription}")
    
    print("\n9. Unsubscribing user...")
    unsubscribed = db.unsubscribe(test_chat_id, product.id)
    print(f"   Unsubscribed: {unsubscribed}")
    
    print("\n10. Getting subscribers after unsubscribe...")
    subscribers_after = db.get_subscribers_for_product(product.id)
    print(f"   Subscribers: {subscribers_after}")
    
    print("\n11. Testing add_product_if_new with existing URL...")
    existing_product = db.add_product_if_new(test_url, title="New Title")
    print(f"   Should return existing product: {existing_product}")
    
    print("\n" + "=" * 70)
    print("Database test completed successfully!")
    
    # Clean up test database
    session = db.get_session()
    session.query(Subscription).delete()
    session.query(Product).delete()
    session.commit()
    session.close()
    
    print("\nTest database cleaned up.")


if __name__ == '__main__':
    main()
