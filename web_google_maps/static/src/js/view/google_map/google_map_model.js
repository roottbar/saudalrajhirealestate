/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

export class GoogleMapModel {
    constructor(orm) {
        this.orm = orm;
        this.defaultGroupedBy = null;
    }

    /**
     * Load data
     */
    async load(params) {
        this.defaultGroupedBy = params.groupBy;
        params.groupedBy = (params.groupedBy && params.groupedBy.length) ? params.groupedBy : this.defaultGroupedBy;
        return params;
    }

    /**
     * Reload data
     */
    async reload(id, options) {
        if (options && options.groupBy && !options.groupBy.length) {
            options.groupBy = this.defaultGroupedBy;
        }
        return id;
    }

    /**
     * Disable group by - not supported in map view
     */
    async _readGroup() {
        return Promise.reject();
    }
}

