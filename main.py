import shopify
from dotenv import load_dotenv
import os
import pandas as pd


def load_env_variables():
    """Load environment variables from .env file."""
    load_dotenv(".env")
    return os.getenv("TOKEN"), os.getenv("MERCHANT")


def activate_shopify_session(token, merchant):
    """Activate Shopify session using the provided token and merchant details."""
    try:
        api_session = shopify.Session(merchant, "2024-07", token)
        shopify.ShopifyResource.activate_session(api_session)
    except Exception as e:
        print(f"Error activating Shopify session: {e}")
        exit(1)


def load_country_mappings(file_path):
    """Load the CSV file to create the country code to tag mapping."""
    country_mappings = pd.read_csv(file_path)
    to_customer_countries = set(country_mappings["to_customer"].dropna())
    to_dragon_countries = set(country_mappings["to_dragon"].dropna())
    return to_customer_countries, to_dragon_countries


def append_if_untagged(all_orders, untagged_orders):
   try:
        for order in all_orders:
            tags = order.tags.split(",") if order.tags else []
            if "to_customer" not in tags and "to_dragon" not in tags:
                untagged_orders.append(order)
   except Exception as e :
       print(f"Error appending to untagged orders {e}")       


def get_untagged_orders():
    """
    Fetch untagged orders from Shopify.
    Returns:
        list: List of untagged orders.
    """
    try:
        untagged_orders = []
        all_orders = shopify.Order.find(limit=250)
        append_if_untagged(all_orders, untagged_orders)
        while all_orders.has_next_page():
            all_orders = all_orders.next_page()
            append_if_untagged(all_orders, untagged_orders)
        return untagged_orders
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []


def determine_country_of_order(order):
    """
    Determine the country code of an order.
    Args:
        order (shopify.Order): The order to determine the country code for.
    Returns:
        str: The country code of the order's shipping address, or None if not available.
    """
    try:
        shipping_address = order.shipping_address
        if shipping_address:
            return shipping_address.country_code
    except AttributeError:
        print(f"Order ID {order.id}: Error accessing shipping address.")
    return None


def add_tag_to_an_order(order, new_tag):
    """
    Add a tag to an order.
    Args:
        order (shopify.Order): The order to add a tag to.
        new_tag (str): The tag to add to the order.
    """
    try:
        current_tags = order.tags.split(",") if order.tags else []
        print(current_tags)
        current_tags.append(new_tag)
        order.tags = ",".join(current_tags)
        order.save()
        print(f"Added '{new_tag}' tag to Order ID {order.id}")
    except Exception as e:
        print(f"Error adding tag to Order ID {order.id}: {e}")


def tag_orders(file_path):
    token, merchant = load_env_variables()
    activate_shopify_session(token, merchant)
    to_customer_countries, to_dragon_countries = load_country_mappings(file_path)
    untagged_orders = get_untagged_orders()

    # Add the corresponding tag to each untagged order
    for order in untagged_orders:
        country_code = determine_country_of_order(order)
        if country_code:
            if country_code in to_customer_countries:
                add_tag_to_an_order(order, "to_customer")
            elif country_code in to_dragon_countries:
                add_tag_to_an_order(order, "to_dragon")
            else:
                print(
                    f"Order ID {order.id}: Country code '{country_code}' not found in CSV"
                )
        else:
            print(f"Order ID {order.id}: No shipping country code found")


if __name__ == "__main__":
    tag_orders("00i_country_mappings.csv")
    # Load environment variables
