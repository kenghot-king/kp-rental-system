from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    product_pricing_ids = fields.One2many(
        comodel_name='product.pricing',
        inverse_name='pricelist_id',
        string="Renting Price Rules",
        domain=[
            '|',
            ('product_template_id', '=', None),
            ('product_template_id.active', '=', True),
        ],
        copy=True,
    )

    @api.constrains('product_pricing_ids')
    def _check_pricing_product_rental(self):
        for pricing in self.product_pricing_ids:
            if not pricing.product_template_id.rent_ok:
                raise UserError(_(
                    "You can not have a time-based rule for products that are not rentable."
                ))

    def _compute_price_rule(
        self,
        products,
        quantity,
        *,
        currency=None,
        date=False,
        start_date=None,
        end_date=None,
        **kwargs,
    ):
        """Override to handle rental product pricing.

        When start_date and end_date are provided, rental products use the
        best pricing rule from product.pricing instead of standard pricelist
        rules.  Non-rental products fall through to the default implementation.
        """
        self and self.ensure_one()

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        if not products:
            return {}

        if not date:
            date = fields.Datetime.now()

        results = {}
        if self._enable_rental_price(start_date, end_date):
            rental_products = products.filtered('rent_ok')
            Pricing = self.env['product.pricing']
            for product in rental_products:
                if start_date and end_date:
                    tmpl = product.product_tmpl_id if product._name == 'product.product' else product
                    price = tmpl._compute_greedy_price(
                        start_date=start_date,
                        end_date=end_date,
                        pricelist=self,
                        currency=currency,
                    )
                    if not price:
                        price = product.lst_price if product._name == 'product.product' else product.list_price
                else:
                    pricing = Pricing._get_first_suitable_pricing(product, self)
                    duration = pricing.recurrence_id.duration if pricing else 0
                    if pricing:
                        price = pricing._compute_price(duration, pricing.recurrence_id.unit)
                        price = pricing.currency_id._convert(price, currency, self.env.company, date)
                    else:
                        price = product.lst_price if product._name == 'product.product' else product.list_price

                results[product.id] = (price, False)

        price_computed_products = self.env[products._name].browse(results.keys())
        return {
            **results,
            **super()._compute_price_rule(
                products - price_computed_products,
                quantity,
                currency=currency,
                date=date,
                **kwargs,
            ),
        }

    def _enable_rental_price(self, start_date, end_date):
        """Enable rental price computing or use default price computing.

        :param date start_date: A rental pickup date
        :param date end_date: A rental return date
        :return: Whether product pricing should be used to compute product price
        :rtype: bool
        """
        return bool(start_date and end_date)
