/** @odoo-module **/

import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { STATIC_ACTIONS_GROUP_NUMBER } from "@web/search/action_menus/action_menus";
import { Component } from "@odoo/owl";
import { RentalImportDialog } from "./rental_import_dialog";
import { RentalSerialImportDialog } from "./rental_serial_import_dialog";

const cogMenuRegistry = registry.category("cogMenu");

class DownloadProductTemplate extends Component {
    static template = "ggg_rental.DownloadProductTemplate";
    static components = { DropdownItem };
    static props = {};

    onClick() {
        this.env.services.action.doAction({
            type: "ir.actions.act_url",
            url: "/ggg_rental/download_product_template",
            target: "self",
        });
    }
}

class DownloadPricingTemplate extends Component {
    static template = "ggg_rental.DownloadPricingTemplate";
    static components = { DropdownItem };
    static props = {};

    onClick() {
        this.env.services.action.doAction({
            type: "ir.actions.act_url",
            url: "/ggg_rental/download_pricing_template",
            target: "self",
        });
    }
}

class ImportProducts extends Component {
    static template = "ggg_rental.ImportProducts";
    static components = { DropdownItem };
    static props = {};

    onClick() {
        this.env.services.dialog.add(RentalImportDialog, {});
    }
}

function isRentalProductView(env) {
    return (
        ["kanban", "list"].includes(env.config.viewType) &&
        env.config.actionId &&
        !env.model.root.selection.length &&
        env.searchModel?.resModel === "product.template" &&
        env.searchModel?.context?.default_rent_ok
    );
}

cogMenuRegistry.add("rental-download-product-template", {
    Component: DownloadProductTemplate,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => isRentalProductView(env),
}, { sequence: 20 });

cogMenuRegistry.add("rental-download-pricing-template", {
    Component: DownloadPricingTemplate,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => isRentalProductView(env),
}, { sequence: 21 });

cogMenuRegistry.add("rental-import-products", {
    Component: ImportProducts,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => isRentalProductView(env),
}, { sequence: 22 });

class DownloadSerialTemplate extends Component {
    static template = "ggg_rental.DownloadSerialTemplate";
    static components = { DropdownItem };
    static props = {};

    onClick() {
        this.env.services.action.doAction({
            type: "ir.actions.act_url",
            url: "/ggg_rental/download_serial_template",
            target: "self",
        });
    }
}

class ImportSerials extends Component {
    static template = "ggg_rental.ImportSerials";
    static components = { DropdownItem };
    static props = {};

    onClick() {
        this.env.services.dialog.add(RentalSerialImportDialog, {});
    }
}

cogMenuRegistry.add("rental-download-serial-template", {
    Component: DownloadSerialTemplate,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => isRentalProductView(env),
}, { sequence: 23 });

cogMenuRegistry.add("rental-import-serials", {
    Component: ImportSerials,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: (env) => isRentalProductView(env),
}, { sequence: 24 });
