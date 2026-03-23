from datetime import timedelta
from pytz import UTC, timezone

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command, Domain
from odoo.tools import format_datetime, format_time
from odoo.tools.sql import SQL


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_id = fields.Many2one(group_expand='_read_group_expand_product_id')

    order_is_rental = fields.Boolean(
        related='order_id.is_rental_order', depends=['order_id'],
    )

    is_rental = fields.Boolean(
        compute='_compute_is_rental',
        store=True, precompute=True, readonly=False, copy=True,
    )

    qty_returned = fields.Float("Returned", default=0.0, copy=False)
    start_date = fields.Datetime(
        related='order_id.rental_start_date', readonly=False,
    )
    return_date = fields.Datetime(
        related='order_id.rental_return_date', readonly=False,
    )
    reservation_begin = fields.Datetime(
        string="Pickup date - padding time",
        compute='_compute_reservation_begin',
        store=True,
    )

    is_product_rentable = fields.Boolean(
        related='product_id.rent_ok', depends=['product_id'],
    )

    # Serial number tracking for rentals
    tracking = fields.Selection(related='product_id.tracking', depends=['product_id'])
    pickedup_lot_ids = fields.Many2many(
        'stock.lot',
        'rental_pickedup_lot_rel',
        domain="[('product_id', '=', product_id)]",
        copy=False,
    )
    returned_lot_ids = fields.Many2many(
        'stock.lot',
        'rental_returned_lot_rel',
        domain="[('product_id', '=', product_id)]",
        copy=False,
    )

    # Technical computed fields for UX purposes
    is_late = fields.Boolean(related='order_id.is_late')
    team_id = fields.Many2one(related='order_id.team_id')
    country_id = fields.Many2one(related='order_id.partner_id.country_id')
    rental_status = fields.Selection(
        selection=[
            ('pickup', "Booked"),
            ('return', "Picked-Up"),
            ('returned', "Returned"),
        ],
        compute='_compute_rental_status',
        search='_search_rental_status',
    )
    rental_color = fields.Integer(compute='_compute_rental_color')

    def _domain_product_id(self):
        super_part = ','.join(str(leaf) for leaf in super()._domain_product_id())
        rent_part = "'&', ('rent_ok', '=', True), ('rent_ok', '=', order_is_rental)"
        return f"['|', {rent_part}, {super_part}]"

    @api.depends('order_partner_id.name', 'order_id.name', 'product_id.name')
    @api.depends_context('sale_renting_short_display_name')
    def _compute_display_name(self):
        if not self.env.context.get('sale_renting_short_display_name'):
            return super()._compute_display_name()
        for sol in self:
            descriptions = []
            group_by = self.env.context.get('group_by', [])

            if 'partner_id' not in group_by:
                descriptions.append(sol.order_partner_id.display_name)
            if 'product_id' not in group_by:
                descriptions.append(sol.product_id.name)
            descriptions.append(sol.order_id.name)

            sol.display_name = ", ".join(descriptions)

    @api.depends('order_id.rental_start_date')
    def _compute_reservation_begin(self):
        lines = self.filtered('is_rental')
        for line in lines:
            line.reservation_begin = line.order_id.rental_start_date
        (self - lines).reservation_begin = None

    @api.onchange('qty_delivered')
    def _onchange_qty_delivered(self):
        """When picking up more than reserved, reserved qty is updated."""
        if self.qty_delivered > self.product_uom_qty:
            self.product_uom_qty = self.qty_delivered

    @api.depends('is_rental')
    def _compute_qty_delivered_method(self):
        """Allow modification of delivered qty without depending on stock moves."""
        rental_lines = self.filtered('is_rental')
        super(SaleOrderLine, self - rental_lines)._compute_qty_delivered_method()
        rental_lines.qty_delivered_method = 'manual'

    @api.depends('is_rental')
    def _compute_name(self):
        """Override to add the compute dependency."""
        super()._compute_name()

    @api.depends('product_id')
    def _compute_is_rental(self):
        for line in self:
            line.is_rental = (
                line.is_product_rentable and line.env.context.get('in_rental_app')
            )

    @api.depends('is_rental')
    def _compute_product_updatable(self):
        rental_lines = self.filtered('is_rental')
        super(SaleOrderLine, self - rental_lines)._compute_product_updatable()
        rental_lines.product_updatable = True

    def _compute_pricelist_item_id(self):
        """Discard pricelist item computation for rental lines.

        This disables the standard discount computation because no pricelist rule was found.
        """
        rental_lines = self.filtered('is_rental')
        super(SaleOrderLine, self - rental_lines)._compute_pricelist_item_id()
        rental_lines.pricelist_item_id = False

    @api.depends('product_uom_qty', 'qty_delivered', 'qty_returned')
    def _compute_rental_status(self):
        self.rental_status = False
        for sol in self.filtered('order_is_rental'):
            if sol.qty_delivered < sol.product_uom_qty:
                sol.rental_status = 'pickup'
            elif (
                sol.qty_returned >= sol.qty_delivered
                and sol.qty_delivered >= sol.product_uom_qty
            ):
                sol.rental_status = 'returned'
            else:
                sol.rental_status = 'return'

    @api.depends('order_is_rental', 'state', 'rental_status', 'is_late')
    def _compute_rental_color(self):
        self.rental_color = 0
        for sol in self.filtered('order_is_rental'):
            if sol.state in ('draft', 'sent'):
                sol.rental_color = 5  # purple
                continue
            match sol.rental_status:
                case 'pickup':
                    sol.rental_color = 3 if sol.is_late else 4  # yellow if late else blue
                case 'return':
                    sol.rental_color = 6 if sol.is_late else 2  # red if late else orange
                case 'returned':
                    sol.rental_color = 7  # green

    def _search_rental_status(self, operator, values):
        if operator != 'in':
            return NotImplemented

        return (
            (Domain('order_is_rental', '=', False) if False in values else Domain.FALSE)
            | (
                Domain([('order_is_rental', '=', True)])
                & Domain.custom(to_sql=lambda model, alias, query: SQL(
                    """
                    CASE
                        WHEN %(qty_delivered)s < %(product_uom_qty)s THEN 'pickup'
                        WHEN (
                            %(qty_returned)s >= %(qty_delivered)s
                            AND %(qty_delivered)s >= %(product_uom_qty)s
                        ) THEN 'returned'
                        ELSE 'return'
                    END IN %(values)s
                    """,
                    product_uom_qty=model._field_to_sql(alias, 'product_uom_qty', query),
                    qty_delivered=model._field_to_sql(alias, 'qty_delivered', query),
                    qty_returned=model._field_to_sql(alias, 'qty_returned', query),
                    values=tuple(values),
                ))
            )
        )

    def _read_group_expand_product_id(self, products, domain):
        if not self.env.context.get('in_rental_schedule'):
            return self.env['product.product']

        expanded_products = self.env['product.product'].search(
            Domain([
                ('id', 'not in', products.ids),
                ('rent_ok', '=', True),
                ('type', '!=', 'combo'),
            ]),
            limit=80 - len(products),
        )
        return products + expanded_products

    def web_gantt_write(self, vals):
        """Updates the sale order line and performs necessary validations.

        Also recalculates rental prices if the duration changes.

        :param dict vals: Dictionary of values to update.
        :raises UserError: If the order is already picked up and start date is changed.
        :raises UserError: If the order is already returned and end date is changed.
        :return: A dictionary containing notifications and/or actions.
        :rtype: dict
        """
        self.ensure_one()
        result = {'notifications': [], 'actions': []}

        if self.order_id.rental_status in ('return', 'returned') and 'start_date' in vals:
            raise UserError(self.env._("The order is already picked-up."))
        if self.order_id.rental_status == 'returned' and 'return_date' in vals:
            raise UserError(self.env._("The order is already returned."))

        updating_duration = 'start_date' in vals or 'return_date' in vals
        old_duration = self.return_date - self.start_date if updating_duration else None

        if not self.write(vals):
            raise UserError(self.env._("An error occured. Please try again."))

        if updating_duration:
            new_duration = self.return_date - self.start_date
            if old_duration != new_duration:
                self.order_id.order_line.filtered('is_rental')._compute_name()
                self.order_id.action_update_rental_prices()
                result['notifications'].append({
                    'type': 'success',
                    'message': self.env._("The rental prices have been updated."),
                    'code': 'rental_price_update',
                })

        return result

    def _get_sale_order_line_multiline_description_sale(self):
        """Add Rental information to the SaleOrderLine name."""
        res = super()._get_sale_order_line_multiline_description_sale()
        if self.is_rental:
            self.order_id._rental_set_dates()
            res += self._get_rental_order_line_description()
        return res

    def _get_rental_order_line_description(self):
        tz = self._get_tz()
        start_date = self.order_id.rental_start_date
        return_date = self.order_id.rental_return_date
        env = self.with_context(use_babel=True).env

        if (
            start_date and return_date
            and start_date.replace(tzinfo=UTC).astimezone(timezone(tz)).date()
                == return_date.replace(tzinfo=UTC).astimezone(timezone(tz)).date()
        ):
            return_date_part = format_time(env, return_date, tz=tz, time_format='short')
        else:
            return_date_part = format_datetime(env, return_date, tz=tz, dt_format='short')
        start_date_part = format_datetime(env, start_date, tz=tz, dt_format='short')
        return _(
            "\n%(from_date)s to %(to_date)s",
            from_date=start_date_part,
            to_date=return_date_part,
        )

    def _use_template_name(self):
        """Avoid the template line description to add the rental period on the SOL."""
        if self.is_rental:
            return False
        return super()._use_template_name()

    def _generate_delay_line(self, qty_returned):
        """Generate a sale order line representing the delay cost due to the late return.

        :param float qty_returned: returned quantity
        """
        self.ensure_one()

        self = self.with_company(self.company_id)
        now = fields.Datetime.now()

        if self.return_date + timedelta(hours=self.company_id.min_extra_hour) >= now:
            return

        duration = now - self.return_date
        delay_price = self.product_id._compute_delay_price(duration)
        if delay_price <= 0.0:
            return

        delay_product = self.company_id.extra_product
        if not delay_product:
            delay_product = self.env['product.product'].with_context(
                active_test=False,
            ).search(
                [('default_code', '=', 'RENTAL'), ('type', '=', 'service')],
                limit=1,
            )
            if not delay_product:
                delay_product = self.env['product.product'].create({
                    "name": "Rental Delay Cost",
                    "standard_price": 0.0,
                    "type": 'service',
                    "default_code": "RENTAL",
                    "purchase_ok": False,
                })
            self.company_id.extra_product = delay_product

        if not delay_product.active:
            return

        delay_price = self._convert_to_sol_currency(
            delay_price, self.product_id.currency_id,
        )

        order_line_vals = self._prepare_delay_line_vals(
            delay_product, delay_price * qty_returned,
        )

        self.order_id.write({
            'order_line': [Command.create(order_line_vals)],
        })

    def _prepare_delay_line_vals(self, delay_product, delay_price):
        """Prepare values of delay line.

        :param product.product delay_product: Product used for the delay_line
        :param float delay_price: Price of the delay line
        :return: sale.order.line creation values
        :rtype: dict
        """
        delay_line_description = self._get_delay_line_description()
        return {
            'name': delay_line_description,
            'product_id': delay_product.id,
            'product_uom_qty': 1,
            'qty_delivered': 1,
            'price_unit': delay_price,
        }

    def _get_delay_line_description(self):
        tz = self._get_tz()
        env = self.with_context(use_babel=True).env
        expected_date = format_datetime(env, self.return_date, tz=tz, dt_format=False)
        now = format_datetime(env, fields.Datetime.now(), tz=tz, dt_format=False)
        return "%s\n%s\n%s" % (
            self.product_id.name,
            _("Expected: %(date)s", date=expected_date),
            _("Returned: %(date)s", date=now),
        )

    def _get_tz(self):
        return self.env.context.get('tz') or self.env.user.tz or 'UTC'

    def _get_pricelist_price(self):
        """Custom price computation for rental lines.

        The displayed price will only be the price given by the product.pricing rules matching
        the given line information (product, period, pricelist, ...).
        """
        self.ensure_one()
        if self.is_rental:
            self.order_id._rental_set_dates()
            return self.order_id.pricelist_id._get_product_price(
                self.product_id.with_context(**self._get_product_price_context()),
                self.product_uom_qty or 1.0,
                currency=self.currency_id,
                uom=self.product_uom_id,
                date=self.order_id.date_order or fields.Date.today(),
                start_date=self.start_date,
                end_date=self.return_date,
            )
        return super()._get_pricelist_price()

    # === RENTAL NOTES === #

    RENTAL_NOTES_MARKER = '\n---'

    def _get_rental_notes(self):
        """Build pickup/return note text from current state."""
        self.ensure_one()
        lines = []
        if self.qty_delivered > 0:
            if self.product_id.tracking == 'serial' and self.pickedup_lot_ids:
                lines.append(_("Picked up: %(serials)s", serials=', '.join(self.pickedup_lot_ids.mapped('name'))))
            else:
                qty = int(self.qty_delivered) if self.qty_delivered == int(self.qty_delivered) else self.qty_delivered
                lines.append(_("Picked up: %(qty)s", qty=qty))
        if self.qty_returned > 0:
            if self.product_id.tracking == 'serial' and self.returned_lot_ids:
                lines.append(_("Returned: %(serials)s", serials=', '.join(self.returned_lot_ids.mapped('name'))))
            else:
                qty = int(self.qty_returned) if self.qty_returned == int(self.qty_returned) else self.qty_returned
                lines.append(_("Returned: %(qty)s", qty=qty))
        return '\n'.join(lines)

    def _update_rental_notes(self):
        """Rebuild the notes portion of the name field."""
        for sol in self:
            if not sol.is_rental or not sol.name:
                continue
            # Strip existing notes (everything after marker)
            base_name = sol.name.split(sol.RENTAL_NOTES_MARKER)[0]
            notes = sol._get_rental_notes()
            if notes:
                sol.name = base_name + sol.RENTAL_NOTES_MARKER + '\n' + notes
            else:
                sol.name = base_name

    # === STOCK MOVE METHODS === #

    def write(self, vals):
        """Handle rental stock operations when qty_delivered/qty_returned change.

        Pickup: validates the existing delivery picking (created on SO confirmation).
        Return: creates and validates a new return picking.
        Also updates the line description with pickup/return notes.
        """
        rental_keys = ('qty_delivered', 'qty_returned', 'pickedup_lot_ids', 'returned_lot_ids')
        if not any(key in vals for key in rental_keys):
            return super().write(vals)

        old_vals = {}
        movable_lines = self.filtered(
            lambda sol: sol.is_rental
                and sol.state == 'sale'
                and sol.product_id.type == 'consu'
        )
        for sol in movable_lines:
            old_vals[sol.id] = {
                'qty_delivered': sol.qty_delivered,
                'qty_returned': sol.qty_returned,
                'pickedup_lot_ids': sol.pickedup_lot_ids,
                'returned_lot_ids': sol.returned_lot_ids,
            }

        res = super().write(vals)

        for sol in movable_lines:
            sol = sol.with_company(sol.company_id)
            old = old_vals[sol.id]

            # Pickup: validate existing delivery picking
            if sol.qty_delivered > old['qty_delivered']:
                lot_ids = sol.pickedup_lot_ids if sol.product_id.tracking == 'serial' else None
                sol._validate_rental_pickup(lot_ids=lot_ids)

            # Return: create and validate a new return picking
            if sol.qty_returned > old['qty_returned']:
                qty = sol.qty_returned - old['qty_returned']
                if sol.product_id.tracking == 'serial':
                    lot_ids = sol.returned_lot_ids - old['returned_lot_ids']
                else:
                    lot_ids = None
                sol._create_rental_return(qty, lot_ids=lot_ids)

        # Update line descriptions with pickup/return notes
        rental_lines = self.filtered(lambda sol: sol.is_rental and sol.state == 'sale')
        rental_lines._update_rental_notes()

        return res

    def _validate_rental_pickup(self, lot_ids=None):
        """Validate the existing delivery picking for this rental line.

        For serial-tracked products, assigns the given lot_ids to move lines.
        """
        self.ensure_one()
        moves = self.move_ids.filtered(
            lambda m: m.state not in ('done', 'cancel')
            and m.location_dest_id == self.company_id.rental_loc_id
        )
        if not moves:
            return

        if lot_ids:
            # Assign serial numbers to move lines
            for move in moves:
                move.move_line_ids.unlink()
                for lot in lot_ids:
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': lot.id,
                        'quantity': 1,
                        'picked': True,
                    })

        for move in moves:
            if not lot_ids:
                move.quantity = move.product_uom_qty
            move.picked = True
        moves._action_done()

    def _create_rental_return(self, qty, lot_ids=None):
        """Create and validate a return move (Rental Location → WH/Stock).

        :param float qty: quantity to return
        :param stock.lot lot_ids: specific lots to return (for serial-tracked products)
        """
        self.ensure_one()
        rented_location = self.company_id.rental_loc_id
        stock_location = self.order_id.warehouse_id.lot_stock_id

        rental_stock_move = self.env['stock.move'].create({
            'product_id': self.product_id.id,
            'product_uom_qty': qty,
            'product_uom': self.product_id.uom_id.id,
            'location_id': rented_location.id,
            'location_dest_id': stock_location.id,
            'partner_id': self.order_partner_id.id,
            'sale_line_id': self.id,
        })
        rental_stock_move._action_confirm(merge=False)
        rental_stock_move._action_assign()

        if lot_ids:
            rental_stock_move.move_line_ids.unlink()
            for lot in lot_ids:
                self.env['stock.move.line'].create({
                    'move_id': rental_stock_move.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_id.uom_id.id,
                    'location_id': rented_location.id,
                    'location_dest_id': stock_location.id,
                    'lot_id': lot.id,
                    'quantity': 1,
                    'picked': True,
                })
        else:
            rental_stock_move.quantity = qty

        rental_stock_move.picked = True
        rental_stock_move.move_line_ids.picked = True
        rental_stock_move._action_done()

    def _get_location_final(self):
        """Redirect rental lines to the Rental Location instead of Customer."""
        self.ensure_one()
        if self.is_rental:
            if not self.company_id.rental_loc_id:
                self.company_id._create_rental_location()
            return self.company_id.rental_loc_id
        return super()._get_location_final()

    def _action_launch_stock_rule(self, **kwargs):
        """Let rental lines go through normal stock rule flow for reservation."""
        super()._action_launch_stock_rule(**kwargs)
