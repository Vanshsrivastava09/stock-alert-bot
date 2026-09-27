import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.crud import DatabaseManager

def main():
    print("Simulating price drop for testing scheduler alerts...")
    
    # Force use of SQLite for testing
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    db = DatabaseManager('stock_alerts.db')
    
    # Get all products
    products = db.get_all_products()
    
    if not products:
        print("❌ No products found in database.")
        print("Please first track a product using the Telegram bot.")
        return
    
    print("Current products in database:")
    for idx, product in enumerate(products, 1):
        price_text = f"£{product.last_price}" if product.last_price else "N/A"
        print(f"{idx}. {product.title} - Price: {price_text} (ID: {product.id})")
    
    # Simulate price drop for the first product
    if products:
        product = products[0]
        old_price = product.last_price
        
        # Set a lower price
        new_price = old_price * 0.8 if old_price else 10.0  # 20% discount or £10 if no price
        
        print(f"\n🔄 Updating price for: {product.title}")
        print(f"   Old price: £{old_price}")
        print(f"   New price: £{new_price}")
        
        updated_product = db.update_product_status(product.id, price=new_price, in_stock=product.in_stock)
        
        print(f"✅ Price updated successfully!")
        print(f"   Subscribers will be notified on next scheduler cycle.")
        
        # Show subscribers
        subscribers = db.get_subscribers_for_product(product.id)
        print(f"   Current subscribers: {subscribers}")
        
        print("\n📅 Next scheduler cycle will run in ≤10 minutes.")
        print("   Or run: python scheduler/monitor.py to trigger an immediate check")

if __name__ == '__main__':
    main()
