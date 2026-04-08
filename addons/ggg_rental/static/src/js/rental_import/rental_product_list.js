/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { RentalImportDialog } from "./rental_import_dialog";

export class RentalProductListController extends ListController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.actionService = useService("action");
    }

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems();
        items.download_product_template = {
            sequence: 100,
            icon: "fa fa-download",
            description: this.env._t("Download Product Template"),
            callback: () => this.actionService.doAction({
                type: "ir.actions.act_url",
                url: "/ggg_rental/download_product_template",
                target: "self",
            }),
        };
        items.download_pricing_template = {
            sequence: 101,
            icon: "fa fa-download",
            description: this.env._t("Download Pricing Template"),
            callback: () => this.actionService.doAction({
                type: "ir.actions.act_url",
                url: "/ggg_rental/download_pricing_template",
                target: "self",
            }),
        };
        items.import_products = {
            sequence: 102,
            icon: "fa fa-upload",
            description: this.env._t("Import Products"),
            callback: () => this.dialogService.add(RentalImportDialog, {}),
        };
        return items;
    }
}

export const rentalProductListView = {
    ...listView,
    Controller: RentalProductListController,
};

registry.category("views").add("rental_product_list", rentalProductListView);
