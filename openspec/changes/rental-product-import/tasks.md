## 1. SAP Article Code Field

- [x] 1.1 Add `sap_article_code` field to `product.template` in `models/product_template.py` (Char, required, indexed, copy=False)
- [x] 1.2 Add SQL unique constraint for `sap_article_code`
- [x] 1.3 Add `sap_article_code` to product form view (rental form)
- [x] 1.4 Add `sap_article_code` to product tree view (rental list)
- [x] 1.5 Add `sap_article_code` to `_rec_names_search` so it can be searched by this field

## 2. CSV Template Download

- [x] 2.1 Create `controllers/__init__.py` and `controllers/main.py` with rental CSV controller
- [x] 2.2 Implement `GET /ggg_rental/download_product_template` endpoint — dynamically generates CSV with product fields + recurrence period columns + example row
- [x] 2.3 Implement `GET /ggg_rental/download_pricing_template` endpoint — generates CSV with `sap_article_code` + recurrence period columns + example row
- [x] 2.4 Register controllers in `__init__.py` and `__manifest__.py`
- [x] 2.5 Add "Download Product Template" and "Download Pricing Template" buttons to rental product tree view header

## 3. CSV Import Controller

- [x] 3.1 Implement `POST /ggg_rental/import_products` endpoint — accepts CSV file upload
- [x] 3.2 Implement CSV parsing: separate fixed product columns from dynamic pricing columns by matching against `sale.temporal.recurrence` records (en_US)
- [x] 3.3 Implement upsert logic: search by `sap_article_code`, create if not found, update all fields if found
- [x] 3.4 Implement pricing merge logic: value = create/update, empty = delete, column missing = keep
- [x] 3.5 Implement result reporting: return JSON with created/updated/error counts and warnings array
- [x] 3.6 Handle edge cases: missing `sap_article_code`, unrecognized columns (warn + skip), invalid values

## 4. Import UI

- [x] 4.1 Add "Import Products" button to rental product tree view header
- [x] 4.2 Create JS client action or dialog for file upload that calls the import endpoint
- [x] 4.3 Display import results (created, updated, errors, warnings) in a dialog after upload

## 5. Integration & Testing

- [ ] 5.1 Test full flow: download template → fill data → import → verify products and pricing created
- [ ] 5.2 Test update flow: modify CSV → re-import → verify products updated and pricing merged correctly
- [ ] 5.3 Test edge cases: duplicate sap_article_code in CSV, empty pricing cells, unknown columns, missing required fields
- [x] 5.4 Update `__manifest__.py` with new data files and dependencies if needed
