from odoo.http import route

from odoo.addons.sale.controllers.product_configurator import (
    SaleProductConfiguratorController,
)
from odoo.addons.ggg_rental.controllers.utils import _convert_rental_dates


class GGGRentalProductConfiguratorController(SaleProductConfiguratorController):

    @route()
    def sale_product_configurator_get_values(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_get_values(*args, **kwargs)

    @route()
    def sale_product_configurator_update_combination(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_update_combination(*args, **kwargs)

    @route()
    def sale_product_configurator_get_optional_products(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_get_optional_products(*args, **kwargs)
