from odoo import fields, models


class QaScenarioLog(models.Model):
    _name = 'qa.scenario.log'
    _description = 'QA Scenario Log'
    _order = 'applied_at desc'

    scenario_id = fields.Many2one('qa.scenario', required=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', required=True, ondelete='cascade', string='Order')
    field_changed = fields.Char(readonly=True)
    original_value = fields.Datetime(string='Original Date', readonly=True)
    new_value = fields.Datetime(string='Mutated Date', readonly=True)
    applied_by = fields.Many2one('res.users', readonly=True)
    applied_at = fields.Datetime(readonly=True)
    reverted = fields.Boolean(default=False, readonly=True)
