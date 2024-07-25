from shopify_utilities import load_env_variables,add_tag_to_an_order,determine_country_of_order, activate_shopify_session
import shopify
import pandas as pd

"""This script fetches the orders that have not been categorized  with  to_customer  and to_dragon
   It determines the country of the order, then checks which category  it belongs to,  the categorized country
   codes  are in the country mappings  csv file and according to  category,  and it adds  to_customer or to_dragon  tags
   accordingly
"""



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


def main(file_path):
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
    main("00i_country_mappings.csv")
    # Load environment variables
