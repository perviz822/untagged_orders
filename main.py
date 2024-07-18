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

# Load the CSV file to create the country code to name mapping
file_path = 'country_codes.csv'  # Update with the correct path
country_mappings = pd.read_csv(file_path)

# Create a dictionary from the country mappings
country_code_to_name = pd.Series(country_mappings['name'].values, index=country_mappings['alpha-2']).to_dict()

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

# Add the corresponding country name as a tag to each untagged order
for order in untagged_orders:
    country_code = determine_order_country(order)
    if country_code:
        country_name = country_code_to_name.get(country_code, "Unknown Country")
        add_tag_to_order(order, country_name)
        print(f"Added '{country_name}' tag to Order ID {order.id}")
    else:
        print(f"Order ID {order.id}: No shipping country code found")
