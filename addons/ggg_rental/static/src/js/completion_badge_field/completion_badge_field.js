import { Component, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { usePopover } from "@web/core/popover/popover_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { CompletionBadgePopover } from "./completion_badge_popover";

export class CompletionBadgeField extends Component {
    static template = "ggg_rental.CompletionBadgeField";
    static props = { ...standardFieldProps };

    setup() {
        this.badgeRef = useRef("badge");
        this.popover = usePopover(CompletionBadgePopover, {
            position: "bottom",
        });
    }

    get value() {
        return this.props.record.data[this.props.name];
    }

    get isComplete() {
        return this.value === "complete";
    }

    get label() {
        const field = this.props.record.fields[this.props.name];
        const option = field.selection.find((o) => o[0] === this.value);
        return option ? option[1] : "";
    }

    get detail() {
        return this.props.record.data.rental_completion_detail || "";
    }

    get badgeClass() {
        if (this.isComplete) {
            return "text-bg-success";
        }
        if (this.value === "incomplete") {
            return "text-bg-danger";
        }
        return "text-bg-secondary";
    }

    toggle() {
        if (this.popover.isOpen) {
            this.popover.close();
        } else if (this.badgeRef.el) {
            this.popover.open(this.badgeRef.el, {
                detail: this.detail,
                isComplete: this.isComplete,
            });
        }
    }

    onClick(ev) {
        ev.stopPropagation();
        this.toggle();
    }

    onKeydown(ev) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            ev.stopPropagation();
            this.toggle();
        }
    }
}

export const completionBadgeField = {
    component: CompletionBadgeField,
    displayName: _t("Completion Badge"),
    supportedTypes: ["selection"],
    fieldDependencies: [
        { name: "rental_completion_detail", type: "char" },
    ],
};

registry.category("fields").add("completion_badge", completionBadgeField);
