import shopify
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from .env file
load_dotenv('.env')
token = os.getenv('TOKEN')
merchant = os.getenv('MERCHANT')

try:
    # Activate Shopify session
    api_session = shopify.Session(merchant, '2024-07', token)
    shopify.ShopifyResource.activate_session(api_session)
except Exception as e:
    print(f"Error activating Shopify session: {e}")
    exit(1)

# Load the CSV file to create the country code to tag mapping
file_path = '00i_country_mappings.csv'
country_mappings = pd.read_csv(file_path)


# Create sets from the country mappings

to_customer_countries = set(country_mappings['to_customer'].dropna())
to_dragon_countries = set(country_mappings['to_dragon'].dropna())


# Function to fetch untagged orders from Shopify
def get_untagged_orders():
    try:
        orders= []
        data = shopify.Order.find(limit=250)
        for d  in data:
            tags = d.tags.split(",") if d.tags else []
            if 'to_customer' not in tags and 'to_dragon' not in tags:
             orders.append(d)
        while data.has_next_page():
            data=data.next_page()
            for d in data:
             tags = d.tags.split(",") if d.tags else []
             if 'to_customer' not in tags and 'to_dragon' not in tags:
                orders.append(d)   

        return orders         
    
    
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []

# Function to determine the country code of an order
def determine_order_country(order):
    try:
        shipping_address = order.shipping_address
        if shipping_address:
            country_code = shipping_address.country_code
            return country_code
    except AttributeError:
        print(f"Order ID {order.id}: Error accessing shipping address.")
    return None

# Function to add a tag to an order
def add_tag_to_order(order, new_tag):
    try:
        current_tags = order.tags.split(",") if order.tags else []
        current_tags.append(new_tag)
        order.tags = ",".join(current_tags)
        order.save()
        print(f"Added '{new_tag}' tag to Order ID {order.id}")
    except Exception as e:
      
        print(f"Error adding tag to Order ID {order.id}: {e}")


if __name__=="__main__":
    # Fetch untagged orders
    untagged_orders = get_untagged_orders()
    # Add the corresponding tag to each untagged order
    for order in untagged_orders:
        country_code = determine_order_country(order)
        if country_code:
            if country_code in to_customer_countries:
                add_tag_to_order(order, 'to_customer')
            elif country_code in to_dragon_countries:
                add_tag_to_order(order, 'to_dragon')
            else:
                print(f"Order ID {order.id}: Country code '{country_code}' not found in CSV")
        else:
            print(f"Order ID {order.id}: No shipping country code found")
