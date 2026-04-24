{
    'name': 'GGG Rental Website',
    'summary': 'Show rental pricing and deposit on the e-commerce shop',
    'category': 'Sales/Sales',
    'version': '19.0.1.0.0',
    'depends': ['ggg_rental', 'website_sale'],
    'data': [
        'views/website_rental_shop_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ggg_rental_website/static/src/css/rental_shop.css',
        ],
    },
    'author': 'GGG',
    'license': 'LGPL-3',
    'application': False,
}
