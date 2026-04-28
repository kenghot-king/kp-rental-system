from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Extra Costs
    extra_hour = fields.Float("Per Hour", default=0.0)
    extra_day = fields.Float("Per Day", default=0.0)
    min_extra_hour = fields.Integer(
        "Minimum delay time before applying fines.", default=2,
    )

    # Default Rental Period Times
    default_pickup_time = fields.Float(
        "Default Pickup Time", default=9.0,
        help="Default time-of-day applied to a rental order's pickup datetime "
             "when only a date is provided (time component equals 00:00). "
             "Stored as hours since midnight (e.g. 9.0 = 09:00).",
    )
    default_return_time = fields.Float(
        "Default Return Time", default=23.983333,
        help="Default time-of-day applied to a rental order's return datetime "
             "when only a date is provided (time component equals 00:00). "
             "Stored as hours since midnight (e.g. 23.983 ≈ 23:59).",
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
    rental_deposit_product_id = fields.Many2one(
        'product.product',
        string="Rental Deposit Product",
        help="Product used for auto-created deposit lines on rental orders.",
        domain="[('is_rental_deposit', '=', True)]",
    )
    deposit_auto_refund = fields.Boolean(
        "Auto Refund Deposit",
        default=True,
        help="Automatically register a refund payment when a deposit credit note is created on return.",
    )

    # Rental Contract
    rental_contract_terms = fields.Html(
        string="Rental Contract Terms",
        company_dependent=True,
        help="Terms and conditions printed on rental contracts. Supports rich text formatting.",
    )

    # Pickup
    require_payment_before_pickup = fields.Boolean(
        "Require Payment Before Pickup",
        default=False,
        help="Block the pickup process until all posted customer invoices on the rental order are fully paid.",
    )
    auto_confirm_invoice = fields.Boolean(
        "Auto Confirm Invoice",
        default=True,
        help="Automatically confirm (post) invoices immediately after creation from a rental order, making them ready for payment.",
    )

    # Rental Inventory
    rental_loc_id = fields.Many2one(
        "stock.location", string="Rental Location",
        domain=[('usage', '=', 'internal')],
        help="Internal location for products currently in rental. "
             "Products remain in inventory valuation.",
    )
    damage_loc_id = fields.Many2one(
        "stock.location", string="Damage Location",
        domain=[('usage', '=', 'internal')],
        help="Internal location for products returned in damaged condition.",
    )
    inspection_loc_id = fields.Many2one(
        "stock.location", string="Inspection Location",
        domain=[('usage', '=', 'internal')],
        help="Internal location for products returned pending inspection.",
    )

    _min_extra_hour = models.Constraint(
        'CHECK(min_extra_hour >= 1)',
        "Minimal delay time before applying fines has to be positive.",
    )

    def _create_per_company_locations(self):
        super()._create_per_company_locations()
        self._create_rental_location()
        self._create_rental_support_locations()

    @api.model
    def create_missing_rental_location(self):
        companies = self.env['res.company'].search([('rental_loc_id', '=', False)])
        companies._create_rental_location()

    @api.model
    def create_missing_rental_support_locations(self):
        companies = self.env['res.company'].search([
            '|',
            ('damage_loc_id', '=', False),
            ('inspection_loc_id', '=', False),
        ])
        companies._create_rental_support_locations()

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

    def _create_rental_support_locations(self):
        """Create Damage and Inspection locations for companies missing them.

        Created as top-level locations (no parent) so they are outside the
        warehouse tree and excluded from bookable stock counts.
        stock.stock_location_locations was removed in Odoo 19.
        """
        damage_vals = []
        inspection_vals = []
        for company in self.sudo():
            if not company.damage_loc_id:
                damage_vals.append({
                    "name": self.env._("Damage"),
                    "usage": "internal",
                    "company_id": company.id,
                })
            if not company.inspection_loc_id:
                inspection_vals.append({
                    "name": self.env._("Inspection"),
                    "usage": "internal",
                    "company_id": company.id,
                })
        if damage_vals:
            damage_locs = self.env['stock.location'].sudo().create(damage_vals)
            company_damage_loc = {loc.company_id.id: loc for loc in damage_locs}
            for company in damage_locs.company_id:
                company.damage_loc_id = company_damage_loc.get(company.id, False)
        if inspection_vals:
            inspection_locs = self.env['stock.location'].sudo().create(inspection_vals)
            company_inspection_loc = {loc.company_id.id: loc for loc in inspection_locs}
            for company in inspection_locs.company_id:
                company.inspection_loc_id = company_inspection_loc.get(company.id, False)
