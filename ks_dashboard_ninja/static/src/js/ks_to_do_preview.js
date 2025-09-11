/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { _t } from "@web/core/l10n/translation";

export class KsToDOViewPreview extends Component {
    static template = "ks_to_do_container";
    static props = {
        ...standardFieldProps,
        supportedTypes: { validate: (types) => types.includes("char") },
    };

    setup() {
        super.setup();
        this.state = {};
    }

    get recordData() {
        return this.props.record.data;
    }

    get ks_to_do_view_name() {
        return this.recordData.name ? this.recordData.name : 'Name';
    }

    get to_do_view_data() {
        if (this.recordData.ks_to_do_data) {
            return JSON.parse(this.recordData.ks_to_do_data);
        }
        return {};
    }

    get ks_header_color() {
        return this._ks_get_rgba_format(this.recordData.ks_header_bg_color);
    }

    get ks_font_color() {
        return this._ks_get_rgba_format(this.recordData.ks_font_color);
    }

    get ks_rgba_button_color() {
        return this._ks_get_rgba_format(this.recordData.ks_button_color);
    }

    _ks_get_rgba_format(val) {
        if (!val) return 'rgba(0,0,0,1)';
        const rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
        const rgbaValues = rgba.map(v => parseInt(v, 16)).join(",");
        return "rgba(" + rgbaValues + "," + val.split(',')[1] + ")";
    }

    onMounted() {
        this.applyStyles();
    }

    onPatched() {
        this.applyStyles();
    }

    applyStyles() {
        const headerColor = this.ks_header_color;
        const fontColor = this.ks_font_color;
        
        $(this.el).find('.ks_card_header').addClass('ks_bg_to_color').css({"background-color": headerColor });
        $(this.el).find('.ks_card_header').addClass('ks_bg_to_color').css({"color": fontColor + ' !important' });
        $(this.el).find('.ks_li_tab').addClass('ks_bg_to_color').css({"color": fontColor + ' !important' });
        $(this.el).find('.ks_chart_heading').addClass('ks_bg_to_color').css({"color": fontColor + ' !important' });
    }


}

registry.category("fields").add('ks_dashboard_to_do_preview', KsToDOViewPreview);