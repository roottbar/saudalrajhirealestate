/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

export class KsQuickEditView extends Component {
    static template = "ksQuickEditViewOption";

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.action = useService("action");
        
        this.state = useState({
            item: this.props.item,
            isLoading: false,
        });
        
        this.ksDashboardController = this.props.parent;
        this.ksOriginalItemData = { ...this.props.item };
        this.item_name = this.props.item.name;
        
        onWillStart(this.onWillStart);
    }

    async onWillStart() {
        await this._ksCreateController();
    }

    async _ksCreateController() {
        this.context = {
            ...session.user_context,
            form_view_ref: 'ks_dashboard_ninja.item_quick_edit_form_view',
            res_id: this.state.item.id,
        };
        this.res_model = "ks_dashboard_ninja.item";
    }

    async ksOnQuickEditViewAction(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        
        this.state.isLoading = true;
        
        try {
            // Open form dialog for editing
            this.dialog.add(FormViewDialog, {
                res_model: this.res_model,
                res_id: this.state.item.id,
                context: this.context,
                title: _t("Quick Edit: ") + this.item_name,
                mode: "edit",
                size: "medium",
                onRecordSaved: this._onRecordSaved.bind(this),
                onRecordDeleted: this._onRecordDeleted.bind(this),
            });
        } catch (error) {
            console.error("Error opening quick edit dialog:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    async _onRecordSaved(record) {
        // Refresh the dashboard item data
        try {
            const updatedData = await this.orm.read(
                this.res_model,
                [this.state.item.id],
                []
            );
            
            if (updatedData.length > 0) {
                Object.assign(this.state.item, updatedData[0]);
                
                // Notify parent dashboard to refresh
                if (this.ksDashboardController && this.ksDashboardController.ksRefreshDashboardItem) {
                    this.ksDashboardController.ksRefreshDashboardItem(this.state.item.id);
                }
            }
        } catch (error) {
            console.error("Error refreshing item data:", error);
        }
    }

    async _onRecordDeleted() {
        // Notify parent dashboard to remove the item
        if (this.ksDashboardController && this.ksDashboardController.ksRemoveDashboardItem) {
            this.ksDashboardController.ksRemoveDashboardItem(this.state.item.id);
        }
    }

    async ksGetItemData() {
        try {
            const result = await this.orm.call(
                'ks_dashboard_ninja.item',
                'read',
                [this.state.item.id]
            );
            return result[0] || {};
        } catch (error) {
            console.error("Error fetching item data:", error);
            return {};
        }
    }

    async ksUpdateItemData(values) {
        try {
            await this.orm.write(
                'ks_dashboard_ninja.item',
                [this.state.item.id],
                values
            );
            
            // Update local state
            Object.assign(this.state.item, values);
            
            return true;
        } catch (error) {
            console.error("Error updating item data:", error);
            return false;
        }
    }

    ksResetItemData() {
        // Reset item data to original values
        Object.assign(this.state.item, this.ksOriginalItemData);
    }

    ksValidateItemData() {
        // Basic validation for required fields
        if (!this.state.item.name || this.state.item.name.trim() === '') {
            return {
                valid: false,
                message: _t("Item name is required")
            };
        }
        
        if (!this.state.item.ks_model_id) {
            return {
                valid: false,
                message: _t("Model is required")
            };
        }
        
        return {
            valid: true,
            message: ""
        };
    }

    async ksPreviewItem() {
        // Preview functionality for the dashboard item
        try {
            const previewData = await this.orm.call(
                'ks_dashboard_ninja.item',
                'ks_get_item_preview_data',
                [this.state.item.id]
            );
            
            // Open preview dialog or update preview area
            console.log("Preview data:", previewData);
            
        } catch (error) {
            console.error("Error generating preview:", error);
        }
    }

    get itemDisplayName() {
        return this.state.item.name || _t("Unnamed Item");
    }

    get isItemValid() {
        return this.ksValidateItemData().valid;
    }
}