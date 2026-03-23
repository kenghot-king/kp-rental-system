/** @odoo-module **/

import { ViewCompiler } from "@web/views/view_compiler";

/**
 * Compiler for Gantt view templates.
 *
 * Extends ViewCompiler to allow additional OWL directives
 * that are used in gantt popover templates.
 */
export class GanttCompiler extends ViewCompiler {}

GanttCompiler.OWL_DIRECTIVE_WHITELIST = [
    ...ViewCompiler.OWL_DIRECTIVE_WHITELIST,
    "t-name",
    "t-esc",
    "t-out",
    "t-set",
    "t-value",
    "t-if",
    "t-else",
    "t-elif",
    "t-foreach",
    "t-as",
    "t-key",
    "t-att.*",
    "t-call",
];
