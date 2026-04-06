from odoo import _, fields, models


class StockLot(models.Model):
    _inherit = 'stock.lot'

    damage_log_ids = fields.One2many(
        'rental.damage.log', 'lot_id', string="Damage History",
    )
    damage_count = fields.Integer(
        string="Damage Count", compute='_compute_damage_count',
    )

    def _compute_damage_count(self):
        damage_data = self.env['rental.damage.log']._read_group(
            [('lot_id', 'in', self.ids)],
            ['lot_id'],
            ['__count'],
        )
        counts = {lot.id: count for lot, count in damage_data}
        for lot in self:
            lot.damage_count = counts.get(lot.id, 0)

    def action_view_damage_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Damage History"),
            'res_model': 'rental.damage.log',
            'view_mode': 'list,form',
            'domain': [('lot_id', '=', self.id)],
            'context': {'default_lot_id': self.id},
        }
