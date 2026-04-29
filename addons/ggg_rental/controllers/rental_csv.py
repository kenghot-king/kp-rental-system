import csv
import io

from odoo import http
from odoo.http import request, content_disposition


SERIAL_FIELDS = ['sap_article_code', 'serial_number']

PRODUCT_FIELDS = [
    'sap_article_code',
    'name',
    'type',
    'is_storable',
    'categ_id',
    'list_price',
    'sale_ok',
    'rent_ok',
    'extra_hourly',
    'extra_daily',
    'deposit_price',
    'uom_id',
    'tracking',
    'taxes_id',
    'default_code',
    'barcode',
    'description_sale',
]

PRODUCT_FIELD_MAP = {
    'type': {
        'consu': 'Goods',
        'service': 'Service',
        'combo': 'Combo',
    },
}

IMPORT_TYPE_MAP = {v: k for k, v in PRODUCT_FIELD_MAP['type'].items()}


class RentalCSVController(http.Controller):

    def _company_env(self):
        """Return an env with allowed_company_ids resolved from the cids cookie.

        Plain HTTP controllers don't inherit allowed_company_ids from the JS
        client the way JSON-RPC does, so company-dependent fields would resolve
        to user.company_id instead of the UI's active company. Reading the
        cids cookie keeps reads/writes aligned with what the user sees.
        """
        cids_cookie = request.httprequest.cookies.get('cids') or ''
        company_ids = []
        for token in cids_cookie.replace(',', '-').split('-'):
            if token.isdigit():
                company_ids.append(int(token))
        if not company_ids:
            company_ids = request.env.user.company_id.ids
        return request.env(context=dict(
            request.env.context, allowed_company_ids=company_ids,
        ))

    def _get_recurrences(self):
        """Get all recurrence periods with en_US display names."""
        recurrences = request.env['sale.temporal.recurrence'].with_context(
            lang='en_US'
        ).search([], order='unit, duration')
        return recurrences

    def _get_recurrence_headers(self, recurrences):
        """Get display names for recurrence periods."""
        return [r.with_context(lang='en_US').duration_display for r in recurrences]

    @http.route('/ggg_rental/download_product_template', type='http', auth='user')
    def download_product_template(self):
        recurrences = self._get_recurrences()
        recurrence_headers = self._get_recurrence_headers(recurrences)

        headers = PRODUCT_FIELDS + recurrence_headers

        # Build recurrence map: record -> display header
        recurrence_map = {
            r: r.with_context(lang='en_US').duration_display for r in recurrences
        }

        # Fetch up to 10 existing rental products as sample rows.
        # Use the request's native env so company-dependent fields read
        # from whatever company the session resolves to.
        products = request.env['product.template'].search(
            [('rent_ok', '=', True)], limit=10, order='id asc'
        )

        rows = []
        for product in products:
            type_label = PRODUCT_FIELD_MAP['type'].get(product.type, product.type)
            taxes = product.taxes_id.filtered(lambda t: t.type_tax_use == 'sale')
            row = {
                'sap_article_code': product.sap_article_code or '',
                'name': product.name or '',
                'type': type_label,
                'is_storable': str(product.is_storable),
                'categ_id': product.categ_id.complete_name if product.categ_id else '',
                'list_price': str(product.list_price),
                'sale_ok': str(product.sale_ok),
                'rent_ok': str(product.rent_ok),
                'extra_hourly': str(product.extra_hourly),
                'extra_daily': str(product.extra_daily),
                'deposit_price': str(product.deposit_price),
                'uom_id': product.uom_id.name if product.uom_id else '',
                'tracking': product.tracking or 'none',
                'taxes_id': ';'.join(taxes.mapped('name')),
                'default_code': product.default_code or '',
                'barcode': product.barcode or '',
                'description_sale': product.description_sale or '',
            }
            # Pricing per recurrence period
            pricing_map = {
                p.recurrence_id: p.price
                for p in product.product_pricing_ids
                if not p.pricelist_id
            }
            for recurrence, header in recurrence_map.items():
                price = pricing_map.get(recurrence)
                row[header] = str(price) if price is not None else ''
            rows.append(row)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

        content = output.getvalue().encode('utf-8-sig')
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', content_disposition('rental_product_template.csv')),
            ],
        )

    @http.route('/ggg_rental/download_pricing_template', type='http', auth='user')
    def download_pricing_template(self):
        recurrences = self._get_recurrences()
        recurrence_headers = self._get_recurrence_headers(recurrences)

        headers = ['sap_article_code'] + recurrence_headers

        example = {'sap_article_code': 'SAP-001'}
        for i, header in enumerate(recurrence_headers):
            example[header] = str((i + 1) * 500) if i < 3 else ''

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerow(example)

        content = output.getvalue().encode('utf-8-sig')
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', content_disposition('rental_pricing_template.csv')),
            ],
        )

    @http.route('/ggg_rental/download_serial_template', type='http', auth='user')
    def download_serial_template(self):
        example = {'sap_article_code': 'FORK-001', 'serial_number': 'SN-2026-001'}

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=SERIAL_FIELDS)
        writer.writeheader()
        writer.writerow(example)

        content = output.getvalue().encode('utf-8-sig')
        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'text/csv; charset=utf-8'),
                ('Content-Disposition', content_disposition('rental_serial_template.csv')),
            ],
        )

    @http.route('/ggg_rental/import_serials', type='http', auth='user',
                methods=['POST'], csrf=False)
    def import_serials(self, file=None, **kwargs):
        if not file:
            return request.make_json_response({'error': 'No file uploaded'}, status=400)

        try:
            content = file.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            content = file.read().decode('latin-1')

        env = self._company_env()
        company = env.user.company_id

        # Resolve destination: active company's default warehouse lot_stock_id
        warehouse = env['stock.warehouse'].sudo().search(
            [('company_id', '=', company.id)], limit=1
        )
        if not warehouse or not warehouse.lot_stock_id:
            return request.make_json_response(
                {'error': 'No default warehouse with stock location found. '
                          'Configure a warehouse with lot_stock_id before importing serials.'},
                status=400,
            )
        location = warehouse.lot_stock_id

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            return request.make_json_response(
                {'error': 'Empty or invalid CSV file'}, status=400
            )

        missing = [f for f in SERIAL_FIELDS if f not in reader.fieldnames]
        if missing:
            return request.make_json_response(
                {'error': f"Missing required columns: {', '.join(missing)}"},
                status=400,
            )

        Lot = env['stock.lot'].sudo()
        Quant = env['stock.quant'].sudo()
        ProductTemplate = env['product.template'].sudo()

        created = 0
        skipped = 0
        warnings = []
        row_errors = []
        seen_in_csv = set()  # (product_id, serial_number) already processed this run

        for row_num, row in enumerate(reader, start=2):
            sap_code = (row.get('sap_article_code') or '').strip()
            serial = (row.get('serial_number') or '').strip()

            if not sap_code or not serial:
                row_errors.append(f"Row {row_num}: missing sap_article_code or serial_number — skipped")
                continue

            # Product validation state machine
            tmpl = ProductTemplate.search([('sap_article_code', '=', sap_code)], limit=1)
            if not tmpl:
                row_errors.append(f"Row {row_num}: SAP code '{sap_code}' not found")
                continue
            if not tmpl.rent_ok:
                row_errors.append(f"Row {row_num}: product '{tmpl.name}' is not a rental product")
                continue
            if not tmpl.is_storable:
                row_errors.append(f"Row {row_num}: product '{tmpl.name}' is not storable")
                continue
            if tmpl.tracking != 'serial':
                row_errors.append(f"Row {row_num}: product '{tmpl.name}' is not serial-tracked")
                continue
            variants = tmpl.product_variant_ids
            if len(variants) != 1:
                row_errors.append(
                    f"Row {row_num}: product '{tmpl.name}' has {len(variants)} variants — "
                    f"cannot determine which variant; use a single-variant product"
                )
                continue
            product = variants[0]

            # Duplicate detection: in-CSV and pre-existing
            csv_key = (product.id, serial)
            if csv_key in seen_in_csv:
                warnings.append(
                    f"Row {row_num}: serial '{serial}' duplicated in CSV for {sap_code} — skipped"
                )
                skipped += 1
                continue
            seen_in_csv.add(csv_key)

            existing_lot = Lot.search(
                [('product_id', '=', product.id), ('name', '=', serial)], limit=1
            )
            if existing_lot:
                warnings.append(
                    f"Row {row_num}: serial '{serial}' already exists for {sap_code} — skipped"
                )
                skipped += 1
                continue

            # Create lot + quant with inventory adjustment
            try:
                with env.cr.savepoint():
                    lot = Lot.create({
                        'name': serial,
                        'product_id': product.id,
                        'company_id': company.id,
                    })
                    quant = Quant.with_context(inventory_mode=True).create({
                        'product_id': product.id,
                        'location_id': location.id,
                        'lot_id': lot.id,
                        'inventory_quantity': 1.0,
                    })
                    quant._apply_inventory()
                    created += 1
            except Exception as e:
                row_errors.append(f"Row {row_num} ({sap_code} / {serial}): {str(e)}")

        return request.make_json_response({
            'created': created,
            'skipped': skipped,
            'errors': len(row_errors),
            'warnings': warnings,
            'row_errors': row_errors,
        })

    @http.route('/ggg_rental/import_products', type='http', auth='user',
                methods=['POST'], csrf=False)
    def import_products(self, file=None, **kwargs):
        if not file:
            return request.make_json_response(
                {'error': 'No file uploaded'}, status=400
            )

        try:
            content = file.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            content = file.read().decode('latin-1')

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            return request.make_json_response(
                {'error': 'Empty or invalid CSV file'}, status=400
            )

        # Build recurrence map: display_name -> record
        recurrences = self._get_recurrences()
        recurrence_map = {}
        for r in recurrences:
            display = r.with_context(lang='en_US').duration_display
            recurrence_map[display] = r

        # Classify columns
        pricing_columns = {}
        product_columns = []
        warnings = []
        for col in reader.fieldnames:
            if col in recurrence_map:
                pricing_columns[col] = recurrence_map[col]
            elif col in PRODUCT_FIELDS:
                product_columns.append(col)
            else:
                warnings.append(f"Unknown column '{col}' — skipped")

        is_pricing_only = (
            product_columns == ['sap_article_code'] and pricing_columns
        )

        created = 0
        updated = 0
        errors = []

        env = self._company_env()
        ProductTemplate = env['product.template'].sudo()

        for row_num, row in enumerate(reader, start=2):
            sap_code = (row.get('sap_article_code') or '').strip()
            if not sap_code:
                errors.append(f"Row {row_num}: missing sap_article_code — skipped")
                continue

            existing = ProductTemplate.search(
                [('sap_article_code', '=', sap_code)], limit=1
            )

            if not existing and is_pricing_only:
                errors.append(
                    f"Row {row_num}: product '{sap_code}' not found "
                    f"— cannot create from pricing-only template"
                )
                continue

            # Per-row savepoint so a single bad row only rolls back itself,
            # not earlier successful rows in the same import.
            try:
                with request.env.cr.savepoint():
                    if existing:
                        if not is_pricing_only:
                            vals = self._prepare_product_vals(row, product_columns, warnings)
                            if vals:
                                existing.write(vals)
                        self._merge_pricing(existing, row, pricing_columns)
                        updated += 1
                    else:
                        vals = self._prepare_product_vals(row, product_columns, warnings)
                        vals['sap_article_code'] = sap_code
                        vals['rent_ok'] = True
                        product = ProductTemplate.create(vals)
                        self._merge_pricing(product, row, pricing_columns)
                        created += 1
            except Exception as e:
                errors.append(f"Row {row_num} ({sap_code}): {str(e)}")

        return request.make_json_response({
            'created': created,
            'updated': updated,
            'errors': len(errors),
            'error_details': errors,
            'warnings': warnings,
        })

    def _prepare_product_vals(self, row, columns, warnings=None):
        """Convert CSV row values to Odoo field values."""
        if warnings is None:
            warnings = []
        vals = {}
        for col in columns:
            if col == 'sap_article_code':
                continue
            raw = (row.get(col) or '').strip()
            if not raw:
                continue

            if col == 'type':
                vals[col] = IMPORT_TYPE_MAP.get(raw, raw)
            elif col == 'categ_id':
                categ = request.env['product.category'].search(
                    [('complete_name', '=', raw)], limit=1
                )
                if categ:
                    vals[col] = categ.id
            elif col == 'uom_id':
                uom = request.env['uom.uom'].search(
                    [('name', '=', raw)], limit=1
                )
                if uom:
                    vals[col] = uom.id
            elif col in ('list_price', 'extra_hourly', 'extra_daily', 'deposit_price'):
                try:
                    vals[col] = float(raw)
                except ValueError:
                    pass
            elif col in ('rent_ok', 'sale_ok', 'is_storable'):
                vals[col] = raw.lower() in ('true', '1', 'yes')
            elif col == 'tracking':
                if raw in ('none', 'lot', 'serial'):
                    vals[col] = raw
            elif col == 'taxes_id':
                tax_names = [n.strip() for n in raw.split(';') if n.strip()]
                tax_ids = []
                for tax_name in tax_names:
                    tax = request.env['account.tax'].search([
                        ('name', '=', tax_name),
                        ('type_tax_use', '=', 'sale'),
                        ('active', '=', True),
                    ], limit=1)
                    if tax:
                        tax_ids.append(tax.id)
                    else:
                        warnings.append(f"Tax '{tax_name}' not found — skipped")
                if tax_ids:
                    vals[col] = [(6, 0, tax_ids)]
            else:
                vals[col] = raw

        return vals

    def _merge_pricing(self, product, row, pricing_columns):
        """Apply merge semantics for pricing columns.

        - Column present with value: create or update pricing
        - Column present with empty value: delete pricing
        - Column absent: keep existing pricing
        """
        ProductPricing = request.env['product.pricing'].sudo()

        for col_name, recurrence in pricing_columns.items():
            raw = row.get(col_name, '').strip() if row.get(col_name) is not None else ''

            existing_pricing = ProductPricing.search([
                ('product_template_id', '=', product.id),
                ('recurrence_id', '=', recurrence.id),
                ('pricelist_id', '=', False),
            ], limit=1)

            if raw == '':
                # Empty cell: delete existing pricing for this period
                if existing_pricing:
                    existing_pricing.unlink()
            else:
                try:
                    price = float(raw)
                except ValueError:
                    continue

                if existing_pricing:
                    existing_pricing.write({'price': price})
                else:
                    ProductPricing.create({
                        'product_template_id': product.id,
                        'recurrence_id': recurrence.id,
                        'price': price,
                    })
