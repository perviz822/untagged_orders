from shopify_utilities import load_env_variables, activate_shopify_session, get_current_tags  , send_graph_ql_request, remove_tags_from_order
"""
This script  removes the tags from an order based on the provided  tag list

"""

def get_all_orders_with_tags():
    query = """
    query($cursor: String) {
      orders(first: 250, after: $cursor) {
        edges {
          node {
            id
            tags
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    orders = []
    cursor = None
    while True:
        variables = {'cursor': cursor} if cursor else {}
        response = send_graph_ql_request( query, variables)
        
        if 'data' in response and 'orders' in response['data']:
            orders_data = response['data']['orders']
            for edge in orders_data['edges']:
                orders.append(edge['node'])

            # Check if there are more pages
            page_info = orders_data['pageInfo']
            if page_info['hasNextPage']:
                cursor = page_info['endCursor']
            else:
                break
        else:
            print("Error fetching orders.")
            break

    return orders



def remove_tags_from_all_orders (tags):
    orders =  get_all_orders_with_tags()
    for order in orders:
        remove_tags_from_order(order.get('id'),tags)



if __name__ == "__main__":
    tags =['Custom Item']
    remove_tags_from_all_orders(tags)
        



