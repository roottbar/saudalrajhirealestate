/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { formView } from "@web/views/form/form_view";

patch(formView, {
    parseArchAttrs(attrs) {
        const result = super.parseArchAttrs(...arguments);
        
        if (attrs.geo_field) {
            try {
                const geo_field = JSON.parse(attrs.geo_field);
                if (geo_field && geo_field.lat && geo_field.lng) {
                    result.geo_field = geo_field;
                }
            } catch (e) {
                console.warn('Failed to parse geo_field attribute', e);
            }
        }
        
        return result;
    },
});

