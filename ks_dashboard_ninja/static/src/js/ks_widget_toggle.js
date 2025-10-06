/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const fieldRegistry = registry.category("fields");

// Base Widget Toggle Component
export class KsWidgetToggle extends Component {
    static template = "ks_widget_toggle";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            selectedValue: this.props.value || '',
        });
    }

    onToggleChange(ev) {
        if (this.props.readonly) {
            return;
        }
        
        const value = ev.target.value;
        this.state.selectedValue = value;
        this.props.update(value);
    }

    get isReadonly() {
        return this.props.readonly;
    }

    isSelected(value) {
        return this.state.selectedValue === value;
    }
}

// KPI Widget Toggle Component
export class KsWidgetToggleKPI extends Component {
    static template = "ks_widget_toggle_kpi";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            selectedValue: this.props.value || '',
        });
    }

    onToggleChange(ev) {
        if (this.props.readonly) {
            return;
        }
        
        const value = ev.target.value;
        this.state.selectedValue = value;
        this.props.update(value);
    }

    get isReadonly() {
        return this.props.readonly;
    }

    isSelected(value) {
        return this.state.selectedValue === value;
    }
}

// KPI Target Widget Toggle Component
export class KsWidgetToggleKpiTarget extends Component {
    static template = "ks_widget_toggle_kpi_target_view";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            selectedValue: this.props.value || '',
        });
    }

    onToggleChange(ev) {
        if (this.props.readonly) {
            return;
        }
        
        const value = ev.target.value;
        this.state.selectedValue = value;
        this.props.update(value);
    }

    get isReadonly() {
        return this.props.readonly;
    }

    isSelected(value) {
        return this.state.selectedValue === value;
    }

    get toggleOptions() {
        return [
            { value: 'none', label: 'None' },
            { value: 'target', label: 'Target' },
            { value: 'previous', label: 'Previous Period' },
        ];
    }
}

// Set supported field types
KsWidgetToggle.supportedTypes = ["char"];
KsWidgetToggleKPI.supportedTypes = ["char"];
KsWidgetToggleKpiTarget.supportedTypes = ["char"];

// Register field widgets
fieldRegistry.add("ks_widget_toggle", KsWidgetToggle);
fieldRegistry.add("ks_widget_toggle_kpi", KsWidgetToggleKPI);
fieldRegistry.add("ks_widget_toggle_kpi_target", KsWidgetToggleKpiTarget);