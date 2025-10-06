/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { loadJS, loadCSS } from "@web/core/assets";

const fieldRegistry = registry.category("fields");

export class KsColorPicker extends Component {
    static template = "ks_color_picker_opacity_view";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.colorPickerRef = useRef("colorPicker");
        this.opacityRef = useRef("opacitySlider");
        
        this.state = useState({
            colorValue: '#376CAE',
            colorOpacity: '0.99',
            isLoading: true,
        });

        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
        
        this._parseValue();
    }

    async onMounted() {
        await this._loadLibraries();
        this._initializeColorPicker();
        this.state.isLoading = false;
    }

    onWillUnmount() {
        if (this.colorPickerRef.el && this.colorPickerRef.el.spectrum) {
            this.colorPickerRef.el.spectrum("destroy");
        }
    }

    async _loadLibraries() {
        try {
            await Promise.all([
                loadJS('/ks_dashboard_ninja/static/lib/js/spectrum.js'),
                loadCSS('/ks_dashboard_ninja/static/lib/css/spectrum.css')
            ]);
        } catch (error) {
            console.error("Error loading color picker libraries:", error);
        }
    }

    _parseValue() {
        if (this.props.value) {
            const parts = this.props.value.split(',');
            this.state.colorValue = parts[0] || '#376CAE';
            this.state.colorOpacity = parts[1] || '0.99';
        }
    }

    _initializeColorPicker() {
        if (!this.colorPickerRef.el || !window.jQuery || !window.jQuery.fn.spectrum) {
            return;
        }

        const $ = window.jQuery;
        const $colorPicker = $(this.colorPickerRef.el);

        $colorPicker.spectrum({
            color: this.state.colorValue,
            showInput: true,
            hideAfterPaletteSelect: true,
            showPalette: true,
            showSelectionPalette: true,
            maxSelectionSize: 10,
            preferredFormat: "hex",
            localStorageKey: "ks_dashboard_ninja.color_picker",
            palette: [
                ["#000", "#444", "#666", "#999", "#ccc", "#eee", "#f3f3f3", "#fff"],
                ["#f00", "#f90", "#ff0", "#0f0", "#0ff", "#00f", "#90f", "#f0f"],
                ["#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e0e3", "#cfe2f3", "#d9d2e9", "#ead1dc"],
                ["#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#9fc5e8", "#b4a7d6", "#d5a6bd"],
                ["#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6fa8dc", "#8e7cc3", "#c27ba0"],
                ["#cc0000", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3d85c6", "#674ea7", "#a64d79"],
                ["#990000", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#0b5394", "#351c75", "#741b47"],
                ["#660000", "#783f04", "#7f6000", "#274e13", "#0c343d", "#073763", "#20124d", "#4c1130"]
            ],
            change: this._onColorChange.bind(this),
            move: this._onColorMove.bind(this),
        });
    }

    _onColorChange(color) {
        this.state.colorValue = color.toHexString();
        this._updateValue();
    }

    _onColorMove(color) {
        this.state.colorValue = color.toHexString();
    }

    _onOpacityChange(ev) {
        this.state.colorOpacity = ev.target.value;
        this._updateValue();
    }

    _onOpacityInput(ev) {
        this.state.colorOpacity = ev.target.value;
    }

    _updateValue() {
        const newValue = `${this.state.colorValue},${this.state.colorOpacity}`;
        this.props.update(newValue);
    }

    _validateOpacity(value) {
        const opacity = parseFloat(value);
        if (isNaN(opacity)) return '0.99';
        return Math.max(0, Math.min(1, opacity)).toString();
    }

    _validateColor(value) {
        const hexPattern = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
        return hexPattern.test(value) ? value : '#376CAE';
    }

    get displayValue() {
        return `${this.state.colorValue}, ${this.state.colorOpacity}`;
    }

    get rgbaColor() {
        const hex = this.state.colorValue.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        const a = parseFloat(this.state.colorOpacity);
        return `rgba(${r}, ${g}, ${b}, ${a})`;
    }

    resetToDefault() {
        this.state.colorValue = '#376CAE';
        this.state.colorOpacity = '0.99';
        this._updateValue();
        
        if (this.colorPickerRef.el && this.colorPickerRef.el.spectrum) {
            const $ = window.jQuery;
            $(this.colorPickerRef.el).spectrum("set", this.state.colorValue);
        }
    }
}

KsColorPicker.supportedTypes = ["char"];

fieldRegistry.add("ks_color_picker", KsColorPicker);