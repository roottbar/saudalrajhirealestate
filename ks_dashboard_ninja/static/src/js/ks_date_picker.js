/** @odoo-module **/

import { DatePicker } from "@web/core/datepicker/datepicker";
import { patch } from "@web/core/utils/patch";

// Patch the DatePicker component for dashboard-specific behavior
patch(DatePicker.prototype, "ks_dashboard_ninja.ks_date_picker", {
    
    setup() {
        this._super(...arguments);
        this.isDashboardContext = this.props.name === "ks_dashboard" || 
                                 this.env.config?.viewType === "ks_dashboard";
    },

    onDateTimePickerShow() {
        this._super(...arguments);
        
        // Remove scroll event listener for dashboard context to prevent conflicts
        if (this.isDashboardContext) {
            window.removeEventListener('scroll', this._onScroll, true);
        }
    },

    onDateTimePickerHide() {
        this._super(...arguments);
        
        // Clean up any dashboard-specific event listeners
        if (this.isDashboardContext) {
            this._cleanupDashboardListeners();
        }
    },

    _cleanupDashboardListeners() {
        // Remove any dashboard-specific event listeners
        if (this._dashboardScrollHandler) {
            window.removeEventListener('scroll', this._dashboardScrollHandler, true);
            this._dashboardScrollHandler = null;
        }
    },

    _onScroll(ev) {
        // Override scroll behavior for dashboard context
        if (this.isDashboardContext) {
            // Prevent default scroll handling in dashboard
            return;
        }
        return this._super(...arguments);
    },
});

export { DatePicker };