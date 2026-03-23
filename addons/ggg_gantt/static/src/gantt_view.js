/** @odoo-module **/

import { registry } from "@web/core/registry";
import { scrollSymbol } from "@web/search/action_hook";
import { GanttArchParser } from "./gantt_arch_parser";
import { GanttController } from "./gantt_controller";
import { GanttModel } from "./gantt_model";
import { GanttRenderer } from "./gantt_renderer";
import { omit } from "@web/core/utils/objects";

const viewRegistry = registry.category("views");

export const ganttView = {
    type: "gantt",
    Controller: GanttController,
    Renderer: GanttRenderer,
    Model: GanttModel,
    ArchParser: GanttArchParser,
    searchMenuTypes: ["filter", "groupBy", "favorite"],
    buttonTemplate: "ggg_gantt.GanttView.Buttons",

    props(genericProps, view, config) {
        const { arch, resModel } = genericProps;

        let modelParams;
        let displayParams;
        let multiCreateValues;
        let scrollPosition;

        if (genericProps.state) {
            const state = genericProps.state;
            modelParams = {
                metaData: state.metaData,
                displayParams: state.displayParams,
            };
            displayParams = state.displayParams;
            multiCreateValues = state.multiCreateValues || undefined;
            scrollPosition = state.scrollPosition || undefined;
        } else {
            const parser = new this.ArchParser();
            const archInfo = parser.parse(arch);

            // Resolve formViewId from available views if not specified in arch
            let formViewId = archInfo.formViewId;
            if (!formViewId) {
                const formView = (genericProps.views || []).find(
                    ([, type]) => type === "form"
                );
                formViewId = formView ? formView[0] : false;
            }

            // Resolve kanbanViewId from available views if not specified in arch
            let kanbanViewId = archInfo.kanbanViewId;
            if (kanbanViewId === null) {
                const kanbanView = (genericProps.views || []).find(
                    ([, type]) => type === "kanban"
                );
                kanbanViewId = kanbanView ? kanbanView[0] : null;
            }

            const metaData = {
                ...omit(archInfo, "formViewId", "kanbanViewId"),
                formViewId,
                kanbanViewId,
                resModel,
                fields: genericProps.fields,
            };

            displayParams = {};

            modelParams = {
                metaData,
                displayParams,
            };
        }

        // Capture scroll position from action state if available
        if (genericProps[scrollSymbol]) {
            scrollPosition = genericProps[scrollSymbol];
        }

        return {
            ...genericProps,
            Model: this.Model,
            Renderer: this.Renderer,
            buttonTemplate: this.buttonTemplate,
            modelParams,
            multiCreateValues,
            scrollPosition,
        };
    },
};

viewRegistry.add("gantt", ganttView);
