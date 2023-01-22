odoo.define("petty_cash.DynamicReportRequestFeeding", function (require) {
    "use strict";

    var BasicDynamicReport = require("base_dynamic_reports.BasicDynamicReport");
    var DynamicRelationFilters = require("base_dynamic_reports.DynamicRelationFilters");
    var field_utils = require("web.field_utils");
    var rpc = require('web.rpc');
    var core = require("web.core");
    var QWeb = core.qweb;
    var _t = core._t;


    var DynamicReportRequestFeeding = BasicDynamicReport.extend({
        init: function (parent, action) {
            this._super.apply(this, arguments);

        },
        events: _.extend({}, BasicDynamicReport.prototype.events, {
            "click .js_dynamic_report_group_by": "_onClickGroupBy",
            "click .js_dynamic_report_state": "_onClickStateFilter",
        }),
        renderSearch: function () {
            this._super.apply(this, arguments);
            this.$searchView = $(
                QWeb.render(
                    "petty_cash_dynamic_report.dynamic_report_request_feeding_menus",
                    {}
                ),
            );
        },
        _default_search: function () {
            var self = this;
            self._super.apply(self, arguments);

            // default search menu period filter
            var filter_date = self.$searchView
                .find(".js_dynamic_report_period_filter.selected")
                .attr("data-filter");

            self.formdata.filter = filter_date;
            var [date_from, date_to] = self.periodFilter(filter_date);
            self.$searchView
                .find('.o_datepicker_input[name="date_from"]')
                .val(date_from);
            self.$searchView.find('.o_datepicker_input[name="date_to"]').val(date_to);

            self.formdata.date_from = field_utils.parse.date(date_from);
            self.formdata.date_to = field_utils.parse.date(date_to);


            var fields = {};
            self.formdata.responsible_ids = [];
            self.formdata.account_ids = [];
            self.formdata.journal_ids = [];
            self.formdata.payment_journal_ids = [];
            var dynamic_RelationFilters = new DynamicRelationFilters(self, fields);

            rpc.query({
                model: 'report.dynamic.request.feeding',
                method: 'filter_config_responsible',
            }).then(function (result) {
                fields["responsible_ids"] = {
                    label: _t("Responsible Box"),
                    modelName: "res.users",
                    domain: [['id', 'in', result]],
                    value: self.formdata.responsible_ids.map(Number),
                };
                dynamic_RelationFilters.appendTo(
                    self.$searchView.find(".js_m2m_filter")
                );
            })

            fields["account_ids"] = {
                label: _t("Account"),
                modelName: "account.account",
                value: self.formdata.journal_ids.map(Number),
            };

            fields["journal_ids"] = {
                label: _t("Journal"),
                modelName: "account.journal",
                value: self.formdata.journal_ids.map(Number),
            };

            fields["payment_journal_ids"] = {
                label: _t("Payment Journal"),
                modelName: "account.journal",
                domain: [['type', 'in', ['bank', 'cash']]],
                value: self.formdata.payment_journal_ids.map(Number),
            };


            dynamic_RelationFilters.appendTo(
                self.$searchView.find(".js_m2m_filter")
            );


            self.formdata.group_by = false;
            self.formdata.state = false;
            // default title search menus
            self.changeTitlePeriodFilter();
            self.getTitleExtraOptions();
            self.changeTitleGroupBy(_t("Without"));
            self.changeTitleStateFilter(_t("All"));


        },
        _onClickGroupBy: function (ev) {
            var value = $(ev.currentTarget).attr("data-filter")
            this.formdata.group_by = value === 'without' ? false : value;
            this._afterChangeFilter(
                $(ev.currentTarget),
                "js_dynamic_report_group_by"
            );
            var title = $(ev.currentTarget)[0].title;
            this.changeTitleGroupBy(title);
        },
        changeTitleGroupBy: function (title) {
            var $contents = this.$searchView.find(".js_dynamic_reports_group_by").contents();
            $contents.text(_t(" Group By: ") + title);
        },

        _onClickStateFilter: function (ev) {
            var value = $(ev.currentTarget).attr("data-filter")
            this.formdata.state = value === 'all' ? false : value;
            this._afterChangeFilter(
                $(ev.currentTarget),
                "js_dynamic_report_state"
            );
            var title = $(ev.currentTarget)[0].title;
            this.changeTitleStateFilter(title);
        },
        changeTitleStateFilter: function (title) {
            var $contents = this.$searchView.find(".js_dynamic_reports_state_filter").contents();
            $contents.text(_t(" State: ") + title);
        },

        _onChangeRelationFilters: function (ev) {
            var self = this;
            self.formdata.responsible_ids = ev.data.responsible_ids;
            self.formdata.account_ids = ev.data.account_ids;
            self.formdata.journal_ids = ev.data.journal_ids;
            self.formdata.payment_journal_ids = ev.data.payment_journal_ids;
            self._reload();
        },
    });
    core.action_registry.add(
        "DynamicReportRequestFeeding",
        DynamicReportRequestFeeding
    );
    return DynamicReportRequestFeeding;
});