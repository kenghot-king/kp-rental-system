from datetime import datetime

from odoo.tests.common import TransactionCase


class TestRentalCalendarBilling(TransactionCase):
    """Tests for the calendar-day-difference billing model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricing_model = cls.env['product.pricing']

    def _duration_vals(self, start_str, end_str):
        fmt = '%Y-%m-%d %H:%M'
        return self.pricing_model._compute_duration_vals(
            datetime.strptime(start_str, fmt),
            datetime.strptime(end_str, fmt),
        )

    # ── _compute_duration_vals ────────────────────────────────────────────────

    def test_multi_day_endofday_return_is_4_not_5(self):
        """Apr 29 09:00 → May 3 23:59 is 4 calendar days, not 5."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-05-03 23:59')
        self.assertEqual(vals['day'], 4)

    def test_multi_day_same_time_return(self):
        """Apr 29 09:00 → May 3 09:00 is 4 calendar days."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-05-03 09:00')
        self.assertEqual(vals['day'], 4)

    def test_cross_midnight_is_1_day(self):
        """Apr 29 09:00 → Apr 30 01:00 (crosses midnight) is 1 calendar day."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-04-30 01:00')
        self.assertEqual(vals['day'], 1)
        self.assertEqual(vals['remaining_hours'] if 'remaining_hours' in vals else 0, 0)

    def test_same_date_is_0_days(self):
        """Apr 29 09:00 → Apr 29 17:00 (sub-day) is 0 calendar days."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-04-29 17:00')
        self.assertEqual(vals['day'], 0)

    def test_week_derived_from_days(self):
        """14-day rental → 2 weeks."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-05-13 23:59')
        self.assertEqual(vals['day'], 14)
        self.assertEqual(vals['week'], 2)

    def test_week_zero_when_subday(self):
        """Sub-day rental → 0 weeks."""
        vals = self._duration_vals('2026-04-29 09:00', '2026-04-29 17:00')
        self.assertEqual(vals['week'], 0)

    # ── _compute_greedy_price (sub-day fallback) ──────────────────────────────

    def _make_product_with_tiers(self, tiers):
        """Create a storable rental product with the given pricing tiers.

        tiers: list of (recurrence_duration, recurrence_unit, price)
        """
        product = self.env['product.template'].create({
            'name': 'Test Rental Product',
            'type': 'consu',
            'rent_ok': True,
        })
        for duration, unit, price in tiers:
            recurrence = self.env['sale.temporal.recurrence'].search([
                ('duration', '=', duration), ('unit', '=', unit)
            ], limit=1)
            if not recurrence:
                recurrence = self.env['sale.temporal.recurrence'].create({
                    'duration': duration, 'unit': unit,
                })
            self.env['product.pricing'].create({
                'product_template_id': product.id,
                'recurrence_id': recurrence.id,
                'price': price,
            })
        return product

    def test_subday_daily_only_product_bills_one_day(self):
        """Same-day rental with daily-only product → bills 1 day (min fallback)."""
        product = self._make_product_with_tiers([(1, 'day', 300.0)])
        start = datetime(2026, 4, 29, 9, 0)
        end = datetime(2026, 4, 29, 17, 0)
        price = product._compute_greedy_price(start, end)
        self.assertEqual(price, 300.0)

    def test_subday_hourly_product_bills_hours(self):
        """Same-day rental with hourly tier → bills by hour (ceil)."""
        product = self._make_product_with_tiers([(1, 'hour', 50.0)])
        start = datetime(2026, 4, 29, 9, 0)
        end = datetime(2026, 4, 29, 12, 30)  # 3.5 hours → ceil = 4
        price = product._compute_greedy_price(start, end)
        self.assertEqual(price, 200.0)  # 4 × 50

    def test_multiday_not_affected_by_fallback(self):
        """Multi-day rental should not trigger the sub-day fallback."""
        product = self._make_product_with_tiers([(1, 'day', 300.0)])
        start = datetime(2026, 4, 29, 9, 0)
        end = datetime(2026, 5, 3, 23, 59)  # 4 calendar days
        price = product._compute_greedy_price(start, end)
        self.assertEqual(price, 1200.0)  # 4 × 300
