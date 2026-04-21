import base64
import io

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class RentalDailyReconciliation(models.Model):
    _name = 'rental.daily.reconciliation'
    _description = 'Daily Payment Reconciliation'
    _inherit = ['mail.thread']
    _order = 'date desc, cashier_id'

    name = fields.Char(string="Reference", compute='_compute_name', store=True)

    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    cashier_id = fields.Many2one(
        'res.users',
        string="Cashier",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed')],
        string="State",
        default='draft',
        required=True,
        tracking=True,
    )
    note = fields.Text(string="Note")
    confirmed_by = fields.Many2one('res.users', string="Confirmed By", readonly=True)
    confirmed_at = fields.Datetime(string="Confirmed At", readonly=True)
    reopened_by = fields.Many2one('res.users', string="Reopened By", readonly=True)
    reopened_at = fields.Datetime(string="Reopened At", readonly=True)

    line_ids = fields.One2many(
        'rental.daily.reconciliation.line',
        'reconciliation_id',
        string="Lines",
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        compute='_compute_currency_id',
        store=True,
    )
    expected_total = fields.Monetary(
        string="Expected Total",
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    actual_total = fields.Monetary(
        string="Actual Total",
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    variance_total = fields.Monetary(
        string="Variance",
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )

    _sql_constraints = [
        ('unique_cashier_date', 'UNIQUE(cashier_id, date)',
         'A reconciliation already exists for this cashier and date.'),
    ]

    @api.depends('cashier_id', 'date')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.cashier_id.name or '?'} – {str(rec.date) if rec.date else '?'}"

    @api.depends_context('company')
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.env.company.currency_id

    @api.depends('line_ids.expected_amount', 'line_ids.actual_amount', 'line_ids.variance')
    def _compute_totals(self):
        for rec in self:
            rec.expected_total = sum(rec.line_ids.mapped('expected_amount'))
            rec.actual_total = sum(l.actual_amount or 0.0 for l in rec.line_ids)
            rec.variance_total = sum(l.variance for l in rec.line_ids)

    def _check_supervisor(self):
        if not self.env.user.has_group('ggg_rental.group_rental_supervisor'):
            raise UserError(_("Only rental supervisors can perform this action."))

    def _rebuild_lines(self):
        self.ensure_one()
        payments = self.env['account.payment'].search([
            ('cashier_id', '=', self.cashier_id.id),
            ('date', '=', self.date),
            ('state', 'in', ['in_process', 'paid']),
            ('reconciliation_id', 'in', [False, self.id]),
        ])
        groups = {}
        for p in payments:
            key = (p.display_method or '', p.journal_id.id)
            if key not in groups:
                groups[key] = self.env['account.payment']
            groups[key] |= p

        self.line_ids.unlink()
        for (display_method, journal_id), pmts in groups.items():
            self.env['rental.daily.reconciliation.line'].create({
                'reconciliation_id': self.id,
                'display_method': display_method,
                'journal_id': journal_id,
                'payment_ids': [(6, 0, pmts.ids)],
            })

    def action_rebuild_lines(self):
        for rec in self:
            rec._rebuild_lines()
        return True

    def action_confirm(self):
        self._check_supervisor()
        for rec in self:
            if rec.state != 'draft':
                continue
            incomplete = [l for l in rec.line_ids if not l.actual_entered]
            if incomplete:
                raise UserError(_(
                    "Reconciliation '%(name)s' has lines without actual amount entered. "
                    "Please enter actual amounts for all lines before confirming.",
                    name=rec.name,
                ))
            all_payments = rec.line_ids.mapped('payment_ids')
            all_payments.sudo().write({'reconciliation_id': rec.id})
            rec.write({
                'state': 'confirmed',
                'confirmed_by': self.env.user.id,
                'confirmed_at': fields.Datetime.now(),
            })
            rec.message_post(body=_(
                "Reconciliation confirmed by %s.", self.env.user.name,
            ))

    def action_reopen(self):
        self._check_supervisor()
        for rec in self:
            if rec.state != 'confirmed':
                continue
            rec.write({
                'state': 'draft',
                'reopened_by': self.env.user.id,
                'reopened_at': fields.Datetime.now(),
            })
            rec.line_ids.mapped('payment_ids').sudo().write({'reconciliation_id': False})
            rec.message_post(body=_(
                "Reconciliation reopened by %s.", self.env.user.name,
            ))

    def action_confirm_multi(self):
        self._check_supervisor()
        incomplete_names = []
        for rec in self:
            if rec.state != 'draft':
                continue
            if any(not l.actual_entered for l in rec.line_ids):
                incomplete_names.append(rec.name)
        if incomplete_names:
            raise UserError(_(
                "Cannot confirm: the following reconciliations have lines without actual amount:\n%s\n\n"
                "Please complete all lines before confirming.",
                '\n'.join(f"  • {n}" for n in incomplete_names),
            ))
        for rec in self:
            if rec.state == 'draft':
                rec.action_confirm()

    def action_report_reconciliation_pdf(self):
        return self.env.ref('ggg_rental.action_report_reconciliation_pdf').report_action(self)

    def action_print_xlsx(self):
        self.ensure_one()
        try:
            import xlsxwriter as xlsxw
        except ImportError as exc:
            raise UserError(_("xlsxwriter is not installed.")) from exc

        buf = io.BytesIO()
        wb = xlsxw.Workbook(buf, {'in_memory': True})
        ws = wb.add_worksheet('Reconciliation')

        bold = wb.add_format({'bold': True})
        headers = ['Date', 'Cashier', 'State', 'Method', 'Journal',
                   'Expected', 'Actual', 'Variance']
        for col, h in enumerate(headers):
            ws.write(0, col, h, bold)

        row = 1
        for line in self.line_ids:
            ws.write(row, 0, str(self.date))
            ws.write(row, 1, self.cashier_id.name or '')
            ws.write(row, 2, dict(self._fields['state'].selection).get(self.state, ''))
            ws.write(row, 3, line.display_method or '')
            ws.write(row, 4, line.journal_id.name or '')
            ws.write(row, 5, line.expected_amount)
            ws.write(row, 6, line.actual_amount or 0.0)
            ws.write(row, 7, line.variance)
            row += 1

        row += 1
        ws.write(row, 4, 'TOTAL', bold)
        ws.write(row, 5, self.expected_total)
        ws.write(row, 6, self.actual_total)
        ws.write(row, 7, self.variance_total)

        wb.close()
        xlsx_data = buf.getvalue()

        attachment = self.env['ir.attachment'].create({
            'name': f'Reconciliation_{self.cashier_id.name}_{self.date}.xlsx',
            'datas': base64.b64encode(xlsx_data).decode(),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }


class RentalDailyReconciliationLine(models.Model):
    _name = 'rental.daily.reconciliation.line'
    _description = 'Daily Reconciliation Line'
    _order = 'journal_id, display_method'

    reconciliation_id = fields.Many2one(
        'rental.daily.reconciliation',
        string="Reconciliation",
        required=True,
        ondelete='cascade',
        index=True,
    )
    display_method = fields.Char(string="Method")
    journal_id = fields.Many2one('account.journal', string="Journal", index=True)

    payment_ids = fields.Many2many(
        'account.payment',
        'rental_recon_line_payment_rel',
        'line_id',
        'payment_id',
        string="Payments",
    )

    currency_id = fields.Many2one(
        related='reconciliation_id.currency_id',
        store=True,
    )
    expected_amount = fields.Monetary(
        string="Expected",
        compute='_compute_expected_amount',
        store=True,
        currency_field='currency_id',
    )
    actual_amount = fields.Monetary(
        string="Actual",
        currency_field='currency_id',
    )
    actual_entered = fields.Boolean(string="Amount Entered", default=False)
    variance = fields.Monetary(
        string="Variance",
        compute='_compute_variance',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('payment_ids.amount')
    def _compute_expected_amount(self):
        for line in self:
            line.expected_amount = sum(line.payment_ids.mapped('amount'))

    @api.depends('actual_amount', 'expected_amount')
    def _compute_variance(self):
        for line in self:
            line.variance = (line.actual_amount or 0.0) - line.expected_amount

    def write(self, vals):
        if 'actual_amount' in vals:
            vals = dict(vals, actual_entered=True)
        return super().write(vals)


class RentalDailyReconciliationNeeded(models.Model):
    _name = 'rental.daily.reconciliation.needed'
    _description = 'Unreconciled Payment Tuples'
    _auto = False
    _order = 'payment_date desc, cashier_id'

    cashier_id = fields.Many2one('res.users', string="Cashier", readonly=True)
    payment_date = fields.Date(string="Date", readonly=True)
    payment_count = fields.Integer(string="# Payments", readonly=True)
    total_amount = fields.Float(string="Total Amount", digits=(16, 2), readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # reconciliation_id column may not yet exist on first install (ORM ordering).
        # _post_init_rental calls init() again after all columns are created.
        self.env.cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'account_payment' AND column_name = 'reconciliation_id'
        """)
        has_col = bool(self.env.cr.fetchone())
        recon_filter = "AND ap.reconciliation_id IS NULL" if has_col else ""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY ap.cashier_id, am.date) AS id,
                    ap.cashier_id,
                    am.date AS payment_date,
                    COUNT(ap.id) AS payment_count,
                    SUM(ap.amount) AS total_amount
                FROM account_payment ap
                JOIN account_move am ON am.id = ap.move_id
                WHERE am.state = 'posted'
                    AND ap.cashier_id IS NOT NULL
                    %s
                GROUP BY ap.cashier_id, am.date
            )
        """ % (self._table, recon_filter))

    def action_create_reconciliation(self):
        self.ensure_one()
        existing = self.env['rental.daily.reconciliation'].search([
            ('cashier_id', '=', self.cashier_id.id),
            ('date', '=', self.payment_date),
        ], limit=1)
        if existing:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'rental.daily.reconciliation',
                'res_id': existing.id,
                'view_mode': 'form',
                'target': 'current',
            }
        recon = self.env['rental.daily.reconciliation'].create({
            'cashier_id': self.cashier_id.id,
            'date': self.payment_date,
        })
        recon._rebuild_lines()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rental.daily.reconciliation',
            'res_id': recon.id,
            'view_mode': 'form',
            'target': 'current',
        }
