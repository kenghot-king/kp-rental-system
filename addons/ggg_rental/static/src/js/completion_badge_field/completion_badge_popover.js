import { Component } from "@odoo/owl";

export class CompletionBadgePopover extends Component {
    static template = "ggg_rental.CompletionBadgePopover";
    static props = {
        detail: { type: String, optional: true },
        isComplete: { type: Boolean },
        close: { type: Function, optional: true },
    };
}
