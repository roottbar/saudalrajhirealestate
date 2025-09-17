/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { AbstractField } from "@web/views/fields/abstract_field";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

    //Component for dashboard item theme using while creating dashboard item.
    class KsDashboardTheme extends AbstractField {
        static supportedTypes = ['char'];
        static template = 'ks_dashboard_theme_view';

        get events() {
            return {
                ...super.events,
                'click .ks_dashboard_theme_input_container': this.ks_dashboard_theme_input_container_click.bind(this),
            };
        }

        _render() {
            $(this.el).empty();
            const $view = $(renderToElement('ks_dashboard_theme_view'));
            if (this.value) {
                $view.find("input[value='" + this.value + "']").prop("checked", true);
            }
            $(this.el).append($view);

            if (this.mode === 'readonly') {
                $(this.el).find('.ks_dashboard_theme_view_render').addClass('ks_not_click');
            }
        }

        ks_dashboard_theme_input_container_click(e) {
            const $box = $(e.currentTarget).find(':input');
            if ($box.is(":checked")) {
                $(this.el).find('.ks_dashboard_theme_input').prop('checked', false);
                $box.prop("checked", true);
            } else {
                $box.prop("checked", false);
            }
            this._setValue($box[0].value);
        }
    }

    registry.category("fields").add('ks_dashboard_item_theme', KsDashboardTheme);

    export { KsDashboardTheme };