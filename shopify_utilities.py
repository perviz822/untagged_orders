import shopify
from dotenv import load_dotenv
import os
import pandas as pd
import requests


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





def get_current_tags(order_id):
    #  Fetch current tags of the order
    query = """
    query($id: ID!) {
      order(id: $id) {
        id
        tags
      }
    }
    """
    variables = {"id": order_id}
    response = send_graph_ql_request(query, variables)
    
    if 'errors' in response:
        print(f"GraphQL errors: {response['errors']}")
        return
    elif 'data' in response and 'order' in response['data']:
        current_tags = response['data']['order']['tags']
        return current_tags
    else:
        print("Unexpected response format:", response)
        return
    


def send_graph_ql_request(query,  variables=None):
    token, merchant = load_env_variables()
    
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token
        }
        shopify_url = f'https://{merchant}.myshopify.com/admin/api/2024-07/graphql.json'

        payload = {
            'query': query,
            'variables': variables
        }

       
        response = requests.post(shopify_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching orders: HTTP {response.status_code} - {response.text}")
            return []   

    except Exception as e:
        print(f"Error fetching orders: {e}")
        return [] 
    


def remove_tags_from_order(order_id, tags_to_remove):
    current_tags =  get_current_tags(order_id)
    new_tags = [tag for tag in current_tags if tag not in tags_to_remove]
    mutation = """
    mutation($id: ID!, $tags: [String!]!) {
      orderUpdate(input: {id: $id, tags: $tags}) {
        order {
          id
          tags
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "id": order_id,
        "tags": new_tags
    }
    
    response = send_graph_ql_request(mutation, variables)
    
    if 'errors' in response:
        print(f"GraphQL errors: {response['errors']}")
    elif 'data' in response and 'orderUpdate' in response['data']:
        if response['data']['orderUpdate']['userErrors']:
            print(f"User errors: {response['data']['orderUpdate']['userErrors']}")
        else:
            print(f"Tags updated successfully. Updated order tags: {response['data']['orderUpdate']['order']['tags']}")
    else:
        print("Unexpected response format:", response)

   


# Example usage

