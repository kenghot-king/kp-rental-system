import base64
import io

from odoo import _, api, fields, models
from odoo.exceptions import UserError

MAX_DAYS = 90


class RentalDailyReconciliationPeriodReportWizard(models.TransientModel):
    _name = 'rental.daily.reconciliation.period.report.wizard'
    _description = 'Daily Reconciliation Period Report'

    date_from = fields.Date(string="From", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="To", required=True, default=fields.Date.context_today)
    cashier_ids = fields.Many2many('res.users', string="Cashiers (leave empty for all)")
    report_format = fields.Selection(
        [('xlsx', 'XLSX'), ('pdf', 'PDF')],
        string="Format",
        default='xlsx',
        required=True,
    )

    def _get_reconciliations(self):
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.cashier_ids:
            domain.append(('cashier_id', 'in', self.cashier_ids.ids))
        return self.env['rental.daily.reconciliation'].search(
            domain, order='cashier_id, date'
        )

    def _validate_date_range(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both date range fields."))
        delta = (self.date_to - self.date_from).days
        if delta < 0:
            raise UserError(_("'From' date must be before 'To' date."))
        if delta > MAX_DAYS:
            raise UserError(_(
                "Date range exceeds %(max)d days (limit is %(max)d days inclusive). "
                "Please narrow the range.",
                max=MAX_DAYS,
            ))

    def action_generate(self):
        self._validate_date_range()
        if self.report_format == 'xlsx':
            return self._generate_xlsx()
        return self._generate_pdf()

    def _generate_xlsx(self):
        try:
            import xlsxwriter as xlsxw
        except ImportError as exc:
            raise UserError(_("xlsxwriter is not installed.")) from exc

        recs = self._get_reconciliations()
        buf = io.BytesIO()
        wb = xlsxw.Workbook(buf, {'in_memory': True})
        ws = wb.add_worksheet('Reconciliations')

        bold = wb.add_format({'bold': True})
        headers = ['Date', 'Cashier', 'Expected Total', 'Actual Total', 'Variance', 'State']
        for col, h in enumerate(headers):
            ws.write(0, col, h, bold)

        row = 1
        state_labels = dict(self.env['rental.daily.reconciliation']._fields['state'].selection)
        for rec in recs:
            ws.write(row, 0, str(rec.date))
            ws.write(row, 1, rec.cashier_id.name or '')
            ws.write(row, 2, rec.expected_total)
            ws.write(row, 3, rec.actual_total)
            ws.write(row, 4, rec.variance_total)
            ws.write(row, 5, state_labels.get(rec.state, rec.state))
            row += 1

        wb.close()
        xlsx_data = buf.getvalue()

        attachment = self.env['ir.attachment'].create({
            'name': f'Reconciliations_{self.date_from}_{self.date_to}.xlsx',
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

    def _generate_pdf(self):
        recs = self._get_reconciliations()
        if not recs:
            raise UserError(_("No reconciliation records found for the selected period."))
        return self.env.ref(
            'ggg_rental.action_report_reconciliation_period_pdf'
        ).report_action(recs)
