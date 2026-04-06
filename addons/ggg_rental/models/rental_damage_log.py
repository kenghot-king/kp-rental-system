from odoo import fields, models


class RentalDamageLog(models.Model):
    _name = 'rental.damage.log'
    _description = "Rental Damage Log"
    _order = 'date desc'

    lot_id = fields.Many2one(
        'stock.lot', string="Serial Number", ondelete='set null',
    )
    order_id = fields.Many2one(
        'sale.order', string="Rental Order", required=True, ondelete='cascade',
    )
    order_line_id = fields.Many2one(
        'sale.order.line', string="Order Line", required=True, ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product', string="Product", required=True, ondelete='cascade',
    )
    damage_fee = fields.Float(string="Damage Fee")
    reason = fields.Text(string="Reason")
    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)
    user_id = fields.Many2one(
        'res.users', string="Assessed By", default=lambda self: self.env.uid,
    )
