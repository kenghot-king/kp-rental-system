import csv
import io

from odoo import http
from odoo.http import request, content_disposition


PRODUCT_FIELDS = [
    'sap_article_code',
    'name',
    'type',
    'categ_id',
    'list_price',
    'rent_ok',
    'extra_hourly',
    'extra_daily',
    'uom_id',
    'tracking',
    'default_code',
    'barcode',
    'description_sale',
]

PRODUCT_FIELD_MAP = {
    'type': {
        'consu': 'Storable Product',
        'service': 'Service',
        'combo': 'Combo',
    },
}

IMPORT_TYPE_MAP = {v: k for k, v in PRODUCT_FIELD_MAP['type'].items()}


class RentalCSVController(http.Controller):

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

        # Build example row
        categories = request.env['product.category'].search([], limit=1)
        uoms = request.env['uom.uom'].search([('name', '=', 'Units')], limit=1)
        example = {
            'sap_article_code': 'SAP-001',
            'name': 'Example Rental Product',
            'type': 'Storable Product',
            'categ_id': categories[0].complete_name if categories else 'Goods',
            'list_price': '15000.00',
            'rent_ok': 'True',
            'extra_hourly': '50.00',
            'extra_daily': '200.00',
            'uom_id': uoms[0].name if uoms else 'Units',
            'tracking': 'serial',
            'default_code': 'EX-001',
            'barcode': '',
            'description_sale': 'Example product for rental',
        }
        # Add example pricing for first few recurrences
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

        ProductTemplate = request.env['product.template'].sudo()
        ProductPricing = request.env['product.pricing'].sudo()

        for row_num, row in enumerate(reader, start=2):
            sap_code = (row.get('sap_article_code') or '').strip()
            if not sap_code:
                errors.append(f"Row {row_num}: missing sap_article_code — skipped")
                continue

            # Find existing product
            existing = ProductTemplate.search(
                [('sap_article_code', '=', sap_code)], limit=1
            )

            try:
                if existing:
                    # Update product fields (unless pricing-only import)
                    if not is_pricing_only:
                        vals = self._prepare_product_vals(row, product_columns)
                        if vals:
                            existing.write(vals)

                    # Merge pricing
                    self._merge_pricing(existing, row, pricing_columns)
                    updated += 1
                else:
                    if is_pricing_only:
                        errors.append(
                            f"Row {row_num}: product '{sap_code}' not found "
                            f"— cannot create from pricing-only template"
                        )
                        continue

                    vals = self._prepare_product_vals(row, product_columns)
                    vals['sap_article_code'] = sap_code
                    vals['rent_ok'] = True
                    product = ProductTemplate.create(vals)

                    # Create pricing
                    self._merge_pricing(product, row, pricing_columns)
                    created += 1

            except Exception as e:
                errors.append(f"Row {row_num} ({sap_code}): {str(e)}")
                request.env.cr.rollback()
                continue

        return request.make_json_response({
            'created': created,
            'updated': updated,
            'errors': len(errors),
            'error_details': errors,
            'warnings': warnings,
        })

    def _prepare_product_vals(self, row, columns):
        """Convert CSV row values to Odoo field values."""
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
            elif col in ('list_price', 'extra_hourly', 'extra_daily'):
                try:
                    vals[col] = float(raw)
                except ValueError:
                    pass
            elif col == 'rent_ok':
                vals[col] = raw.lower() in ('true', '1', 'yes')
            elif col == 'tracking':
                if raw in ('none', 'lot', 'serial'):
                    vals[col] = raw
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
