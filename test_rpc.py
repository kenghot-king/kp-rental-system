import xmlrpc.client

url = 'http://localhost:8069'
db = 'test_ce'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
if uid:
    print(f"Successfully authenticated with UID {uid}")
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    # Test checking if we can query products
    products = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[['rent_ok', '=', True]]], {'fields': ['name', 'list_price']})
    print(f"Found {len(products)} rental products: {products}")
else:
    print("Failed to authenticate")
