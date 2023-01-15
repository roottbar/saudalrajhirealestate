odoo.define('accountReports.OverDueFormView', function (require) {
"use strict";

/**
 * FollowupFormView
 *
 * The FollowupFormView is a sub-view of FormView. It's used to display
 * the Follow-up reports, and manage the complete flow (send by mail, send
 * letter, ...).
 */

var OverDueFormController = require('account_over_due.OverDueFormController');
var OverDueFormModel = require('account_over_due.OverDueFormModel');
var OverDueFormRenderer = require('account_over_due.OverDueFormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var OverDueFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: OverDueFormController,
        Model: OverDueFormModel,
        Renderer: OverDueFormRenderer,
    }),
});

viewRegistry.add('over_due_form', OverDueFormView);

return OverDueFormView;
});
