odoo.define("petty_cash.DynamicReportPettyCashLines", function (require) {
    "use strict";

    var BasicDynamicReport = require("base_dynamic_reports.BasicDynamicReport");
    var DynamicRelationFilters = require("base_dynamic_reports.DynamicRelationFilters");
    var field_utils = require("web.field_utils");
    var rpc = require('web.rpc');
    var core = require("web.core");
    var QWeb = core.qweb;
    var _t = core._t;

    var DynamicReportPettyCashLines = BasicDynamicReport.extend({
        init: function (parent, action) {
            this._super.apply(this, arguments);

        },
        events: _.extend({}, BasicDynamicReport.prototype.events, {
            "click .js_dynamic_report_group_by": "_onClickGroupBy",
            "click .js_dynamic_report_display_options": "_onClickDisplayOptions",
            "click .js_dynamic_report_bool_filter": "_onClickExtraOptions",
        }),
        renderSearch: function () {
            this._super.apply(this, arguments);
            this.$searchView = $(
                QWeb.render(
                    "petty_cash_dynamic_report.dynamic_report_petty_cash_lines_menus",
                    {}
                )
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
            self.formdata.product_ids = [];
            self.formdata.account_ids = [];
            self.formdata.partner_ids = [];
            self.formdata.analytic_account_ids = [];
            var dynamic_RelationFilters = new DynamicRelationFilters(self, fields);

            rpc.query({
                model: 'report.dynamic.petty.cash.lines',
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

            rpc.query({
                model: 'report.dynamic.petty.cash.lines',
                method: 'filter_config_products',
            }).then(function (result) {
                fields["product_ids"] = {
                    label: _t("Products"),
                    modelName: "product.product",
                    domain: [['id', 'in', result]],
                    value: self.formdata.product_ids.map(Number),
                };
                dynamic_RelationFilters.appendTo(
                    self.$searchView.find(".js_m2m_filter")
                );
            })

            rpc.query({
                model: 'report.dynamic.petty.cash.lines',
                method: 'filter_config_accounts',
            }).then(function (result) {
                fields["account_ids"] = {
                    label: _t("Accounts"),
                    modelName: "account.account",
                    domain: [['id', 'in', result]],
                    value: self.formdata.account_ids.map(Number),
                };
                dynamic_RelationFilters.appendTo(
                    self.$searchView.find(".js_m2m_filter")
                );
            })

            rpc.query({
                model: 'report.dynamic.petty.cash.lines',
                method: 'filter_config_partners',
            }).then(function (result) {
                fields["partner_ids"] = {
                    label: _t("Partners"),
                    modelName: "res.partner",
                    domain: [['id', 'in', result]],
                    value: self.formdata.partner_ids.map(Number),
                };
                dynamic_RelationFilters.appendTo(
                    self.$searchView.find(".js_m2m_filter")
                );
            })

            rpc.query({
                model: 'report.dynamic.petty.cash.lines',
                method: 'filter_config_analytic_account',
            }).then(function (result) {
                fields["analytic_account_ids"] = {
                    label: _t("Analytic Accounts"),
                    modelName: "account.analytic.account",
                    domain: [['id', 'in', result]],
                    value: self.formdata.analytic_account_ids.map(Number),
                };
                dynamic_RelationFilters.appendTo(
                    self.$searchView.find(".js_m2m_filter")
                );
            })

            self.formdata.include_tax = false;
            self.formdata.group_by = false;
            self.formdata.display = 'all';
            // default title search menus
            self.changeTitlePeriodFilter();
            self.changeTitleDisplayOptions(_t("All"));
            self.changeTitleGroupBy(_t("Without"));
            self.getTitleExtraOptions();

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
        _onClickDisplayOptions: function (ev) {
            this.formdata.display = $(ev.currentTarget).attr("data-filter");
            this._afterChangeFilter(
                $(ev.currentTarget),
                "js_dynamic_report_display_options"
            );
            var title = $(ev.currentTarget)[0].title;
            this.changeTitleDisplayOptions(title);
        },
        changeTitleDisplayOptions: function (title) {
            var $contents = this.$searchView.find(".js_dynamic_reports_display_options").contents();
            $contents.text(_t(" Display: ") + title);
        },
        _onChangeRelationFilters: function (ev) {
            var self = this;
            self.formdata.responsible_ids = ev.data.responsible_ids;
            self.formdata.product_ids = ev.data.product_ids;
            self.formdata.account_ids = ev.data.account_ids;
            self.formdata.partner_ids = ev.data.partner_ids;
            self.formdata.analytic_account_ids = ev.data.analytic_account_ids;
            self._reload();
        },
        //    Look for proper syntax of inheriting a method
        _onClickExtraOptions: function (ev) {
            var self = this;
            var option_value = $(ev.currentTarget).attr("data-filter");
            self.formdata.option_value = !self.formdata.option_value;
            if (option_value === "unfold_all") {
                self.unfold_all(self.formdata.option_value);
            } else if (option_value === 'include_tax') {
                self.formdata.include_tax = !self.formdata.include_tax;
                self._reload();
            }

            // update date
            self._afterChangeToggleFilter($(ev.currentTarget));
        },
        unfold_all: function (option_value) {
            if (option_value) {
                $(".js_dynamic_report_foldable.folded").trigger("click");
            } else {
                $(".js_dynamic_report_foldable:not(.folded)").trigger("click");
            }
        },

    });
    core.action_registry.add(
        "DynamicReportPettyCashLines",
        DynamicReportPettyCashLines
    );
    return DynamicReportPettyCashLines;
});
