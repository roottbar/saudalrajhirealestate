/** @odoo-module **/

import { PivotModel } from "@web/static/src/views/pivot/pivot_model";
import { patch } from 'web.utils';

patch(PivotModel.prototype, 'web/static/src/views/pivot/pivot_model.js', {

    /**
     * Expands a specific group in the pivot table, loads the associated data,
     * and notifies the change.
     * This method overrides the base `_expandGroup` method to ensure that
     * after expanding a group, the data is reloaded and the view is updated.
     * It allows for handling dynamic data loading and user notifications in
     * the context of group expansion in the pivot view.
     * @param {Array} groupId - The unique identifier for the group to be
     expanded, consisting of row and column values.
     * @param {string} type - The type of group being expanded, either "row" or
     "col".
     * @param {Object} config - The configuration object containing data and
     metadata related to the pivot table.
     *
     * @returns {Promise} - A promise that resolves after the group has been
     expanded and the data has been reloaded.
     *
     * @override
     */
     async _expandGroup(groupId, type, config) {
        const res = super._expandGroup(...arguments);
        await this._loadData(config, false);
		this.notify();
        return res
     }
});