from ast import literal_eval
from datetime import timedelta

from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestByItemReport(AccountTestInvoicingCommon):
    """Tests for credit notes in the Reporting > By Item report."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data['company']
        cls.company.deposit_auto_refund = False
        cls.tax_vat = cls.env['account.tax'].create({
            'name': "VAT 7% (By Item)",
            'amount': 7.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': cls.company.id,
        })
        cls.rental_product = cls.env['product.product'].create({
            'name': "By Item Rental",
            'type': 'service',
            'rent_ok': True,
            'invoice_policy': 'order',
            'taxes_id': [Command.set(cls.tax_vat.ids)],
            'deposit_price': 1000.0,
        })
        cls.deposit_product = cls.env['product.product'].create({
            'name': "By Item Deposit",
            'type': 'service',
            'is_rental_deposit': True,
            'invoice_policy': 'order',
        })
        # sudo: also clears default taxes of other companies in the test database.
        cls.deposit_product.sudo().taxes_id = [Command.clear()]
        cls.company.rental_deposit_product_id = cls.deposit_product
        cls.action = cls.env.ref('ggg_rental.action_rental_invoice_by_item')
        cls.report_domain = literal_eval(cls.action.domain)

        # The test user is an accountant with no sales access, like a user who
        # only checks this report, so the order is created with sudo.
        now = fields.Datetime.now()
        cls.order = cls.env['sale.order'].sudo().create({
            'partner_id': cls.partner_a.id,
            'is_rental_order': True,
            'rental_start_date': now,
            'rental_return_date': now + timedelta(days=1),
            'order_line': [
                Command.create({
                    'product_id': cls.rental_product.id,
                    'product_uom_qty': 1,
                    'price_unit': 300.0,
                    'tax_ids': [Command.set(cls.tax_vat.ids)],
                    'is_rental': True,
                }),
            ],
        })
        cls.rental_line = cls.order.order_line
        cls.order.action_sync_deposits()
        cls.order.action_confirm()
        invoices = cls.order._create_invoices().with_env(cls.env)
        invoices.filtered(lambda m: m.state == 'draft').action_post()
        cls.rental_invoice = invoices.filtered(lambda m: not m.is_deposit_invoice)
        cls.deposit_invoice = invoices.filtered('is_deposit_invoice')

    def _report_lines(self, moves):
        return self.env['account.move.line'].search(
            self.report_domain + [('move_id', 'in', moves.ids)],
        )

    def _manual_credit_note(self, invoice):
        """Create a draft credit note through the core reversal wizard."""
        reversal = self.env['account.move.reversal'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'journal_id': invoice.journal_id.id,
            'date': fields.Date.today(),
            'reason': "By Item test",
        })
        reversal.refund_moves()
        return reversal.new_move_ids

    def _add_deposit_hold(self, hold_state):
        return self.env['account.payment'].create({
            'is_deposit_hold': True,
            'hold_state': hold_state,
            'deposit_invoice_id': self.deposit_invoice.id,
            'partner_id': self.partner_a.id,
            'journal_id': self.company_data['default_journal_bank'].id,
            'amount': self.deposit_invoice.amount_total,
            'payment_type': 'inbound',
            'partner_type': 'customer',
        })

    def _order_credit_notes(self):
        return self.env['account.move.line'].search(
            self.report_domain + [
                ('sale_order_id', '=', self.order.id),
                ('move_id.move_type', '=', 'out_refund'),
            ],
        )

    # ── Signed amounts ────────────────────────────────────────────────────────

    def test_invoice_amounts_are_positive(self):
        line = self._report_lines(self.rental_invoice)
        self.assertEqual(line.signed_subtotal, 300.0)
        self.assertEqual(line.signed_tax_amount, 21.0)

    def test_full_credit_note_nets_to_zero(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()

        line = self._report_lines(credit_note)
        self.assertEqual(line.signed_subtotal, -300.0)
        self.assertEqual(line.signed_tax_amount, -21.0)

        lines = self._report_lines(self.rental_invoice | credit_note)
        self.assertEqual(sum(lines.mapped('signed_subtotal')), 0.0)
        self.assertEqual(sum(lines.mapped('signed_tax_amount')), 0.0)

    def test_partial_credit_note_nets_to_remainder(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.invoice_line_ids.price_unit = 100.0
        credit_note.action_post()

        lines = self._report_lines(self.rental_invoice | credit_note)
        self.assertEqual(sum(lines.mapped('signed_subtotal')), 200.0)
        self.assertEqual(sum(lines.mapped('signed_tax_amount')), 14.0)

    def test_grouped_totals_are_net(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()

        groups = self.env['account.move.line']._read_group(
            self.report_domain + [
                ('move_id', 'in', (self.rental_invoice | credit_note).ids),
            ],
            groupby=['sale_order_id'],
            aggregates=['signed_subtotal:sum', 'signed_tax_amount:sum'],
        )
        self.assertEqual(groups, [(self.order, 0.0, 0.0)])

    def test_credit_note_keeps_printed_quantity_and_unit_price(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()

        line = self._report_lines(credit_note)
        self.assertEqual(line.quantity, 1.0)
        self.assertEqual(line.price_unit, 300.0)

    # ── Order and original invoice ────────────────────────────────────────────

    def test_invoice_shows_order(self):
        line = self._report_lines(self.rental_invoice)
        self.assertEqual(line.sale_order_id, self.order)

    def test_automatic_deposit_credit_note_shows_order(self):
        self.rental_line._create_deposit_credit_note(1, 1)

        line = self._order_credit_notes()
        self.assertEqual(len(line), 1)
        self.assertEqual(line.signed_subtotal, -1000.0)
        self.assertEqual(line.reversed_entry_id, self.deposit_invoice)

    def test_manual_credit_note_shows_order(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()

        self.assertEqual(self._report_lines(credit_note).sale_order_id, self.order)

    def test_user_without_sales_access_can_read_order(self):
        self.assertFalse(self.env.user.has_group('sales_team.group_sale_salesman'))

        order_value = self._report_lines(self.rental_invoice).read(['sale_order_id'])[0]
        self.assertEqual(
            order_value['sale_order_id'],
            (self.order.id, self.order.sudo().display_name),
        )

    def test_document_without_order_is_listed_with_empty_order(self):
        invoice = self.init_invoice('out_invoice', amounts=[100.0], post=True)

        line = self._report_lines(invoice)
        self.assertEqual(len(line), 1)
        self.assertFalse(line.sale_order_id)

    def test_credit_note_shows_original_invoice(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()

        self.assertEqual(
            self._report_lines(credit_note).reversed_entry_id,
            self.rental_invoice,
        )

    def test_credited_invoice_has_no_reversal_value(self):
        self._manual_credit_note(self.rental_invoice).action_post()

        self.assertFalse(self._report_lines(self.rental_invoice).reversed_entry_id)

    def test_credit_note_without_original_invoice_is_listed(self):
        credit_note = self.init_invoice('out_refund', amounts=[50.0], post=True)

        line = self._report_lines(credit_note)
        self.assertEqual(line.signed_subtotal, -50.0)
        self.assertFalse(line.reversed_entry_id)

    # ── Report contents ───────────────────────────────────────────────────────

    def test_report_excludes_other_journal_items_and_vendor_documents(self):
        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()
        vendor_bill = self.init_invoice('in_invoice', amounts=[100.0], post=True)

        self.assertEqual(
            set(self._report_lines(self.rental_invoice | credit_note).mapped('display_type')),
            {'product'},
        )
        self.assertEqual(len(self._report_lines(self.rental_invoice)), 1)
        self.assertEqual(len(self._report_lines(credit_note)), 1)
        self.assertFalse(self._report_lines(vendor_bill))

    def test_released_or_forfeited_hold_has_no_credit_note_line(self):
        for hold_state in ('released', 'forfeited'):
            with self.subTest(hold_state=hold_state):
                hold = self._add_deposit_hold(hold_state)
                self.rental_line._create_deposit_credit_note(1, 1)
                self.assertFalse(self._order_credit_notes())
                hold.unlink()

    def test_reversed_invoice_matches_reversed_filter(self):
        credit_note = self.rental_invoice._reverse_moves(cancel=True)

        self.assertEqual(self.rental_invoice.payment_state, 'reversed')
        self.assertEqual(
            self._report_lines(self.rental_invoice).invoice_payment_state,
            'reversed',
        )
        lines = self._report_lines(self.rental_invoice | credit_note)
        self.assertEqual(sum(lines.mapped('signed_subtotal')), 0.0)

    def test_credit_notes_leave_stored_amounts_unchanged(self):
        fields_to_check = ['debit', 'credit', 'balance', 'price_unit', 'price_subtotal']
        before = self.rental_invoice.line_ids.read(fields_to_check)

        credit_note = self._manual_credit_note(self.rental_invoice)
        credit_note.action_post()
        self.env['account.move.line'].flush_model()

        self.assertEqual(self.rental_invoice.line_ids.read(fields_to_check), before)
        self.assertEqual(self._report_lines(credit_note).price_subtotal, 300.0)

    # ── Views ─────────────────────────────────────────────────────────────────

    def test_action_opens_on_posted_documents(self):
        self.assertEqual(literal_eval(self.action.context).get('search_default_posted'), 1)
        self.assertEqual(
            self.action.search_view_id,
            self.env.ref('ggg_rental.view_rental_invoice_line_by_item_search'),
        )

    def test_list_is_read_only(self):
        view = self.env.ref('ggg_rental.view_rental_invoice_line_list')
        arch = self.env['account.move.line'].get_view(view.id, 'list')['arch']
        for attribute in ('create="false"', 'edit="false"', 'delete="false"'):
            self.assertIn(attribute, arch)

    def test_new_filters_only_appear_on_by_item(self):
        AccountMoveLine = self.env['account.move.line']
        by_item = AccountMoveLine.get_view(self.action.search_view_id.id, 'search')['arch']
        core = AccountMoveLine.get_view(
            self.env.ref('account.view_account_move_line_filter').id, 'search',
        )['arch']

        for name in ('rental_reversed', 'rental_invoices', 'rental_credit_notes',
                     'group_by_sale_order'):
            self.assertIn(f'name="{name}"', by_item)
            self.assertNotIn(f'name="{name}"', core)
        self.assertIn('name="rental_paid"', core)
