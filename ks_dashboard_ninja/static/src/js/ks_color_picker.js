/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { _t } from "@web/core/l10n/translation";

//Component for color picker being used in dashboard item create view.
//TODO : This color picker functionality can be improved a lot.
export class KsColorPicker extends Component {
    static template = "ks_color_picker_opacity_view";
    static props = {
        ...standardFieldProps,
        supportedTypes: { validate: (types) => types.includes("char") },
    };

    setup() {
        super.setup();
    }

    get events() {
        return {
            'change.spectrum .ks_color_picker': this._ksOnColorChange.bind(this),
            'change .ks_color_opacity': this._ksOnOpacityChange.bind(this),
            'input .ks_color_opacity': this._ksOnOpacityInput.bind(this)
        };
    }

    get ks_color_value() {
        if (this.props.record.data[this.props.name]) {
            return this.props.record.data[this.props.name].split(',')[0];
        }
        return '#376CAE';
    }

    get ks_color_opacity() {
        if (this.props.record.data[this.props.name]) {
            return this.props.record.data[this.props.name].split(',')[1];
        }
        return '0.99';
    }

    onMounted() {
        this.initializeColorPicker();
    }

    initializeColorPicker() {
        const colorValue = this.ks_color_value;
        $(this.el).find('.ks_color_picker').spectrum({
            color: colorValue,
            showInput: true,
            className: "full-spectrum",
            showInitial: true,
            showPalette: true,
            showSelectionPalette: true,
            maxSelectionSize: 10,
            preferredFormat: "hex",
            localStorageKey: "spectrum.demo",
            move: (color) => {

            },
            show: () => {

            },
            beforeShow: () => {

            },
            hide: () => {

            }
        });

        if (this.props.readonly) {
            $(this.el).find('.ks_color_picker').addClass('ks_not_click');
            $(this.el).find('.ks_color_opacity').addClass('ks_not_click');
            $(this.el).find('.ks_color_picker').spectrum("disable");
        } else {
            $(this.el).find('.ks_color_picker').spectrum("enable");
        }
    }



    _ksOnColorChange(e, tinycolor) {
        const currentValue = this.props.record.data[this.props.name] || '#376CAE,0.99';
        const opacity = currentValue.split(',')[1];
        this.props.record.update({ [this.props.name]: tinycolor.toHexString() + "," + opacity });
    }

    _ksOnOpacityChange(event) {
        const currentValue = this.props.record.data[this.props.name] || '#376CAE,0.99';
        const color = currentValue.split(',')[0];
        this.props.record.update({ [this.props.name]: color + "," + event.currentTarget.value });
    }

    _ksOnOpacityInput(event) {
        let color;
        if (this.props.name == "ks_background_color") {
            color = $('.ks_db_item_preview_color_picker').css("background-color")
            $('.ks_db_item_preview_color_picker').css("background-color", this.get_color_opacity_value(color, event.currentTarget.value))

            color = $('.ks_db_item_preview_l2').css("background-color")
            $('.ks_db_item_preview_l2').css("background-color", this.get_color_opacity_value(color, event.currentTarget.value))

        } else if (this.props.name == "ks_default_icon_color") {
            color = $('.ks_dashboard_icon_color_picker > span').css('color')
            $('.ks_dashboard_icon_color_picker > span').css('color', this.get_color_opacity_value(color, event.currentTarget.value))
        } else if (this.props.name == "ks_font_color") {
            color = $('.ks_db_item_preview').css("color")
            color = $('.ks_db_item_preview').css("color", this.get_color_opacity_value(color, event.currentTarget.value))
        }
    }

    get_color_opacity_value(color, val) {
        if (color) {
            return color.replace(color.split(',')[3], val + ")");
        } else {
            return false;
        }
    }


}

registry.add('ks_color_dashboard_picker', KsColorPicker);