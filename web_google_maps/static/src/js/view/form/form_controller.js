/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
        
        // Get geo_field from props if available
        this.geo_field = this.props.archInfo?.geo_field || false;
    },

    /**
     * Handle edit marker button click
     */
    _onButtonEditMarker() {
        const resId = this.model.root.resId;
        const resModel = this.model.root.resModel;
        
        this.action.doAction({
            name: _t('Edit Geolocation'),
            res_model: resModel,
            type: 'ir.actions.act_window',
            view_mode: 'google_map',
            domain: [['id', '=', resId]],
            views: [[false, 'google_map']],
            target: 'current',
            context: { edit_geo_field: true },
        });
    },
});
