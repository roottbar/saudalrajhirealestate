odoo.define("base_dynamic_reports.BasicDynamicReport", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var session = require("web.session");
    var WarningDialog = require("web.CrashManager").WarningDialog;
    var core = require("web.core");
    var time = require("web.time");
    var field_utils = require("web.field_utils");
    var DynamicReportWidget = require("base_dynamic_reports.DynamicReportWidget");
    var QWeb = core.qweb;
    var _t = core._t;
    var framework = require("web.framework");

    var BasicDynamicReport = AbstractAction.extend({
        hasControlPanel: true,
        withControlPanel: true,
        events: {
            "click .js_foldable_trigger": "_onClickFoldableMenu",
            "click .js_dynamic_report_period_filter": "_onClickPeriodFilter",
            "click .js_dynamic_report_date_filter": "_onClickDateFilter",
            "click .js_dynamic_report_period_cmp_filter":
                "_onClickPeriodComparisonFilter",
            "click .js_dynamic_report_date_cmp_filter":
                "_onClickDateComparisonFilter",
            "click .js_dynamic_report_bool_filter": "_onClickExtraOptions",
            "click .js_dynamic_report_foldable": "_onCLickFoldableLine",
        },
        custom_events: {
            onChangeRelationFilters: "_onChangeRelationFilters",
        },
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.given_context = session.user_context;
            if (action.context) {
                this.given_context = action.context;
            }

            this.given_context.active_id =
                action.context.active_id || action.params.active_id;
            this.given_context.model =
                action.context.model || action.context.active_model || false;
            this.given_context.ttype = action.context.ttype || false;

            // report pdf (file,name)
            this.given_context.report_pdf_name = action.context.report_pdf_name;
            this.given_context.report_pdf_file = action.context.report_pdf_file;
            this.formdata = {};
        },
        willStart: function () {
            this.renderSearch();
            this._default_search();
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.set_html();
            });
        },
        get_html: function () {
            var self = this;
            var defs = [];

            return self
                ._rpc({
                    model: self.given_context.model,
                    method: "get_html",
                    args: [self.formdata],
                    context: self.given_context,
                })
                .then(function (result) {
                    self.html = result.html;

                });
        },
        set_html: function () {
            var self = this;
            var def = Promise.resolve();
            if (!this.report_widget) {
                this.dynamic_report_widget = new DynamicReportWidget(
                    this,
                    this.given_context
                );
                def = this.dynamic_report_widget.appendTo(this.$(".o_content"));
            }
            return def.then(function () {
                self._update_control_panel()
                self.dynamic_report_widget.$el.html(self.html);
                self.dynamic_report_widget.$el
                    .find(".js_header_filter")
                    .text(self._get_header_filters());
            });
        },
        _update_control_panel: function () {
            if (!this.$buttons) {
                this.renderButtons();
            }
            var status = {
                cp_content: {
                    $buttons: this.$buttons,
                    $searchview_buttons: this.$searchView,
                },
            };
            return this.updateControlPanel(status);
        },
        renderButtons: function () {
            var self = this;
            self.$buttons = $(QWeb.render("DynamicReports.buttons"), {});
            self.$buttons.on("click", function () {
                if ($(this).hasClass("o_dynamic_report_pdf")) {
                    self
                        ._rpc({
                            model: self.given_context.model,
                            method: "print_report",
                            args: [self.formdata],
                            context: self.given_context,
                        })
                        .then(function (result) {
                            var action = {
                                type: "ir.actions.report",
                                report_type: "qweb-pdf",
                                report_name: self.given_context.report_pdf_name,
                                report_file: self.given_context.report_pdf_file,
                                data: result,
                                context: {
                                    active_model: self.given_context.model,
                                },
                            };
                            return self.do_action(action);
                        });
                } else {
                    self.print_report_xlsx();
                }
            });
            return self.$buttons;
        },
        print_report_xlsx: function () {
            var self = this;
            var [columns_header, lines] = self._exportData();

            framework.blockUI();
            self.getSession().get_file({
                url: "/base_dynamic_reports/export/xlsx",
                data: {
                    data: JSON.stringify({
                        model: self.given_context.model,
                        columns_header: columns_header,
                        lines: lines,
                        ws_name: self.getTitle(),
                        filename:
                            self.getTitle().toLowerCase().replaceAll(" ", "_") + ".xlsx",
                        context: self.given_context,
                    }),
                },
                complete: framework.unblockUI,
                error: (error) = > this.call("crash_manager", "rpc_error", error),
        })
            ;
        },
        _exportData: function () {
            var self = this,
                columns_header = [],
                lines = [];

            // get columns header
            $(
                ".o_dynamic_report_column_header > .o_dynamic_report_column_header"
            ).each(function () {
                columns_header.push($(this).text().trim());
            });

            // get rows data: {}, level,folded

            $("tbody > tr:visible").each(function () {
                var data = [];
                var level = false;
                var section = false;

                if ($(this).hasClass("o_js_dynamic_report_inner_row")) {
                    level = 3;
                } else {
                    if ($(this).hasClass("o_dynamic_reports_level0")) {
                        level = 0;

                        if ($(this).hasClass("o_dynamic_reports_totals_below_sections")) {
                            section = true;
                        }
                    } else if ($(this).hasClass("o_dynamic_reports_level1")) {
                        level = 1;
                    } else if ($(this).hasClass("o_dynamic_reports_level2")) {
                        level = 2;
                    } else if ($(this).hasClass("o_dynamic_reports_level3")) {
                        if ($(this).hasClass("total")) {
                            level = 2;
                        } else {
                            level = 3;
                        }
                    }
                }

                $(this)
                    .find("td")
                    .each(function () {
                        var colspan = parseInt($(this).attr("colspan")) || 1;
                        var line_name = $(this).find("span.dynamic_report_line_name");
                        if (line_name.length > 0) {
                            data.push({
                                value: line_name.contents().get(0).nodeValue.split(" ").join("").split("\n").join(" ").trim(),
                                colspan: colspan,
                            });
                        } else {
                            $(this)
                                .find(
                                    "span.o_dynamic_report_column_value,span.o_dynamic_reports_domain_line_3,span.o_dynamic_reports_domain_line_4"
                                )
                                .each(function () {
                                    data.push({
                                        value: $(this).text().split(" ").join("").split("\n").join(" ").trim(),
                                        colspan: colspan
                                    });
                                });
                        }
                    });

                lines.push({data: data, level: level, section: section});
            });

            return [columns_header, lines];
        },
        renderSearch: function () {
            // override this method to add search menus
        },
        _default_search: function () {
            // override default form date search in reports, just now add datepicker options in datepicker input

            this.$searchView.find(".o_datepicker").each(function () {
                $(this).datetimepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        next: "fa fa-chevron-right",
                        previous: "fa fa-chevron-left",
                        up: "fa fa-chevron-up",
                        down: "fa fa-chevron-down",
                    },
                    viewMode: "days",
                    format: time.getLangDateFormat(),
                    locale: moment.locale(),
                    allowInputToggle: true,
                    useCurrent: false,
                    buttons: {
                        showToday: true,
                        showClear: true,
                        showClose: true,
                    },
                    widgetParent: "body",
                });
            });
        },
        _get_header_filters: function (html) {
            // override to call get header filters in template
        },
        _afterChangeFilter: function (current_target, filter_class) {
            var self = this;
            // update menuitem selected in dropdown menu
            self.$searchView
                .find("." + filter_class + ".selected")
                .removeClass("selected");
            current_target.addClass("selected");

            // close all folable menus
            self.$searchView.find(".o_filters_menu.show").removeClass("show");
            self.$searchView
                .find(".js_foldable_trigger.o_open_menu")
                .trigger("click");

            // reload data in template
            self._reload();
        },
        _afterChangeToggleFilter: function (current_target) {
            var self = this;

            current_target.toggleClass("selected");

            // close all folable menus
            self.$searchView.find(".o_filters_menu.show").removeClass("show");
            self.$searchView
                .find(".js_foldable_trigger.o_open_menu")
                .trigger("click");
        },
        _onClickPeriodFilter: function (ev) {
            var self = this;
            var filter_date = $(ev.currentTarget).attr("data-filter");
            var date_from = self.$searchView.find(
                '.o_datepicker_input[name="date_from"]'
            );
            var date_to = self.$searchView.find(
                '.o_datepicker_input[name="date_to"]'
            );
            var error = false;
            self.formdata.filter = filter_date;

            if (filter_date === "custom") {
                if (date_from.length > 0) {
                    error = date_from.val() === "" || date_to.val() === "";
                    self.formdata.date_from = field_utils.parse.date(date_from.val());
                    self.formdata.date_to = field_utils.parse.date(date_to.val());
                } else {
                    error = date_to.val() === "";
                    self.formdata.date_to = field_utils.parse.date(date_to.val());
                }
            } else {
                var [new_date_from, new_date_to] = self.periodFilter(filter_date);

                date_from.val(new_date_from);
                date_to.val(new_date_to);

                self.formdata.date_from = field_utils.parse.date(new_date_from);
                self.formdata.date_to = field_utils.parse.date(new_date_to);
            }

            if (error) {
                new WarningDialog(
                    self,
                    {
                        title: _t("Odoo Warning"),
                    },
                    {
                        message: _t("Date cannot be empty"),
                    }
                ).open();
            } else {
                // change title search menu
                self.changeTitlePeriodFilter();

                // change period comparison if search period comparison menu exists
                var comparison_filter = self.$searchView
                    .find(".js_dynamic_report_period_cmp_filter.selected")
                    .attr("data-filter");

                if (
                    comparison_filter &&
                    (comparison_filter === "previous_period" ||
                        comparison_filter === "same_last_year")
                ) {
                    var [new_date_from, new_date_to] = self.periodComparisonFilter();

                    self.$searchView
                        .find('.o_datepicker_input[name="date_from_cmp"]')
                        .val(new_date_from);
                    self.$searchView
                        .find('.o_datepicker_input[name="date_to_cmp"]')
                        .val(new_date_to);

                    self.formdata.comparison_date_from = field_utils.parse.date(
                        new_date_from
                    );
                    self.formdata.comparison_date_to = field_utils.parse.date(
                        new_date_to
                    );

                    // change title search menu
                    self.changeTitlePeriodComparisonFilter();

                    // change period number in input
                    self.$searchView
                        .find('input[name="periods_number"]')
                        .val(self.formdata.number_period_comparison);
                }

                // update date
                self._afterChangeFilter(
                    $(ev.currentTarget),
                    "js_dynamic_report_period_filter"
                );
            }
        },
        _onClickDateFilter: function (ev) {
            var self = this;
            var filter_date = $(ev.currentTarget).attr("data-filter");
            var date = self.$searchView.find('.o_datepicker_input[name="date"]');
            var error = false;
            self.formdata.filter = filter_date;

            if (filter_date === "custom") {
                if (date.length > 0) {
                    error = date.val() === "";
                    self.formdata.date = field_utils.parse.date(date.val());
                }
            } else {
                var new_date = self.DateFilter(filter_date);

                date.val(new_date);
                self.formdata.date = field_utils.parse.date(new_date);
            }

            if (error) {
                new WarningDialog(
                    self,
                    {
                        title: _t("Odoo Warning"),
                    },
                    {
                        message: _t("Date cannot be empty"),
                    }
                ).open();
            } else {
                // change title search menu
                self.changeTitleDateFilter();

                // change date comparison if search date comparison menu exists
                var comparison_filter = self.$searchView
                    .find(".js_dynamic_report_date_cmp_filter.selected")
                    .attr("data-filter");

                if (
                    comparison_filter &&
                    (comparison_filter === "previous_period" ||
                        comparison_filter === "same_last_year")
                ) {
                    var new_date = self.dateComparisonFilter();

                    self.$searchView
                        .find('.o_datepicker_input[name="date_cmp"]')
                        .val(new_date);

                    self.formdata.comparison_date = field_utils.parse.date(new_date);

                    // change title search menu
                    self.changeTitleDateComparisonFilter();

                    // change period number in input
                    self.$searchView
                        .find('input[name="periods_number"]')
                        .val(self.formdata.number_period_comparison);
                }

                // update date
                self._afterChangeFilter(
                    $(ev.currentTarget),
                    "js_dynamic_report_date_filter"
                );
            }
        },
        _onClickPeriodComparisonFilter: function (ev) {
            var self = this;
            var comparison_filter = $(ev.currentTarget).attr("data-filter");
            var date_from = self.$searchView.find(
                '.o_datepicker_input[name="date_from_cmp"]'
            );
            var date_to = self.$searchView.find(
                '.o_datepicker_input[name="date_to_cmp"]'
            );
            var number_period = $(ev.currentTarget)
                .parent()
                .find('input[name="periods_number"]');
            var error = false;
            self.formdata.comparison_filter = comparison_filter;
            self.formdata.number_period_comparison =
                number_period.length > 0 ? parseInt(number_period.val()) : 1;

            if (comparison_filter === "no_comparison") {
                date_from.val("");
                date_to.val("");
                self.formdata.comparison_date_from = false;
                self.formdata.comparison_date_to = false;
            } else if (comparison_filter === "custom") {
                if (date_from.length > 0) {
                    error = date_from.val() === "" || date_to.val() === "";
                    self.formdata.comparison_date_from = field_utils.parse.date(
                        date_from.val()
                    );
                    self.formdata.comparison_date_to = field_utils.parse.date(
                        date_to.val()
                    );
                } else {
                    error = date_to.val() === "";
                    self.formdata.comparison_date_to = field_utils.parse.date(
                        date_to.val()
                    );
                }
            } else {
                var [new_date_from, new_date_to] = self.periodComparisonFilter();

                date_from.val(new_date_from);
                date_to.val(new_date_to);

                self.formdata.comparison_date_from = field_utils.parse.date(
                    new_date_from
                );
                self.formdata.comparison_date_to = field_utils.parse.date(new_date_to);
            }

            if (error) {
                new WarningDialog(
                    self,
                    {
                        title: _t("Odoo Warning"),
                    },
                    {
                        message: _t("Date cannot be empty"),
                    }
                ).open();
            } else {
                // change title search menu
                self.changeTitlePeriodComparisonFilter();

                // change period number in input
                self.$searchView
                    .find('input[name="periods_number"]')
                    .val(self.formdata.number_period_comparison);

                // update date
                self._afterChangeFilter(
                    $(ev.currentTarget),
                    "js_dynamic_report_period_cmp_filter"
                );
            }
        },
        _onClickDateComparisonFilter: function (ev) {
            var self = this;
            var comparison_filter = $(ev.currentTarget).attr("data-filter");
            var date = self.$searchView.find('.o_datepicker_input[name="date_cmp"]');
            var number_period = $(ev.currentTarget)
                .parent()
                .find('input[name="periods_number"]');
            var error = false;
            self.formdata.comparison_filter = comparison_filter;
            self.formdata.number_period_comparison =
                number_period.length > 0 ? parseInt(number_period.val()) : 1;

            if (comparison_filter === "no_comparison") {
                date.val("");
                self.formdata.comparison_date = false;
            } else if (comparison_filter === "custom") {
                if (date.length > 0) {
                    error = date.val() === "";
                    self.formdata.comparison_date = field_utils.parse.date(date.val());
                }
            } else {
                var new_date = self.dateComparisonFilter();

                date.val(new_date);

                self.formdata.comparison_date = field_utils.parse.date(new_date);
            }

            if (error) {
                new WarningDialog(
                    self,
                    {
                        title: _t("Odoo Warning"),
                    },
                    {
                        message: _t("Date cannot be empty"),
                    }
                ).open();
            } else {
                // change title search menu
                self.changeTitleDateComparisonFilter();

                // change period number in input
                self.$searchView
                    .find('input[name="periods_number"]')
                    .val(self.formdata.number_period_comparison);

                // update date
                self._afterChangeFilter(
                    $(ev.currentTarget),
                    "js_dynamic_report_date_cmp_filter"
                );
            }
        },
        periodFilter: function (filter_date) {
            var date_from, date_to;
            switch (filter_date) {
                case "today":
                    date_from = moment();
                    date_to = moment();
                    break;
                case "yesterday":
                    date_from = moment().subtract(1, "days");
                    date_to = moment().subtract(1, "days");
                    break;
                case "this_week":
                    date_from = moment().startOf("week");
                    date_to = moment().endOf("week");
                    break;
                case "this_month":
                    date_from = moment().startOf("month");
                    date_to = moment().endOf("month");
                    break;
                case "this_quarter":
                    date_from = moment().startOf("quarter");
                    date_to = moment().endOf("quarter");
                    break;
                case "this_year":
                    date_from = moment().startOf("year");
                    date_to = moment().endOf("year");
                    break;
                case "last_week":
                    date_from = moment().subtract(1, "weeks").startOf("week");
                    date_to = moment().subtract(1, "weeks").endOf("week");
                    break;
                case "last_month":
                    date_from = moment().subtract(1, "months").startOf("month");
                    date_to = moment().subtract(1, "months").endOf("month");
                    break;
                case "last_quarter":
                    date_from = moment().subtract(1, "quarter").startOf("quarter");
                    date_to = moment().subtract(1, "quarter").endOf("quarter");
                    break;
                case "last_year":
                    date_from = moment().subtract(1, "years").startOf("year");
                    date_to = moment().subtract(1, "years").endOf("year");
                    break;
            }

            return [
                date_from.format(time.getLangDateFormat()),
                date_to.format(time.getLangDateFormat()),
            ];
        },
        DateFilter: function (filter_date) {
            var date;
            switch (filter_date) {
                case "today":
                    date = moment();
                    break;
                case "yesterday":
                    date = moment().subtract(1, "days");
                    break;
                case "last_month":
                    date = moment().subtract(1, "months").endOf("month");
                    break;
                case "last_quarter":
                    date = moment().subtract(1, "quarter").endOf("quarter");
                    break;
                case "last_year":
                    date = moment().subtract(1, "years").endOf("year");
                    break;
            }

            return date.format(time.getLangDateFormat());
        },
        periodComparisonFilter: function () {
            var self = this;
            var [date_from, date_to] = [
                moment(self.formdata.date_from),
                moment(self.formdata.date_to),
            ];

            if (self.formdata.comparison_filter === "same_last_year") {
                date_from = moment(self.formdata.date_from).subtract(1, "years");
                date_to = moment(self.formdata.date_to).subtract(1, "years");
            } else {
                switch (self.formdata.filter) {
                    case "today":
                    case "yesterday":
                        date_from = date_from.subtract(1, "days");
                        date_to = date_to.subtract(1, "days");
                        break;
                    case "this_week":
                    case "last_week":
                        date_from = date_from.subtract(1, "weeks");
                        date_to = date_to.subtract(1, "weeks");
                        break;
                    case "this_month":
                    case "last_month":
                        date_from = date_from.subtract(1, "months").startOf("month");
                        date_to = date_to.subtract(1, "months").endOf("month");
                        break;
                    case "this_quarter":
                    case "last_quarter":
                        date_from = date_from.subtract(1, "quarter").startOf("quarter");
                        date_to = date_to.subtract(1, "quarter").endOf("quarter");
                        break;
                    case "this_year":
                    case "last_year":
                        date_from = date_from.subtract(1, "years").startOf("year");
                        date_to = date_to.subtract(1, "years").endOf("year");
                        break;
                    case "custom":
                        date_from = moment(self.formdata.date_from)
                            .subtract(1, "days")
                            .startOf("month");
                        date_to = moment(self.formdata.date_from)
                            .subtract(1, "days")
                            .endOf("month");
                        break;
                }
            }

            return [
                date_from.format(time.getLangDateFormat()),
                date_to.format(time.getLangDateFormat()),
            ];
        },
        dateComparisonFilter: function () {
            var self = this;
            var date = moment(self.formdata.date);

            if (self.formdata.comparison_filter === "same_last_year") {
                date = date.subtract(1, "years");
            } else {
                switch (self.formdata.filter) {
                    case "today":
                    case "yesterday":
                        date = date.subtract(1, "days");
                        break;
                    case "last_month":
                    case "custom":
                        date = date.subtract(1, "months").endOf("month");
                        break;
                    case "last_quarter":
                        date = date.subtract(1, "quarter").endOf("quarter");
                        break;
                    case "last_year":
                        date = date.subtract(1, "years").endOf("year");
                        break;
                }
            }

            return date.format(time.getLangDateFormat());
        },
        changeTitlePeriodFilter: function () {
            var $contents = this.$searchView
                .find(".js_period_filter_dropdown")
                .contents();
            var $format_date = $contents.find(".js_format_date");

            if (this.formdata.filter === "custom") {
                var [date_from, date_to] = [
                    this.formdata.date_from.format("MMM DD,YYYY"),
                    this.formdata.date_to.format("MMM DD,YYYY"),
                ];

                if ($format_date.length == 0) {
                    var title =
                        _t(' From: <span class="js_format_date">') +
                        date_from +
                        _t(
                            '</span> <br><br> <span class="o_reports_date_to"> to: <span class="js_format_date">'
                        ) +
                        date_to +
                        "</span></span>";
                    $contents.html(title);
                } else {
                    $format_date.each(function () {
                        if ($(this).parent().hasClass("o_reports_date_to")) {
                            $(this).text(date_to);
                        } else {
                            $(this).text(date_from);
                        }
                    });
                }
            } else {
                $contents.text(" " + this.getTitlePeriodFilter());
            }
        },
        changeTitleDateFilter: function () {
            var $contents = this.$searchView
                .find(".js_filter_date_dropdown")
                .contents();
            var $format_date = $contents.find(".js_format_date");

            if (this.formdata.filter === "custom") {
                var date = this.formdata.date.format("MMM D,YYYY");

                if ($format_date.length == 0) {
                    var title = _t(' Date: <span class="js_format_date">') + date;
                    $contents.html(title);
                } else {
                    $format_date.text(date);
                }
            } else {
                $contents.text(
                    _t(" As of ") + this.formdata.date.format(time.getLangDateFormat())
                );
            }
        },
        changeTitlePeriodComparisonFilter: function () {
            var $contents = this.$searchView
                .find(".js_period_comparison_dropdown")
                .contents();
            var $format_date = $contents.find(".js_format_date");

            if (
                this.formdata.comparison_filter === "custom" ||
                (this.formdata.comparison_filter === "same_last_year" &&
                    this.formdata.filter === "custom")
            ) {
                var [date_from, date_to] = [
                    this.formdata.comparison_date_from.format("MMM DD,YYYY"),
                    this.formdata.comparison_date_to.format("MMM DD,YYYY"),
                ];
                if ($format_date.length == 0) {
                    var title =
                        _t(
                            'Comparison: <span class="o_reports_date_to"> <span class="js_format_date">'
                        ) +
                        date_from +
                        '</span> </span> <span class="o_reports_date_to"> - <span class="js_format_date">' +
                        date_to +
                        "</span></span>";
                    $contents.html(title);
                } else {
                    $format_date.eq(0).text(date_from);
                    $format_date.eq(1).text(date_to);
                }
            } else {
                $contents.text(" " + this.getTitleComparisonDate());
            }
        },
        changeTitleDateComparisonFilter: function () {
            var $contents = this.$searchView
                .find(".js_date_comparison_dropdown")
                .contents();
            var $format_date = $contents.find(".js_format_date");

            if (this.formdata.comparison_filter === "no_comparison") {
                $contents.text(_t(" Comparison:"));
            } else if (this.formdata.comparison_filter === "custom") {
                var date = this.formdata.comparison_date.format("MMM D,YYYY");

                if ($format_date.length == 0) {
                    var title =
                        _t(' Comparison: Date: <span class="js_format_date">') + date;
                    $contents.html(title);
                } else {
                    $format_date.text(date);
                }
            } else {
                $contents.text(
                    _t(" Comparison: As of ") +
                    this.formdata.comparison_date.format(time.getLangDateFormat())
                );
            }
        },
        getTitleComparisonDate: function () {
            var title = _t("Comparison: ");
            var date_from = this.formdata.comparison_date_from;
            if (
                this.formdata.comparison_filter === "previous_period" ||
                this.formdata.comparison_filter === "same_last_year"
            ) {
                switch (this.formdata.filter) {
                    case "today":
                    case "yesterday":
                    case "this_week":
                    case "last_week":
                        title += moment(date_from).format("MMM D,YYYY");
                        break;
                    case "this_month":
                    case "last_month":
                    case "custom":
                        title += moment(date_from).format("MMM YYYY");
                        break;
                    case "this_quarter":
                    case "last_quarter":
                        title += moment(date_from).format(_t("[Q]Q YYYY"));
                        break;
                    case "this_year":
                    case "last_year":
                        title += moment(date_from).format("YYYY");
                        break;
                }
            }

            return title;
        },
        getTitlePeriodFilter: function () {
            var [filter_date, date_from] = [
                this.formdata.filter,
                this.formdata.date_from,
            ];
            var title;
            switch (filter_date) {
                case "today":
                case "yesterday":
                case "this_week":
                case "last_week":
                    title = moment(date_from).format("MMM DD,YYYY");
                    break;
                case "this_month":
                case "last_month":
                    title = moment(date_from).format("MMM YYYY");
                    break;
                case "this_quarter":
                case "last_quarter":
                    title = moment(date_from).format(_t("[Q]Q YYYY"));
                    break;
                case "this_year":
                case "last_year":
                    title = moment(date_from).format("YYYY");
                    break;
            }
            return title;
        },
        _onClickExtraOptions: function (ev) {
            var self = this;
            var option_value = $(ev.currentTarget).attr("data-filter");
            self.formdata.option_value = !self.formdata.option_value;

            if (option_value === "unfold_all") {
                self.unfold_all(self.formdata.option_value);
            }

            // update date
            self._afterChangeToggleFilter($(ev.currentTarget));

            // change title search menu
            self.getTitleExtraOptions();
        },
        unfold_all: function (option_value) {
            if (option_value) {
                $(".js_dynamic_report_foldable.folded").trigger("click");
            } else {
                $(".js_dynamic_report_foldable:not(.folded)").trigger("click");
            }
        },
        getTitleExtraOptions: function () {
            this.$searchView
                .find(".js_extra_options_dropdown")
                .contents()
                .text(_t(" Options:"));
        },
        _onClickFoldableMenu: function (ev) {
            var $currentTarget = $(ev.currentTarget);
            $currentTarget.toggleClass("o_closed_menu o_open_menu");
            this.$searchView
                .find(
                    '.o_foldable_menu[data-filter="' +
                    $currentTarget.attr("data-filter") +
                    '"]'
                )
                .toggleClass("o_closed_menu");
        },
        _onCLickFoldableLine: function (ev) {
            var self = this;
            var $currentTarget = $(ev.currentTarget);
            var data_id = $currentTarget.data("id");
            var parent = $currentTarget.parent();
            var inner_rows = $(
                ".o_js_dynamic_report_inner_row[data-parent-id=" + data_id + "]"
            );

            if (inner_rows.length == 0) {
                self
                    ._rpc({
                        model: self.given_context.model,
                        method: "get_lines",
                        args: [self.formdata, data_id],
                        context: self.given_context,
                    })
                    .then(function (result) {
                        parent.after(result.html);
                    });
            } else {
                inner_rows.toggle();
            }

            $currentTarget
                .find(".o_dynamic_reports_caret_icon[data-id=" + data_id + "] > i")
                .toggleClass("fa-caret-right fa-caret-down");
            parent.toggleClass("o_js_dynamic_report_parent_row_unfolded");
            $currentTarget.toggleClass("folded");
        },
        _onChangeRelationFilters: function (ev) {
            // override if use many2many or many2one filters
        },
        _reload: function () {
            var self = this;
            return this.get_html().then(function () {
                self.$(".o_content").html(self.html);
                $(".js_header_filter").text(self._get_header_filters());
            });
        },
    });

    return BasicDynamicReport;
});
