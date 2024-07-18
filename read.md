# Shopify Order Tagging Script Documentation

## Overview

This script is designed to fetch untagged orders, then identifies the  country code of the order, then  determines which category it belongs  ***to_customer*** or ***to_dragon*** in the csv file , then accordingly adds to_customer or to_dragon tags to the untagged order

## Load Environment Variables

Loads the Shopify API credentials from the `.env` file.

```python
from dotenv import load_dotenv
import os

load_dotenv('.env')
token = os.getenv('TOKEN')
merchant = os.getenv('MERCHANT')
```

### Activate Shopify Session

Activates the Shopify API session using the loaded credentials.

```python
import shopify

api_session = shopify.Session(merchant, '2024-07', token)
shopify.ShopifyResource.activate_session(api_session)
```

### Load Country Mappings

Reads the CSV file to create sets of  each category

```python
import pandas as pd

file_path = '00i_country_mappings.csv'
country_mappings = pd.read_csv(file_path)

to_customer_countries = set(country_mappings['to_customer'].dropna())
to_dragon_countries = set(country_mappings['to_dragon'].dropna())
```

### Fetch Untagged Orders

Fetches untagged orders from the Shopify store.

```python
def get_untagged_orders():
    orders = shopify.Order.find(limit=250)
    untagged_orders = [order for order in orders if not order.tags]
    return untagged_orders

untagged_orders = get_untagged_orders()
```

### Determine Order Country

Determines the country code from the order's shipping address.

```python
def determine_order_country(order):
    shipping_address = order.shipping_address
    if shipping_address:
        country_code = shipping_address.country_code
        return country_code
    return None
```

### Add Tag to Order

Adds a specified tag to an order.

```python
def add_tag_to_order(order, new_tag):
    current_tags = order.tags.split(",") if order.tags else []
    current_tags.append(new_tag)
    order.tags = ",".join(current_tags)
    order.save()
```

### Main Tagging Logic

Loops through untagged orders, determines the country code, and adds the appropriate tag based on the mappings.

```python
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
```
