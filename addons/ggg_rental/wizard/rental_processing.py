from dateutil.relativedelta import relativedelta
from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class RentalOrderWizard(models.TransientModel):
    _name = 'rental.order.wizard'
    _description = "Pick-up/Return products"

    order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
    rental_wizard_line_ids = fields.One2many(
        'rental.order.wizard.line', 'rental_order_wizard_id',
    )
    status = fields.Selection(
        selection=[
            ('pickup', 'Pickup'),
            ('return', 'Return'),
        ],
    )
    is_late = fields.Boolean(compute='_compute_is_late')
    has_tracked_lines = fields.Boolean(compute='_compute_has_tracked_lines')

    @api.depends(
        'order_id.is_late',
        'order_id.next_action_date',
        'order_id.company_id.min_extra_hour',
    )
    def _compute_is_late(self):
        """Include the minimum time buffer allowed before an extra cost is added."""
        now = fields.Datetime.now()
        for wizard in self:
            min_extra_hours = relativedelta(
                hours=wizard.order_id.company_id.min_extra_hour,
            )
            wizard.is_late = (
                wizard.order_id.is_late
                and wizard.order_id.next_action_date + min_extra_hours < now
            )

    @api.depends('rental_wizard_line_ids.tracking')
    def _compute_has_tracked_lines(self):
        for wizard in self:
            wizard.has_tracked_lines = any(
                line.tracking == 'serial'
                for line in wizard.rental_wizard_line_ids
            )

    @api.onchange('order_id')
    def _get_wizard_lines(self):
        """Use Wizard lines to set by default the pickup/return value
        to the total pickup/return value expected."""
        rental_lines_ids = self.env.context.get('order_line_ids', [])
        rental_lines_to_process = self.env['sale.order.line'].browse(rental_lines_ids)

        if rental_lines_to_process:
            lines_values = []
            for line in rental_lines_to_process:
                lines_values.append(
                    self.env['rental.order.wizard.line']._default_wizard_line_vals(
                        line, self.status,
                    )
                )
            self.rental_wizard_line_ids = (
                [(6, 0, [])] + [(0, 0, vals) for vals in lines_values]
            )

    def apply(self):
        """Apply the wizard modifications to the SaleOrderLine(s).

        Logs the rental infos in the SaleOrder chatter.
        """
        for wizard in self:
            msg = wizard.rental_wizard_line_ids._apply()
            if msg:
                for key, value in wizard._fields['status']._description_selection(
                    wizard.env
                ):
                    if key == wizard.status:
                        translated_status = value
                        break

                msg = Markup("<b>%s</b>:<ul>%s</ul>") % (translated_status, msg)
                wizard.order_id.message_post(body=msg)


