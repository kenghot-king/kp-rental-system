## 1. Model fields

- [x] 1.1 Add `default_pickup_time = fields.Float(default=9.0)` to `res.company` in `addons/ggg_rental/models/res_company.py`
- [x] 1.2 Add `default_return_time = fields.Float(default=23.983333)` to `res.company` in the same file
- [x] 1.3 Add help text on both fields explaining the snap behavior

## 2. Settings exposure

- [x] 2.1 Add corresponding `related='company_id.default_pickup_time'` and `default_return_time` fields on `res.config.settings` in `addons/ggg_rental/models/res_config_settings.py`
- [x] 2.2 Add the two fields to the **Default Delay Costs** section in `addons/ggg_rental/views/res_config_settings_views.xml` using `widget="float_time"` and clear labels ("Default Pickup Time", "Default Return Time")

## 3. Snap behavior on rental order

- [x] 3.1 Add `@api.onchange('rental_start_date')` method on `sale.order` in `addons/ggg_rental/models/sale_order.py` that snaps the time component to `company.default_pickup_time` when current time component equals 00:00:00
- [x] 3.2 Add `@api.onchange('rental_return_date')` method on `sale.order` that snaps the time component to `company.default_return_time` under the same condition
- [x] 3.3 Ensure both onchange methods perform the snap in the user's timezone (`self.env.user.tz`) and convert back to UTC for storage

## 4. Migration safety

- [ ] 4.1 Verify on a test instance that updating the module on a database with existing companies populates the new fields with their defaults (no manual migration required)
- [ ] 4.2 Verify existing rental orders are unchanged by the upgrade

## 5. Manual verification

- [ ] 5.1 Open Rental → Configuration → Settings; confirm both fields appear in Default Delay Costs section with HH:MM widget
- [ ] 5.2 Change Default Pickup Time to 10:00, save, create a new rental order, pick a date for `rental_start_date`; confirm time defaults to 10:00
- [ ] 5.3 On the same order, manually edit pickup time to 14:30, change the date, confirm 14:30 is preserved (no overwrite)
- [ ] 5.4 Pick a return date, confirm time defaults to 23:59
- [ ] 5.5 With user timezone set to Asia/Bangkok, confirm the snapped datetime stored in DB matches Bangkok local time converted to UTC
