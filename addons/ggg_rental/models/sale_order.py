import logging
import pytz
from dateutil.relativedelta import relativedelta
from math import ceil

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command, Domain
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


RENTAL_STATUS = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('pickup', "Reserved"),
    ('return', "Pickedup"),
    ('returned', "Returned"),
    ('cancel', "Cancelled"),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _rental_period_coherence = models.Constraint(
        'CHECK(rental_start_date < rental_return_date)',
        "The rental start date must be before the rental return date if any.",
    )

    @api.model
    def default_get(self, fields):
        """Override to map relevant default `sale.order.line` fields to `sale.order` fields.

        Mainly used to create a new rental order from the rental schedule view, as it works on
        `sale.order.line` records.
        """
        defaults = super().default_get(fields)

        if self.env.context.get('convert_default_order_line_values'):
            missing_fields = set(fields) - defaults.keys()

            SO_TO_SOL_FIELDS_MAPPING = [
                ('partner_id', 'order_partner_id'),
                ('rental_start_date', 'start_date'),
                ('rental_return_date', 'return_date'),
            ]
            for so_fname, sol_fname in SO_TO_SOL_FIELDS_MAPPING:
                if so_fname in missing_fields and (
                    default_value := self.env.context.get(f'default_{sol_fname}')
                ):
                    defaults[so_fname] = default_value

            if 'order_line' in missing_fields:
                defaults['order_line'] = [self._build_default_order_line_values()]

            # Convert added default values to the right format
            for fname in defaults.keys() & missing_fields:
                field = self._fields[fname]
                value = field.convert_to_cache(defaults[fname], self, validate=False)
                defaults[fname] = field.convert_to_write(value, self)

        return defaults

    def _build_default_order_line_values(self):
        """Generate default values for `sale.order.line` based on context keys prefixed with
        'default_'."""
        default_field_names = (
            key.replace('default_', '', 1)
            for key in self.env.context
            if key.startswith('default_')
        )
        sol_field_names = (
            field_name
            for field_name in default_field_names
            if field_name in self.env['sale.order.line']._fields
        )

        return {
            'product_uom_qty': 1.0,
            **{
                field_name: self.env.context[f'default_{field_name}']
                for field_name in sol_field_names
            },
        }

    #=== FIELDS ===#

    is_rental_order = fields.Boolean(
        string="Created In App Rental",
        compute='_compute_is_rental_order',
        store=True, precompute=True, readonly=False,
        default=lambda self: self.env.context.get('in_rental_app'),
    )
    has_rented_products = fields.Boolean(compute='_compute_has_rented_products')
    rental_start_date = fields.Datetime(string="Rental Start Date", tracking=True)
    rental_return_date = fields.Datetime(string="Rental Return Date", tracking=True)
    duration_days = fields.Integer(
        string="Duration in days",
        compute='_compute_duration',
        help="The duration in days of the rental period.",
    )
    remaining_hours = fields.Integer(
        string="Remaining duration in hours",
        compute='_compute_duration',
        help="The leftover hours of the rental period.",
    )
    show_update_duration = fields.Boolean(
        string="Has Duration Changed", store=False,
    )

    rental_status = fields.Selection(
        selection=RENTAL_STATUS,
        string="Rental Status",
        compute='_compute_rental_status',
        store=True,
    )
    next_action_date = fields.Datetime(
        string="Next Action",
        compute='_compute_rental_status',
        store=True,
    )

    has_pickable_lines = fields.Boolean(compute='_compute_has_action_lines')
    has_returnable_lines = fields.Boolean(compute='_compute_has_action_lines')

    is_late = fields.Boolean(
        string="Is overdue",
        help="The products haven't been picked-up or returned in time."
             " This excludes any grace period before late fees apply.",
        compute='_compute_is_late',
        search='_search_is_late',
    )

    rental_completion = fields.Selection(
        selection=[('complete', "Complete"), ('incomplete', "Incomplete")],
        string="Completion",
        compute='_compute_rental_completion',
        store=True,
    )
    rental_completion_detail = fields.Char(
        string="Completion Detail",
        compute='_compute_rental_completion',
    )

    rental_stock_move_count = fields.Integer(
        string="Rental Stock Moves",
        compute='_compute_rental_stock_move_count',
    )

    rental_lines_subtotal = fields.Monetary(
        string="Rental Lines Subtotal",
        compute='_compute_rental_contract_totals',
        currency_field='currency_id',
    )
    deposit_lines_subtotal = fields.Monetary(
        string="Deposit Lines Subtotal",
        compute='_compute_rental_contract_totals',
        currency_field='currency_id',
    )

    #=== COMPUTE METHODS ===#

    @api.depends('order_line.is_rental')
    def _compute_is_rental_order(self):
        for order in self:
            order.is_rental_order = order.is_rental_order or order.has_rented_products

    @api.depends('order_line.is_rental')
    def _compute_has_rented_products(self):
        for so in self:
            so.has_rented_products = any(line.is_rental for line in so.order_line)

    @api.depends('rental_start_date', 'rental_return_date')
    def _compute_duration(self):
        self.duration_days = 0
        self.remaining_hours = 0
        for order in self:
            if order.rental_start_date and order.rental_return_date:
                duration = order.rental_return_date - order.rental_start_date
                order.duration_days = duration.days
                order.remaining_hours = ceil(duration.seconds / 3600)

    @api.depends(
        'rental_start_date',
        'rental_return_date',
        'state',
        'order_line.is_rental',
        'order_line.product_uom_qty',
        'order_line.qty_delivered',
        'order_line.qty_returned',
    )
    def _compute_rental_status(self):
        self.next_action_date = False
        for order in self:
            if not order.is_rental_order:
                order.rental_status = False
            elif order.state != 'sale':
                order.rental_status = order.state
            elif order.has_returnable_lines:
                order.rental_status = 'return'
                order.next_action_date = order.rental_return_date
            elif order.has_pickable_lines:
                order.rental_status = 'pickup'
                order.next_action_date = order.rental_start_date
            else:
                order.rental_status = 'returned'

    @api.depends(
        'is_rental_order',
        'state',
        'order_line.is_rental',
        'order_line.product_uom_qty',
        'order_line.qty_delivered',
        'order_line.qty_returned',
    )
    def _compute_has_action_lines(self):
        self.has_pickable_lines = False
        self.has_returnable_lines = False
        for order in self:
            if order.state == 'sale' and order.is_rental_order:
                rental_order_lines = order.order_line.filtered(
                    lambda line: line.is_rental and line.product_type != 'combo'
                )
                order.has_pickable_lines = any(
                    sol.qty_delivered < sol.product_uom_qty
                    for sol in rental_order_lines
                )
                order.has_returnable_lines = any(
                    sol.qty_returned < sol.qty_delivered
                    for sol in rental_order_lines
                )

    @api.depends('is_rental_order', 'next_action_date', 'rental_status')
    def _compute_is_late(self):
        now = fields.Datetime.now()
        for order in self:
            order.is_late = (
                order.is_rental_order
                and order.rental_status in ['pickup', 'return']
                and order.next_action_date
                and order.next_action_date < now
            )

    def _compute_rental_stock_move_count(self):
        move_data = self.env['stock.move']._read_group(
            [('sale_line_id.order_id', 'in', self.ids), ('sale_line_id.is_rental', '=', True)],
            groupby=['sale_line_id'],
            aggregates=['__count'],
        )
        # Group by order
        counts = {}
        for sol, count in move_data:
            order_id = sol.order_id.id
            counts[order_id] = counts.get(order_id, 0) + count
        for order in self:
            order.rental_stock_move_count = counts.get(order.id, 0)

    def action_view_rental_stock_moves(self):
        self.ensure_one()
        moves = self.env['stock.move'].search([
            ('sale_line_id.order_id', '=', self.id),
            ('sale_line_id.is_rental', '=', True),
        ])
        action = {
            'name': _("Rental Stock Moves"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', moves.ids)],
            'context': {'create': False},
        }
        if len(moves) == 1:
            action.update(view_mode='form', res_id=moves.id)
        return action

    @api.depends('order_line.price_subtotal', 'order_line.is_rental', 'order_line.deposit_parent_id')
    def _compute_rental_contract_totals(self):
        for order in self:
            rental = order.order_line.filtered(lambda l: l.is_rental and not l.deposit_parent_id)
            deposit = order.order_line.filtered(lambda l: bool(l.deposit_parent_id))
            order.rental_lines_subtotal = sum(rental.mapped('price_subtotal'))
            order.deposit_lines_subtotal = sum(deposit.mapped('price_subtotal'))

    @api.depends(
        'is_rental_order',
        'state',
        'order_line.qty_delivered',
        'order_line.qty_returned',
        'order_line.is_rental',
    )
    def _compute_rental_completion(self):
        for order in self:
            if not order.is_rental_order or order.state != 'sale':
                order.rental_completion = False
                order.rental_completion_detail = False
                continue

            # Axis 1: Returned
            rental_lines = order.order_line.filtered('is_rental')
            total_delivered = sum(rental_lines.mapped('qty_delivered'))
            total_returned = sum(rental_lines.mapped('qty_returned'))
            all_returned = total_returned >= total_delivered and total_delivered > 0

            # Axis 2: Paid (posted out_invoices, excluding deposit invoices)
            deposit_invoices = order._get_deposit_invoices()
            deposit_invoice_ids = set(deposit_invoices.ids)
            non_deposit_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted'
                and inv.move_type == 'out_invoice'
                and inv.id not in deposit_invoice_ids
            )
            total_invoices = len(non_deposit_invoices)
            paid_invoices = len(non_deposit_invoices.filtered(
                lambda inv: inv.payment_state == 'paid'
            ))
            all_paid = paid_invoices >= total_invoices

            # Axis 3: Deposit refunded
            if deposit_invoices:
                total_deposit_amount = sum(deposit_invoices.mapped('amount_total'))
                total_refunded = 0.0
                for dep_inv in deposit_invoices:
                    credits = dep_inv.reversal_move_ids.filtered(
                        lambda m: m.state != 'cancel'
                    )
                    total_refunded += sum(abs(c.amount_total) for c in credits)
                all_deposit_refunded = total_refunded >= total_deposit_amount
            else:
                total_deposit_amount = 0.0
                total_refunded = 0.0
                all_deposit_refunded = True

            # Completion status
            if all_returned and all_paid and all_deposit_refunded:
                order.rental_completion = 'complete'
                order.rental_completion_detail = False
            else:
                order.rental_completion = 'incomplete'
                detail_parts = [
                    _("Returned: %(returned)s/%(total)s",
                      returned=int(total_returned), total=int(total_delivered)),
                    _("Paid: %(paid)s/%(total)s",
                      paid=paid_invoices, total=total_invoices),
                ]
                if deposit_invoices:
                    detail_parts.append(
                        _("Deposit refunded: %(refunded)s/%(total)s",
                          refunded=f"{total_refunded:,.0f}",
                          total=f"{total_deposit_amount:,.0f}")
                    )
                order.rental_completion_detail = '\n'.join(detail_parts)

    def _get_deposit_invoices(self):
        """Return posted out_invoices that contain deposit product lines."""
        self.ensure_one()
        return self.invoice_ids.filtered(
            lambda inv: inv.state == 'posted'
            and inv.move_type == 'out_invoice'
            and any(l.product_id.is_rental_deposit for l in inv.invoice_line_ids)
        )

    def _recompute_rental_completion(self):
        """Trigger recomputation of rental_completion for this recordset."""
        self.env.add_to_compute(
            self._fields['rental_completion'], self,
        )

    #=== SEARCH METHODS ===#

    def _search_is_late(self, operator, value):
        if operator != 'in' and True not in value:
            return NotImplemented

        return Domain([
            ('is_rental_order', '=', True),
            ('rental_status', 'in', ('pickup', 'return')),
            ('next_action_date', '!=', False),
            ('next_action_date', '<', 'now'),
        ])

    #=== ONCHANGE METHODS ===#

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id_show_update_prices(self):
        """Override of `sale` to not show the "Update Prices" button when creating a new order
        from the rental schedule."""
        if (
            self.env.context.get('in_rental_schedule')
            and self.env.context.get('sale_onchange_first_call')
        ):
            return
        return super()._onchange_pricelist_id_show_update_prices()

    @api.onchange('company_id')
    def _onchange_company_id_warning(self):
        """Override of `sale` to not show the "Update Prices" button when creating a new order
        from the rental schedule."""
        if (
            self.env.context.get('in_rental_schedule')
            and self.env.context.get('sale_onchange_first_call')
        ):
            return
        return super()._onchange_company_id_warning()

    @api.onchange('rental_start_date', 'rental_return_date')
    def _onchange_duration_show_update_duration(self):
        if (
            self.env.context.get('in_rental_schedule')
            and self.env.context.get('sale_onchange_first_call')
        ):
            return
        self.show_update_duration = any(line.is_rental for line in self.order_line)

    @api.onchange('is_rental_order')
    def _onchange_is_rental_order(self):
        self.ensure_one()
        if self.is_rental_order:
            self._rental_set_dates()

    @api.onchange('rental_start_date')
    def _onchange_rental_start_date(self):
        if self.rental_start_date:
            snapped = self._snap_time_to_default(
                self.rental_start_date, self.company_id.default_pickup_time,
            )
            if snapped != self.rental_start_date:
                self.rental_start_date = snapped
        self.order_line.filtered('is_rental')._compute_name()

    @api.onchange('rental_return_date')
    def _onchange_rental_return_date(self):
        if self.rental_return_date:
            snapped = self._snap_time_to_default(
                self.rental_return_date, self.company_id.default_return_time,
            )
            if snapped != self.rental_return_date:
                self.rental_return_date = snapped
        self.order_line.filtered('is_rental')._compute_name()

    def _snap_time_to_default(self, dt, default_hours):
        """Snap dt's time component to default_hours when it equals 00:00:00 in user's TZ.

        Treats a midnight time as a date-only pick from the date picker; any other
        time is considered a deliberate user choice and returned unchanged.
        """
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        local = pytz.UTC.localize(dt).astimezone(tz)
        if local.hour or local.minute or local.second:
            return dt
        total_minutes = round(default_hours * 60)
        hours, minutes = divmod(total_minutes, 60)
        snapped_local = local.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        return snapped_local.astimezone(pytz.UTC).replace(tzinfo=None)

    #=== ACTION METHODS ===#

    def action_update_rental_prices(self):
        self.ensure_one()
        self._recompute_rental_prices()
        self.message_post(body=_("Rental prices have been recomputed with the new period."))

    def _recompute_rental_prices(self):
        self.with_context(rental_recompute_price=True)._recompute_prices()

    def _get_update_prices_lines(self):
        """Exclude non-rental lines from price recomputation."""
        lines = super()._get_update_prices_lines()
        if not self.env.context.get('rental_recompute_price'):
            return lines
        return lines.filtered('is_rental')

    def action_open_pickup(self):
        self.ensure_one()
        if self.company_id.require_payment_before_pickup:
            posted_invoices = self.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
            )
            if not posted_invoices:
                raise UserError(_("Cannot process pickup: no invoice has been issued for this order."))
            unpaid = posted_invoices.filtered(lambda inv: inv.payment_state != 'paid')
            if unpaid:
                raise UserError(_(
                    "Cannot process pickup: the following invoice(s) are not fully paid: %s",
                    ', '.join(unpaid.mapped('name'))
                ))
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        lines_to_pickup = self.order_line.filtered(
            lambda r: (
                r.is_rental
                and r.product_type != 'combo'
                and float_compare(
                    r.product_uom_qty, r.qty_delivered, precision_digits=precision,
                ) > 0
            )
        )
        return self._open_rental_wizard('pickup', lines_to_pickup.ids)

    def action_open_return(self):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        lines_to_return = self.order_line.filtered(
            lambda r: (
                r.is_rental
                and r.product_type != 'combo'
                and float_compare(
                    r.qty_delivered, r.qty_returned, precision_digits=precision,
                ) > 0
            )
        )
        return self._open_rental_wizard('return', lines_to_return.ids)

    def _open_rental_wizard(self, status, order_line_ids):
        context = {
            'order_line_ids': order_line_ids,
            'default_status': status,
            'default_order_id': self.id,
        }
        return {
            'name': _('Validate a pickup') if status == 'pickup' else _('Validate a return'),
            'view_mode': 'form',
            'res_model': 'rental.order.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def _get_portal_return_action(self):
        """Return the action used to display orders when returning from customer portal."""
        if self.is_rental_order:
            return self.env.ref('ggg_rental.rental_order_action')
        else:
            return super()._get_portal_return_action()

    def _get_product_catalog_domain(self):
        domain = super()._get_product_catalog_domain()
        if self.is_rental_order:
            return domain | Domain([
                ('rent_ok', '=', True),
                ('company_id', 'in', [self.company_id.id, False]),
                ('type', '!=', 'combo'),
            ])
        return domain

    #=== TOOLING ===#

    def _rental_set_dates(self):
        self.ensure_one()
        if self.rental_start_date and self.rental_return_date:
            return

        tz = pytz.timezone(self.env.user.tz or 'UTC')
        now_local = pytz.UTC.localize(fields.Datetime.now()).astimezone(tz)

        pickup_h, pickup_m = divmod(round(self.company_id.default_pickup_time * 60), 60)
        return_h, return_m = divmod(round(self.company_id.default_return_time * 60), 60)

        start_local = now_local.replace(hour=pickup_h, minute=pickup_m, second=0, microsecond=0)
        if start_local <= now_local:
            start_local += relativedelta(days=1)
        return_local = (start_local + relativedelta(days=1)).replace(
            hour=return_h, minute=return_m, second=0, microsecond=0,
        )

        self.update({
            'rental_start_date': start_local.astimezone(pytz.UTC).replace(tzinfo=None),
            'rental_return_date': return_local.astimezone(pytz.UTC).replace(tzinfo=None),
        })

    def _action_cancel(self):
        """Auto-return rented stock before cancellation."""
        for order in self:
            if not order.is_rental_order or order.state != 'sale':
                continue
            for line in order.order_line.filtered(
                lambda l: l.is_rental and l.product_id.type == 'consu'
            ):
                outstanding_qty = line.qty_delivered - line.qty_returned
                if outstanding_qty <= 0:
                    continue
                lot_ids = None
                if line.product_id.tracking == 'serial':
                    lot_ids = line.pickedup_lot_ids - line.returned_lot_ids
                line.with_company(line.company_id)._create_rental_return(
                    outstanding_qty, lot_ids=lot_ids,
                )
        return super()._action_cancel()

    #=== INVOICING ===#

    def _get_invoiceable_lines(self, final=False):
        """Filter invoiceable lines based on deposit split context.

        Deposit lines that already have a posted out_invoice are always excluded,
        regardless of context. This prevents duplicate deposit invoices after a
        deposit credit note has been issued (the credit note reduces qty_invoiced
        back to zero, making the deposit line appear invoiceable again).
        """
        lines = super()._get_invoiceable_lines(final=final)

        if self.env.context.get('_rental_exclude_deposit'):
            return lines.filtered(
                lambda l: l.display_type or not l.product_id.is_rental_deposit
            )

        # Helper: True if this deposit line was already invoiced (posted out_invoice exists)
        def _deposit_already_invoiced(l):
            return l.product_id.is_rental_deposit and bool(
                l.invoice_lines.filtered(
                    lambda il: il.move_id.state == 'posted'
                    and il.move_id.move_type == 'out_invoice'
                )
            )

        if self.env.context.get('_rental_deposit_only'):
            return lines.filtered(
                lambda l: (l.display_type or l.product_id.is_rental_deposit)
                and not _deposit_already_invoiced(l)
            )

        # Default path: exclude deposit lines that are already invoiced
        return lines.filtered(lambda l: not _deposit_already_invoiced(l))

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Split deposit and non-deposit lines into separate invoices."""
        if self.env.context.get('_rental_deposit_splitting'):
            return super()._create_invoices(grouped=grouped, final=final, date=date)

        # Check if any SO has mixed deposit + non-deposit invoiceable lines.
        # Deposit lines that already have a posted invoice are excluded from the
        # split check (mirrors the _get_invoiceable_lines guard) to avoid an
        # unnecessary split that would produce an empty deposit-only invoice batch.
        precision = self.env['decimal.precision'].precision_get('Product Unit')
        needs_split = False
        for order in self:
            lines = order.order_line.filtered(
                lambda l: not l.display_type
                and not float_is_zero(l.qty_to_invoice, precision_digits=precision)
            )
            has_deposit = any(
                l.product_id.is_rental_deposit
                and not l.invoice_lines.filtered(
                    lambda il: il.move_id.state == 'posted'
                    and il.move_id.move_type == 'out_invoice'
                )
                for l in lines
            )
            has_non_deposit = any(not l.product_id.is_rental_deposit for l in lines)
            if has_deposit and has_non_deposit:
                needs_split = True
                break

        if not needs_split:
            invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        else:
            ctx = {'_rental_deposit_splitting': True}
            rental_invoices = self.with_context(
                **ctx, _rental_exclude_deposit=True,
            )._create_invoices(grouped=grouped, final=final, date=date)
            deposit_invoices = self.with_context(
                **ctx, _rental_deposit_only=True,
            )._create_invoices(grouped=grouped, final=final, date=date)
            invoices = rental_invoices | deposit_invoices

        self._auto_confirm_rental_invoices(invoices)
        return invoices

    def _auto_confirm_rental_invoices(self, invoices):
        """Auto-post invoices that originated from rental orders if the setting is enabled."""
        company = self.env.company
        if not company.auto_confirm_invoice:
            return

        rental_order_ids = self.filtered('is_rental_order').ids
        if not rental_order_ids:
            return

        to_post = invoices.filtered(
            lambda inv: inv.state == 'draft' and any(
                line.sale_line_ids.order_id.id in rental_order_ids
                for line in inv.invoice_line_ids
            )
        )
        for invoice in to_post:
            try:
                invoice.action_post()
            except Exception as e:
                _logger.warning(
                    "Auto-confirm failed for invoice %s: %s", invoice.name, e
                )

    #=== DEPOSIT SYNC ===#

    def action_sync_deposits(self):
        """Create, update, or remove deposit lines to match rental lines."""
        self.ensure_one()
        deposit_product = self.company_id.rental_deposit_product_id
        if not deposit_product:
            raise UserError(_(
                "No rental deposit product configured. "
                "Please set a Rental Deposit Product in Rental Settings."
            ))

        rental_lines = self.order_line.filtered(
            lambda l: l.is_rental and l.product_id.rent_ok and not l.deposit_parent_id
        )
        deposit_lines = self.order_line.filtered(lambda l: l.deposit_parent_id)

        # Build map: parent line id → deposit line
        deposit_map = {dl.deposit_parent_id.id: dl for dl in deposit_lines}

        # Remove orphaned deposit lines
        rental_ids = set(rental_lines.ids)
        orphaned = deposit_lines.filtered(lambda l: l.deposit_parent_id.id not in rental_ids)
        if orphaned:
            orphaned.unlink()

        for line in rental_lines:
            expected_price = line.product_id.product_tmpl_id.with_company(self.company_id).deposit_price
            expected_qty = line.product_uom_qty
            deposit = deposit_map.get(line.id)

            expected_tax_ids = deposit_product.taxes_id.ids

            if deposit:
                # Always write price_unit explicitly to prevent _compute_price_unit
                # from resetting it when other fields (e.g. qty) are written.
                update_vals = {'price_unit': expected_price}
                if deposit.product_uom_qty != expected_qty:
                    update_vals['product_uom_qty'] = expected_qty
                if deposit.tax_ids.ids != expected_tax_ids:
                    update_vals['tax_ids'] = [Command.set(expected_tax_ids)]
                if deposit.name != _("[Deposit] %(product)s", product=line.product_id.name):
                    update_vals['name'] = _("[Deposit] %(product)s", product=line.product_id.name)
                deposit.write(update_vals)
            else:
                # Create missing deposit line
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': deposit_product.id,
                    'name': _("[Deposit] %(product)s", product=line.product_id.name),
                    'price_unit': expected_price,
                    'product_uom_qty': expected_qty,
                    'tax_ids': [Command.set(expected_tax_ids)],
                    'deposit_parent_id': line.id,
                    'sequence': line.sequence + 1,
                    'is_rental': False,
                })

    def _check_deposit_sync(self):
        """Check if deposit lines are in sync with rental lines.

        :return: list of mismatch descriptions, or False if in sync
        """
        self.ensure_one()
        if not self.is_rental_order:
            return False

        deposit_product = self.company_id.rental_deposit_product_id
        if not deposit_product:
            return [_("No rental deposit product configured in Rental Settings.")]

        rental_lines = self.order_line.filtered(
            lambda l: l.is_rental and l.product_id.rent_ok and not l.deposit_parent_id
        )
        deposit_lines = self.order_line.filtered(lambda l: l.deposit_parent_id)
        deposit_map = {dl.deposit_parent_id.id: dl for dl in deposit_lines}

        mismatches = []

        # Check orphaned deposits
        rental_ids = set(rental_lines.ids)
        for dl in deposit_lines:
            if dl.deposit_parent_id.id not in rental_ids:
                mismatches.append(_("Orphaned deposit line: %(name)s", name=dl.name))

        # Check each rental line
        for line in rental_lines:
            deposit = deposit_map.get(line.id)
            if not deposit:
                mismatches.append(_(
                    "%(product)s: no deposit line",
                    product=line.product_id.name,
                ))
            else:
                if deposit.product_uom_qty != line.product_uom_qty:
                    mismatches.append(_(
                        "%(product)s: deposit qty %(dep_qty)s ≠ rental qty %(rent_qty)s",
                        product=line.product_id.name,
                        dep_qty=int(deposit.product_uom_qty),
                        rent_qty=int(line.product_uom_qty),
                    ))

        return mismatches or False

    def _open_deposit_sync_wizard(self, original_action, mismatches):
        """Open the deposit sync wizard with mismatch info."""
        self.ensure_one()
        wizard = self.env['rental.deposit.sync.wizard'].create({
            'order_id': self.id,
            'original_action': original_action,
            'mismatch_info': '\n'.join('• ' + m for m in mismatches),
        })
        return {
            'name': _("Deposit Data Changed"),
            'type': 'ir.actions.act_window',
            'res_model': 'rental.deposit.sync.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _check_deposit_before_action(self, action_name):
        """Check deposits and return wizard or False."""
        self.ensure_one()
        if self.env.context.get('_skip_deposit_check'):
            return False
        if not self.is_rental_order:
            return False
        mismatches = self._check_deposit_sync()
        if mismatches:
            return self._open_deposit_sync_wizard(action_name, mismatches)
        return False

    def action_quotation_send(self):
        wizard = self._check_deposit_before_action('action_quotation_send')
        if wizard:
            return wizard
        return super().action_quotation_send()

    def action_confirm(self):
        for order in self:
            if order.is_rental_order:
                order.action_check_rental_availability()
            wizard = order._check_deposit_before_action('action_confirm')
            if wizard:
                return wizard
        return super().action_confirm()

    def action_check_rental_availability(self):
        """Validate that all rental lines fit currently available stock.

        Groups rental lines by product within the order, sums quantities, and
        compares each product's order-total against the warehouse-scoped
        free_qty. Skips service products. Raises ValidationError on the first
        overbooked product encountered.
        """
        self.ensure_one()
        if not self.is_rental_order:
            return True

        warehouse = self.warehouse_id or self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1,
        )
        if not warehouse:
            return True

        qty_per_product = {}
        for line in self.order_line:
            if not line.is_rental or not line.product_id:
                continue
            if line.product_id.type == 'service':
                continue
            qty_per_product.setdefault(line.product_id, 0.0)
            qty_per_product[line.product_id] += line.product_uom_qty

        for product, requested_qty in qty_per_product.items():
            available = product.with_context(warehouse_id=warehouse.id).free_qty
            if float_compare(
                requested_qty, available, precision_rounding=product.uom_id.rounding,
            ) <= 0:
                continue
            sample_line = self.order_line.filtered(
                lambda l, p=product: l.is_rental and l.product_id == p
            )[:1]
            raise ValidationError(sample_line._get_availability_error_message(
                requested_qty=requested_qty,
                available_qty=available,
                warehouse=warehouse,
            ))
        return True

    def action_preview_sale_order(self):
        wizard = self._check_deposit_before_action('action_preview_sale_order')
        if wizard:
            return wizard
        return super().action_preview_sale_order()

    def action_print_rental(self):
        """Custom print action that validates deposits before printing."""
        self.ensure_one()
        wizard = self._check_deposit_before_action('action_print_rental')
        if wizard:
            return wizard
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    def action_print_rental_contract(self):
        """Print the rental contract. Blocked until the order is at least pickup-ready."""
        self.ensure_one()
        if self.rental_status not in ('pickup', 'return', 'returned'):
            raise UserError(_(
                "The rental contract can only be printed once the order is confirmed and reserved. "
                "Please confirm the order first."
            ))
        return self.env.ref('ggg_rental.action_report_rental_contract').report_action(self)

    #=== BUSINESS METHODS ===#

    def _get_product_catalog_order_data(self, products, **kwargs):
        """Override to add the rental dates for the price computation."""
        return super()._get_product_catalog_order_data(
            products,
            start_date=self.rental_start_date,
            end_date=self.rental_return_date,
            **kwargs,
        )

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        """Override to add context to mark the line as rental and rental dates for pricing."""
        if self.is_rental_order:
            self = self.with_context(in_rental_app=True)
            product = self.env['product.product'].browse(product_id)
            if product.rent_ok:
                self._rental_set_dates()
        return super()._update_order_line_info(
            product_id,
            quantity,
            start_date=self.rental_start_date,
            end_date=self.rental_return_date,
            **kwargs,
        )

    def _get_action_add_from_catalog_extra_context(self):
        """Override to add rental dates in the context for product availabilities."""
        extra_context = super()._get_action_add_from_catalog_extra_context()
        extra_context.update(
            start_date=self.rental_start_date,
            end_date=self.rental_return_date,
        )
        return extra_context
