odoo.define('contracts_management.update_kanban_tender_project', function (require) {
    'use strict';

    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        _openRecord: function () {
            if (this.modelName === 'tender.project' && this.$(".o_project_kanban_boxes a").length) {
                this.$('.o_project_kanban_boxes a').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },

    });
});
