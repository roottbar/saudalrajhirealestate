/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { AbstractField } from "@web/views/fields/abstract_field";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

    class KsWidgetToggle extends AbstractField {
        static supportedTypes = ['char'];
        static template = 'ks_widget_toggle';

        get events() {
            return {
                ...super.events,
                'change .ks_toggle_icon_input': this.ks_toggle_icon_input_click.bind(this),
            };
        }

        _render() {
            $(this.el).empty();

            const $view = $(renderToElement('ks_widget_toggle'));
            if (this.value) {
                $view.find("input[value='" + this.value + "']").prop("checked", true);
            }
            $(this.el).append($view);

            if (this.mode === 'readonly') {
                $(this.el).find('.ks_select_dashboard_item_toggle').addClass('ks_not_click');
            }
        }

        ks_toggle_icon_input_click(e) {
            this._setValue(e.currentTarget.value);
        }
    }

    class KsWidgetToggleKPI extends AbstractField {
        static supportedTypes = ['char'];
        static template = 'ks_widget_toggle_kpi';

        get events() {
            return {
                ...super.events,
                'change .ks_toggle_icon_input': this.ks_toggle_icon_input_click.bind(this),
            };
        }

        _render() {
            $(this.el).empty();
            const $view = $(renderToElement('ks_widget_toggle_kpi'));

            if (this.value) {
                $view.find("input[value='" + this.value + "']").prop("checked", true);
            }
            $(this.el).append($view);

            if (this.mode === 'readonly') {
                $(this.el).find('.ks_select_dashboard_item_toggle').addClass('ks_not_click');
            }
        }

        ks_toggle_icon_input_click(e) {
            this._setValue(e.currentTarget.value);
        }
    }

    class KsWidgetToggleKpiTarget extends AbstractField {
        static supportedTypes = ['char'];
        static template = 'ks_widget_toggle_kpi_target_view';

        get events() {
            return {
                ...super.events,
                'change .ks_toggle_icon_input': this.ks_toggle_icon_input_click.bind(this),
            };
        }

        _render() {
            $(this.el).empty();

            const $view = $(renderToElement('ks_widget_toggle_kpi_target_view'));
            if (this.value) {
                $view.find("input[value='" + this.value + "']").prop("checked", true);
            }
            $(this.el).append($view);

            if (this.mode === 'readonly') {
                $(this.el).find('.ks_select_dashboard_item_toggle').addClass('ks_not_click');
            }
        }

        ks_toggle_icon_input_click(e) {
            this._setValue(e.currentTarget.value);
        }
    }

    registry.category("fields").add('ks_widget_toggle', KsWidgetToggle);
    registry.category("fields").add('ks_widget_toggle_kpi', KsWidgetToggleKPI);
    registry.category("fields").add('ks_widget_toggle_kpi_target', KsWidgetToggleKpiTarget);

    export {
        KsWidgetToggle,
        KsWidgetToggleKPI,
        KsWidgetToggleKpiTarget
    };