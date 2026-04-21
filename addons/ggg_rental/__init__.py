from . import controllers
from . import models
from . import report
from . import wizard
from odoo.tools.sql import column_exists


def _post_init_rental(env):
    """Create rental locations for existing companies on module install."""
    env['res.company'].create_missing_rental_location()
    env['res.company'].create_missing_rental_support_locations()
    # Rebuild the unreconciled-tuples view now that all columns are guaranteed to exist.
    env['rental.daily.reconciliation.needed'].init()


def _pre_init_rental(env):
    """Allow installing ggg_rental in databases with large sale.order / sale.order.line tables.

    The different rental fields are all NULL (falsy) for existing sale orders,
    the computation is way more efficient in SQL than in Python.
    """
    if not column_exists(env.cr, 'sale_order', 'rental_status'):
        env.cr.execute("""
            ALTER TABLE "sale_order"
            ADD COLUMN "rental_start_date" timestamp,
            ADD COLUMN "rental_return_date" timestamp,
            ADD COLUMN "rental_status" VARCHAR,
            ADD COLUMN "next_action_date" timestamp
        """)
        env.cr.execute("""
            ALTER TABLE "sale_order_line"
            ADD COLUMN "reservation_begin" timestamp
        """)
    if not column_exists(env.cr, 'res_company', 'rental_loc_id'):
        env.cr.execute("""
            ALTER TABLE "res_company"
            ADD COLUMN "rental_loc_id" integer
        """)
    if not column_exists(env.cr, 'res_company', 'damage_loc_id'):
        env.cr.execute("""
            ALTER TABLE "res_company"
            ADD COLUMN "damage_loc_id" integer
        """)
    if not column_exists(env.cr, 'res_company', 'inspection_loc_id'):
        env.cr.execute("""
            ALTER TABLE "res_company"
            ADD COLUMN "inspection_loc_id" integer
        """)
