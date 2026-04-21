from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_rental_supervisor = fields.Boolean(
        string="Rental Supervisor",
        compute='_compute_is_rental_supervisor',
        inverse='_inverse_is_rental_supervisor',
    )

    def _compute_is_rental_supervisor(self):
        group = self.env.ref('ggg_rental.group_rental_supervisor')
        for user in self:
            user.is_rental_supervisor = group in user.group_ids

    def _inverse_is_rental_supervisor(self):
        group = self.env.ref('ggg_rental.group_rental_supervisor')
        for user in self:
            if user.is_rental_supervisor:
                user.sudo().group_ids |= group
            else:
                user.sudo().group_ids -= group
