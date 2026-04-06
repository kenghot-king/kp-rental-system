from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Extra Costs
    extra_hour = fields.Float("Per Hour", default=0.0)
    extra_day = fields.Float("Per Day", default=0.0)
    min_extra_hour = fields.Integer(
        "Minimum delay time before applying fines.", default=2,
    )

    extra_product = fields.Many2one(
        'product.product',
        string="Product",
        help="The product is used to add the cost to the sales order",
        domain="[('type', '=', 'service')]",
    )

    # Damage
    damage_product = fields.Many2one(
        'product.product',
        string="Damage Product",
        help="Service product used for damage fee charges on rental returns.",
        domain="[('type', '=', 'service')]",
    )

    # Deposit
    deposit_auto_refund = fields.Boolean(
        "Auto Refund Deposit",
        default=True,
        help="Automatically register a refund payment when a deposit credit note is created on return.",
    )

    # Rental Inventory
    rental_loc_id = fields.Many2one(
        "stock.location", string="Rental Location",
        domain=[('usage', '=', 'internal')],
        help="Internal location for products currently in rental. "
             "Products remain in inventory valuation.",
    )

    _min_extra_hour = models.Constraint(
        'CHECK(min_extra_hour >= 1)',
        "Minimal delay time before applying fines has to be positive.",
    )

    def _create_per_company_locations(self):
        super()._create_per_company_locations()
        self._create_rental_location()

    @api.model
    def create_missing_rental_location(self):
        companies = self.env['res.company'].search([('rental_loc_id', '=', False)])
        companies._create_rental_location()

    def _create_rental_location(self):
        rental_loc_values = []
        for company in self.sudo():
            if not company.rental_loc_id:
                rental_loc_values.append({
                    "name": self.env._("Rental"),
                    "usage": "internal",
                    "company_id": company.id,
                    "location_id": self.env.ref('stock.stock_location_customers').id,
                })
        if not rental_loc_values:
            return
        rental_locs = self.env['stock.location'].sudo().create(rental_loc_values)
        company_rental_loc = {loc.company_id.id: loc for loc in rental_locs}
        for company in rental_locs.company_id:
            company.rental_loc_id = company_rental_loc.get(company.id, False)
