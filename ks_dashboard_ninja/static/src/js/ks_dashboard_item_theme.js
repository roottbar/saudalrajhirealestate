/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const fieldRegistry = registry.category("fields");

export class KsDashboardTheme extends Component {
    static template = "ks_dashboard_theme_view";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            selectedTheme: this.props.value || '',
        });
    }

    onThemeContainerClick(ev) {
        const container = ev.currentTarget;
        const input = container.querySelector('input');
        
        if (!input) return;
        
        // If readonly mode, prevent interaction
        if (this.props.readonly) {
            return;
        }
        
        // Toggle selection
        if (input.checked) {
            // Uncheck all other theme inputs
            this.el.querySelectorAll('.ks_dashboard_theme_input').forEach(inp => {
                inp.checked = false;
            });
            input.checked = true;
        } else {
            input.checked = false;
        }
        
        // Update state and notify parent
        this.state.selectedTheme = input.checked ? input.value : '';
        this.props.update(this.state.selectedTheme);
    }

    get isReadonly() {
        return this.props.readonly;
    }

    get themeOptions() {
        return [
            { value: 'white', label: 'White', class: 'ks_theme_white' },
            { value: 'dark', label: 'Dark', class: 'ks_theme_dark' },
            { value: 'blue', label: 'Blue', class: 'ks_theme_blue' },
            { value: 'red', label: 'Red', class: 'ks_theme_red' },
            { value: 'green', label: 'Green', class: 'ks_theme_green' },
            { value: 'yellow', label: 'Yellow', class: 'ks_theme_yellow' },
            { value: 'purple', label: 'Purple', class: 'ks_theme_purple' },
            { value: 'orange', label: 'Orange', class: 'ks_theme_orange' },
        ];
    }

    isThemeSelected(themeValue) {
        return this.state.selectedTheme === themeValue;
    }

    resetTheme() {
        this.state.selectedTheme = '';
        this.props.update('');
        
        // Uncheck all inputs
        this.el.querySelectorAll('.ks_dashboard_theme_input').forEach(input => {
            input.checked = false;
        });
    }

    setTheme(themeValue) {
        this.state.selectedTheme = themeValue;
        this.props.update(themeValue);
        
        // Update input states
        this.el.querySelectorAll('.ks_dashboard_theme_input').forEach(input => {
            input.checked = input.value === themeValue;
        });
    }

    getThemePreviewClass(themeValue) {
        const themeMap = {
            'white': 'ks_theme_preview_white',
            'dark': 'ks_theme_preview_dark',
            'blue': 'ks_theme_preview_blue',
            'red': 'ks_theme_preview_red',
            'green': 'ks_theme_preview_green',
            'yellow': 'ks_theme_preview_yellow',
            'purple': 'ks_theme_preview_purple',
            'orange': 'ks_theme_preview_orange',
        };
        return themeMap[themeValue] || 'ks_theme_preview_default';
    }
}

KsDashboardTheme.supportedTypes = ["char"];

fieldRegistry.add("ks_dashboard_item_theme", KsDashboardTheme);