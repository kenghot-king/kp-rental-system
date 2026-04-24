from odoo import api, fields, models

PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 31,
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rental_base_daily_price = fields.Float(
        string="Base Daily Rental Price",
        compute='_compute_rental_daily_price',
    )
    rental_best_pricing_id = fields.Many2one(
        comodel_name='product.pricing',
        string="Best Pricing Rule",
        compute='_compute_rental_daily_price',
    )

    @api.depends(
        'product_pricing_ids',
        'product_pricing_ids.price',
        'product_pricing_ids.recurrence_id',
        'product_pricing_ids.recurrence_id.duration',
        'product_pricing_ids.recurrence_id.unit',
    )
    def _compute_rental_daily_price(self):
        for product in self:
            pricings = product.product_pricing_ids.filtered(
                lambda p: p.recurrence_id and p.recurrence_id.duration > 0
                and p.recurrence_id.unit in PERIOD_RATIO
            )
            if not pricings:
                product.rental_base_daily_price = 0.0
                product.rental_best_pricing_id = False
                continue

            def price_per_day(p):
                return p.price / (
                    p.recurrence_id.duration
                    * PERIOD_RATIO[p.recurrence_id.unit]
                    / 24
                )

            best = min(pricings, key=price_per_day)
            product.rental_best_pricing_id = best
            product.rental_base_daily_price = price_per_day(best)
