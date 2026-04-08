/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { RentalImportDialog } from "./rental_import_dialog";

function importProductsAction(env, action) {
    env.services.dialog.add(RentalImportDialog, {});
}

registry.category("actions").add("ggg_rental.import_products", importProductsAction);
