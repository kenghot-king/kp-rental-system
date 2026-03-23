{
    'name': 'GGG Rental',
    'summary': 'Manage rental contracts, deliveries and returns',
    'description': """
GGG Rental
==========
Rental management for Odoo Community Edition.
Specify rentals of products (products, quotations, invoices, ...)
Manage status of products, rentals, delays.
Manage user and manager notifications.
    """,
    'category': 'Sales/Sales',
    'sequence': 160,
    'version': '19.0.1.0.0',
    'depends': ['sale_stock', 'ggg_gantt', 'l10n_th'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/rental_data.xml',
        'data/initial_config.xml',
        'views/product_pricelist_views.xml',
        'views/product_pricing_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_temporal_recurrence_views.xml',
        'views/res_config_settings_views.xml',
        'report/rental_order_report_templates.xml',
        'report/rental_report_views.xml',
        'wizard/rental_processing_views.xml',
        'views/sale_renting_menus.xml',
    ],
    'demo': [
        'data/rental_demo.xml',
    ],
    'application': True,
    'pre_init_hook': '_pre_init_rental',
    'post_init_hook': '_post_init_rental',
    'assets': {
        'web.assets_backend': [
            'ggg_rental/static/src/js/**/*',
        ],
        'web.assets_backend_lazy': [
            'ggg_rental/static/src/views/schedule_gantt/**',
        ],
    },
    'author': 'GGG',
    'license': 'LGPL-3',
}
