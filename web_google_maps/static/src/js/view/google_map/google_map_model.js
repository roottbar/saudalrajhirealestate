/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

const { useState } = owl;

export class GoogleMapModel extends Component {
    static template = "web_google_maps.GoogleMapModel";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            records: [],
            groupedData: {},
            defaultGroupedBy: null,
        });
    }

    async reload(id, options = {}) {
        if (options.groupBy && !options.groupBy.length) {
            options.groupBy = this.state.defaultGroupedBy;
        }
        return this._loadRecords(options);
    }

    async load(params) {
        this.state.defaultGroupedBy = params.groupBy;
        const groupedBy = (params.groupedBy && params.groupedBy.length) ? params.groupedBy : this.state.defaultGroupedBy;
        return this._loadRecords({ ...params, groupedBy });
    }

    async _readGroup() {
        return Promise.reject();
    }

    async _loadRecords(options = {}) {
        try {
            // Implementation for loading records
            this.state.records = [];
            return this.state.records;
        } catch (error) {
            this.notification.add(_("Error loading records"), {
                type: "danger",
            });
            return [];
        }
    }
}

registry.category("views").add("google_map_model", GoogleMapModel);
