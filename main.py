import shopify
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env file
load_dotenv('.env')
token = os.getenv('TOKEN')
merchant = os.getenv('MERCHANT')

# Activate Shopify session
api_session = shopify.Session(merchant, '2024-07', token)
shopify.ShopifyResource.activate_session(api_session)

# Load the CSV file to create the country code to tag mapping
file_path = '00i_country_mappings.csv'  # Update with the correct path
country_mappings = pd.read_csv(file_path)

# Create sets from the country mappings
to_customer_countries = set(country_mappings['to_customer'].dropna())
to_dragon_countries = set(country_mappings['to_dragon'].dropna())
print(to_customer_countries)

# Function to fetch untagged orders from Shopify
def get_untagged_orders():
    orders = shopify.Order.find(limit=250)
    untagged_orders = [order for order in orders if not order.tags]
    return untagged_orders

# Function to determine the country of an order
def determine_order_country(order):
    shipping_address = order.shipping_address
    if shipping_address:
        country_code = shipping_address.country_code
        return country_code
    return None

# Function to add a tag to an order
def add_tag_to_order(order, new_tag):
    current_tags = order.tags.split(",") if order.tags else []
    current_tags.append(new_tag)
    order.tags = ",".join(current_tags)
    order.save()

# Fetch untagged orders
untagged_orders = get_untagged_orders()

# Add the corresponding tag to each untagged order
for order in untagged_orders:
    country_code = determine_order_country(order)
    if country_code:
        if country_code in to_customer_countries:
            add_tag_to_order(order, 'to_customer')
            print(f"Added 'to_customer' tag to Order ID {order.id}")
        elif country_code in to_dragon_countries:
            add_tag_to_order(order, 'to_dragon')
            print(f"Added 'to_dragon' tag to Order ID {order.id}")
        else:
            print(f"Order ID {order.id}: Country code '{country_code}' not found in CSV")
    else:
        print(f"Order ID {order.id}: No shipping country code found")