class RentalOrderWizardLine(models.TransientModel):
    _name = 'rental.order.wizard.line'
    _description = "RentalOrderLine transient representation"

    @api.model
    def _default_wizard_line_vals(self, line, status):
        vals = {
            'order_line_id': line.id,
            'product_id': line.product_id.id,
            'qty_reserved': line.product_uom_qty,
            'qty_delivered': (
                line.qty_delivered
                if status == 'return'
                else line.product_uom_qty - line.qty_delivered
            ),
            'qty_returned': (
                line.qty_returned
                if status == 'pickup'
                else line.qty_delivered - line.qty_returned
            ),
        }

        # Serial number support
        if line.product_id.tracking == 'serial' and line.product_id.type == 'consu':
            if status == 'pickup':
                # Show all serials available in stock (not currently rented out)
                stock_location = line.order_id.warehouse_id.lot_stock_id
                available_lots = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('lot_id', '!=', False),
                    ('location_id', 'child_of', stock_location.id),
                    ('quantity', '>', 0),
                ]).lot_id
                # Pre-select the lots reserved on the delivery move
                rental_loc = line.company_id.rental_loc_id
                pending_moves = line.move_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                    and m.location_dest_id == rental_loc
                )
                reserved_lots = pending_moves.move_line_ids.lot_id & available_lots
                pre_selected = reserved_lots[:int(vals['qty_delivered'])]
                vals['pickeable_lot_ids'] = [(6, 0, available_lots.ids)]
                vals['pickedup_lot_ids'] = [(6, 0, pre_selected.ids)]
                vals['qty_delivered'] = len(pre_selected)
            else:
                # Return: show lots that were picked up but not yet returned
                returnable = line.pickedup_lot_ids - line.returned_lot_ids
                pre_selected = returnable[:int(vals['qty_returned'])]
                vals['returnable_lot_ids'] = [(6, 0, returnable.ids)]
                vals['returned_lot_ids'] = [(6, 0, pre_selected.ids)]
                vals['qty_returned'] = len(pre_selected)

        return vals

    rental_order_wizard_id = fields.Many2one(
        'rental.order.wizard', 'Rental Order Wizard',
        required=True, ondelete='cascade',
    )
    status = fields.Selection(related='rental_order_wizard_id.status')

    order_line_id = fields.Many2one(
        'sale.order.line', required=True, ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, ondelete='cascade',
    )
    tracking = fields.Selection(related='product_id.tracking')
    qty_reserved = fields.Float("Reserved")
    qty_delivered = fields.Float("Picked-up")
    qty_returned = fields.Float("Returned")

    # Damage assessment fields (return only)
    condition = fields.Selection(
        selection=[('good', 'Good'), ('damaged', 'Damaged'), ('inspect', 'Inspect')],
        string="Condition",
        default='good',
    )
    damage_fee = fields.Float(string="Damage Fee")
    damage_reason = fields.Text(string="Damage Reason")

    # Serial number fields
    pickeable_lot_ids = fields.Many2many(
        'stock.lot', 'wizard_line_pickeable_lot_rel',
        string="Available Serials",
    )
    returnable_lot_ids = fields.Many2many(
        'stock.lot', 'wizard_line_returnable_lot_rel',
        string="Returnable Serials",
    )
    pickedup_lot_ids = fields.Many2many(
        'stock.lot', 'wizard_line_pickedup_lot_rel',
        string="Pickup Serials",
        domain="[('id', 'in', pickeable_lot_ids)]",
    )
    returned_lot_ids = fields.Many2many(
        'stock.lot', 'wizard_line_returned_lot_rel',
        string="Return Serials",
        domain="[('id', 'in', returnable_lot_ids)]",
    )

    @api.onchange('pickedup_lot_ids')
    def _onchange_pickedup_lot_ids(self):
        if self.tracking == 'serial':
            self.qty_delivered = len(self.pickedup_lot_ids)

    @api.onchange('returned_lot_ids')
    def _onchange_returned_lot_ids(self):
        if self.tracking == 'serial':
            self.qty_returned = len(self.returned_lot_ids)

    @api.constrains('qty_returned', 'qty_delivered')
    def _check_rental_quantities(self):
        for wizard_line in self:
            order_line = wizard_line.order_line_id
            if wizard_line.status == 'pickup':
                total_delivered = wizard_line.qty_delivered + order_line.qty_delivered
                if total_delivered > order_line.product_uom_qty:
                    raise ValidationError(
                        _("You can't pick up more than the reserved quantity.")
                    )
            elif wizard_line.status == 'return':
                total_returned = wizard_line.qty_returned + order_line.qty_returned
                if total_returned > order_line.qty_delivered:
                    raise ValidationError(
                        _("You can't return more than what's been picked-up.")
                    )

    def _get_return_dest_location(self, order_line):
        """Resolve the destination stock location for this return wizard line.

        Raises UserError if the required location is not configured.

        :param sale.order.line order_line: the rental line being returned
        :return: destination stock.location
        """
        company = order_line.company_id
        condition = self.condition
        if condition == 'damaged':
            if not company.damage_loc_id:
                raise UserError(_(
                    "Damage Location is not configured. "
                    "Please set it in Rental Settings before returning damaged products."
                ))
            return company.damage_loc_id
        elif condition == 'inspect':
            if not company.inspection_loc_id:
                raise UserError(_(
                    "Inspection Location is not configured. "
                    "Please set it in Rental Settings before sending products to inspection."
                ))
            return company.inspection_loc_id
        return order_line.order_id.warehouse_id.lot_stock_id

    def _apply(self):
        """Apply the wizard modifications to the SaleOrderLine.

        For return lines, orchestrates proper stock.picking creation:
          Phase 1 (pre-pass)  — validate destinations, create one Receipts picking per
                                unique destination location (grouped within this call).
          Phase 2 (main pass) — process each line; stock moves are created under the
                                pre-created picking via context.
          Phase 3 (post-pass) — validate each picking once all its moves are added.

        :return: message to log on the Sales Order.
        :rtype: str
        """
        msg = self._generate_log_message()

        # --- Phase 1: pre-pass — resolve destinations and create pickings ---
        # picking_map: {dest_location_id (int) → stock.picking}
        picking_map = {}
        return_lines = self.filtered(
            lambda wl: wl.status == 'return' and wl.qty_returned > 0
        )
        for wizard_line in return_lines:
            order_line = wizard_line.order_line_id
            dest = wizard_line._get_return_dest_location(order_line)  # raises if misconfigured
            if dest.id not in picking_map:
                order = order_line.order_id
                company = order_line.company_id
                picking_map[dest.id] = self.env['stock.picking'].create({
                    'picking_type_id': order.warehouse_id.in_type_id.id,
                    'origin': order.name,
                    'location_id': company.rental_loc_id.id,
                    'location_dest_id': dest.id,
                    'partner_id': order.partner_id.id,
                })

        # Flatten to {dest_id: picking.id} for passing via context
        picking_map_ids = {dest_id: picking.id for dest_id, picking in picking_map.items()}

        # --- Phase 2: main pass — process all wizard lines ---
        for wizard_line in self:
            order_line = wizard_line.order_line_id
            is_serial = wizard_line.tracking == 'serial'

            if wizard_line.status == 'pickup' and wizard_line.qty_delivered > 0:
                delivered_qty = order_line.qty_delivered + wizard_line.qty_delivered
                vals = {'qty_delivered': delivered_qty}
                if delivered_qty > order_line.product_uom_qty:
                    vals['product_uom_qty'] = delivered_qty
                if is_serial and wizard_line.pickedup_lot_ids:
                    vals['pickedup_lot_ids'] = [
                        (4, lot.id) for lot in wizard_line.pickedup_lot_ids
                    ]
                order_line.write(vals)

            elif wizard_line.status == 'return' and wizard_line.qty_returned > 0:
                if wizard_line.rental_order_wizard_id.is_late:
                    order_line._generate_delay_line(wizard_line.qty_returned)

                location_dest_id = wizard_line._get_return_dest_location(order_line)

                # Damage/inspection fee and log (charged immediately if fee > 0)
                if wizard_line.condition in ('damaged', 'inspect'):
                    wizard_line._process_damage(order_line)

                vals = {
                    'qty_returned': order_line.qty_returned + wizard_line.qty_returned,
                }
                if is_serial and wizard_line.returned_lot_ids:
                    vals['returned_lot_ids'] = [
                        (4, lot.id) for lot in wizard_line.returned_lot_ids
                    ]
                order_line.with_context(
                    rental_return_dest_id=location_dest_id.id,
                    rental_return_picking_map=picking_map_ids,
                ).write(vals)

        # --- Phase 3: post-pass — validate all return pickings ---
        for picking in picking_map.values():
            picking._action_done()

        return msg

    def _get_diff(self):
        """Return the quantity changes due to the wizard line.

        :return: (diff, old_qty, new_qty) floats
        :rtype: tuple(float, float, float)
        """
        self.ensure_one()
        order_line = self.order_line_id
        if self.status == 'pickup':
            return (
                self.qty_delivered,
                order_line.qty_delivered,
                order_line.qty_delivered + self.qty_delivered,
            )
        else:
            return (
                self.qty_returned,
                order_line.qty_returned,
                order_line.qty_returned + self.qty_returned,
            )

    def _process_damage(self, order_line):
        """Process damage assessment: create damage fee SO line and damage log records.

        :param sale.order.line order_line: the rental order line
        """
        self.ensure_one()
        is_serial = self.tracking == 'serial'

        # Create damage fee SO line
        if is_serial and self.returned_lot_ids:
            # One damage fee line per serial, split fee equally
            fee_per_lot = self.damage_fee / len(self.returned_lot_ids) if self.damage_fee else 0
            for lot in self.returned_lot_ids:
                order_line._generate_damage_line(fee_per_lot, self.damage_reason, lot=lot)
                self.env['rental.damage.log'].create({
                    'lot_id': lot.id,
                    'order_id': order_line.order_id.id,
                    'order_line_id': order_line.id,
                    'product_id': order_line.product_id.id,
                    'damage_fee': fee_per_lot,
                    'reason': self.damage_reason,
                })
        else:
            # Bulk product: single damage fee line, no lot
            order_line._generate_damage_line(self.damage_fee, self.damage_reason)
            self.env['rental.damage.log'].create({
                'lot_id': False,
                'order_id': order_line.order_id.id,
                'order_line_id': order_line.id,
                'product_id': order_line.product_id.id,
                'damage_fee': self.damage_fee,
                'reason': self.damage_reason,
            })

    def _generate_log_message(self):
        msg = ""
        for line in self:
            order_line = line.order_line_id
            diff, old_qty, new_qty = line._get_diff()
            if diff:
                msg += Markup("<li> %s") % (order_line.product_id.display_name)

                if old_qty > 0:
                    msg += Markup(": %s -> <b> %s </b> %s <br/>") % (
                        old_qty, new_qty, order_line.product_uom_id.name,
                    )
                elif new_qty != 1 or order_line.product_uom_qty > 1.0:
                    msg += Markup(": %s %s <br/>") % (
                        new_qty, order_line.product_uom_id.name,
                    )

                # Add serial numbers to log
                if line.tracking == 'serial':
                    lots = line.pickedup_lot_ids or line.returned_lot_ids
                    if lots:
                        lot_names = ", ".join(lots.mapped('name'))
                        msg += Markup(" [S/N: %s]") % lot_names
        return msg
