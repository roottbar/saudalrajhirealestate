/** @odoo-module **/

import { Component, onMounted, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { DataSet } from "web.data";
import { QuickCreateFormView } from "web.QuickCreateFormView";
import { AbstractAction } from "web.AbstractAction";

    class QuickEditView extends Component {
        static template = 'ksQuickEditViewOption';
        static props = {
            parent: { type: Object },
            options: { type: Object },
        };

        get events() {
            return {
                'click .ks_quick_edit_action': this.ksOnQuickEditViewAction.bind(this),
            };
        }

        setup() {
            this.ksDashboardController = this.props.parent;
            this.ksOriginalItemData = $.extend({}, this.props.options.item);
            this.item = this.props.options.item;
            this.item_name = this.props.options.item.name;

            onWillStart(this.willStart.bind(this));
            onMounted(this.start.bind(this));
        }


        async willStart() {
            await this._ksCreateController();
        }

        async _ksCreateController() {
            this.context = $.extend({}, session.user_context);
            this.context['form_view_ref'] = 'ks_dashboard_ninja.item_quick_edit_form_view';
            this.context['res_id'] = this.item.id;
            this.res_model = "ks_dashboard_ninja.item";
            this.dataset = new DataSet(this, this.res_model, this.context);
            const fieldsViews = await this.loadViews(this.dataset.model, this.context, [
                [false, 'list'],
                [false, 'form']
            ], {});
            
            this.formView = new QuickCreateFormView(fieldsViews.form, {
                context: this.context,
                modelName: this.res_model,
                userContext: this.getSession().user_context,
                currentId: this.item.id,
                index: 0,
                mode: 'edit',
                footerToButtons: true,
                default_buttons: false,
                withControlPanel: false,
                ids: [this.item.id],
            });
            
            this.controller = await this.formView.getController(this);
            this.controller._confirmChange = this._confirmChange.bind(this);
        }

        //This Function is replacing Controllers to intercept in between to fetch changed data and update our item view.
        _confirmChange(id, fields, e) {
            if (e.name === 'discard_changes' && e.target.reset) {
                // the target of the discard event is a field widget.  In that
                // case, we simply want to reset the specific field widget,
                // not the full view
                return e.target.reset(this.controller.model.get(e.target.dataPointID), e, true);
            }

            const state = this.controller.model.get(this.controller.handle);
            this.controller.renderer.confirmChange(state, id, fields, e);
            return this.ks_Update_item();
        }

        ks_Update_item() {
            const ksChanges = this.controller.renderer.state.data;

            if (ksChanges['name']) this.item['name'] = ksChanges['name'];

            this.item['ks_font_color'] = ksChanges['ks_font_color'];
            this.item['ks_icon_select'] = ksChanges['ks_icon_select'];
            this.item['ks_icon'] = ksChanges['ks_icon'];
            this.item['ks_background_color'] = ksChanges['ks_background_color'];
            this.item['ks_default_icon_color'] = ksChanges['ks_default_icon_color'];
            this.item['ks_layout'] = ksChanges['ks_layout'];
            this.item['ks_record_count'] = ksChanges['ks_record_count'];

            if (ksChanges['ks_list_view_data']) this.item['ks_list_view_data'] = ksChanges['ks_list_view_data'];

            if (ksChanges['ks_chart_data']) this.item['ks_chart_data'] = ksChanges['ks_chart_data'];

            if (ksChanges['ks_kpi_data']) this.item['ks_kpi_data'] = ksChanges['ks_kpi_data'];

            if (ksChanges['ks_list_view_type']) this.item['ks_list_view_type'] = ksChanges['ks_list_view_type'];

            if (ksChanges['ks_chart_item_color']) this.item['ks_chart_item_color'] = ksChanges['ks_chart_item_color'];

            this.ksUpdateItemView();
        }

        start() {
            // Component mounted logic
        }

        renderElement() {
            this.controller.appendTo($(this.el).find(".ks_item_field_info"));
            this.trigger('canBeRendered', {});
        }

        ksUpdateItemView() {
            this.ksDashboardController.ksUpdateDashboardItem([this.item.id]);
            this.item_el = $.find('#' + this.item.id + '.ks_dashboarditem_id');
        }

        ksDiscardChanges() {
            this.ksDashboardController.ksFetchUpdateItem(this.item.id);
            this.destroy();
        }


        ksOnQuickEditViewAction(e) {
            this.need_reset = false;
            const options = {
                'need_item_reload': false
            };
            if (e.currentTarget.dataset['ksItemAction'] === 'saveItemInfo') {
                this.controller.saveRecord().then(() => {
                    this.ksDiscardChanges();
                });
            } else if (e.currentTarget.dataset['ksItemAction'] === 'fullItemInfo') {
                this.trigger('openFullItemForm', {});
            } else {
                this.ksDiscardChanges();
            }
        }

        destroy(options) {
            this.trigger('canBeDestroyed', {});
            this.controller.destroy();
            super.destroy();
        }
    }

    export { QuickEditView };