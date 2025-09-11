odoo.define('ks_dashboard_ninja_list.ks_dashboard_ninja_list_view_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');

    var KsListViewPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.state = {};
        },

        _render: function() {
            this.$el.empty()
            var rec = this.recordData;
            if (rec.ks_dashboard_item_type === 'ks_list_view') {
                if (rec.ks_list_view_type == "ungrouped") {
                    if (rec.ks_list_view_fields.count !== 0) {
                        this.ksRenderListView();
                    } else {
                        this.$el.append($('<div>').text("Select Fields to show in list view."));
                    }
                } else if (rec.ks_list_view_type == "grouped") {
                    if (rec.ks_list_view_group_fields.count !== 0 && rec.ks_chart_relation_groupby) {
                        if (rec.ks_chart_groupby_type === 'relational_type' || rec.ks_chart_groupby_type === 'selection' || rec.ks_chart_groupby_type === 'other' || rec.ks_chart_groupby_type === 'date_type' && rec.ks_chart_date_groupby) {
                            this.ksRenderListView();
                        } else {
                            this.$el.append($('<div>').text("Select Group by Date to show list data."));
                        }

                    } else {
                        this.$el.append($('<div>').text("Select Fields and Group By to show in list view."));

                    }
                }
            }
        },

        ksRenderListView: function() {
            var self = this;
            var field = this.recordData;
            var ks_list_view_name;
            var list_view_data = JSON.parse(field.ks_list_view_data);
            var count = field.ks_record_count;
            if (field.name) ks_list_view_name = field.name;
            else if (field.ks_model_name) ks_list_view_name = field.ks_model_id.data.display_name;
            else ks_list_view_name = "Name";
        if (field.ks_list_view_type === "ungrouped" && list_view_data) {
            const index_data = list_view_data.date_index;
            if (index_data) {
                for (let i = 0; i < index_data.length; i++) {
                    for (let j = 0; j < list_view_data.data_rows.length; j++) {
                        const index = index_data[i];
                        const date = list_view_data.data_rows[j]["data"][index];
                        if (date) {
                            if (list_view_data.fields_type[index] === 'date') {
                                list_view_data.data_rows[j]["data"][index] = formatDate(new Date(date));
                            } else {
                                list_view_data.data_rows[j]["data"][index] = formatDateTime(new Date(date));
                            }
                        } else {
                            list_view_data.data_rows[j]["data"][index] = "";
                        }
                    }
                }
            }
            }

        if (field.ks_list_view_data) {
            const data_rows = list_view_data.data_rows;
            if (data_rows) {
                for (let i = 0; i < list_view_data.data_rows.length; i++) {
                    for (let j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = formatFloat(list_view_data.data_rows[i].data[j], {digits: [0, field.ks_precision_digits]});
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }
        } else list_view_data = false;
        count = list_view_data && field.ks_list_view_type === "ungrouped" ? count - list_view_data.data_rows.length : false;
        count = count ? count <= 0 ? false : count : false;
        const $listViewContainer = $(renderToElement('ks_list_view_container', {
            ks_list_view_name: ks_list_view_name,
            list_view_data: list_view_data,
            count: count,
            layout: field.ks_list_view_layout,
        }));
        if (!field.ks_show_records === true) {
            $listViewContainer.find('#ks_item_info').hide();
        }
        $(this.el).append($listViewContainer);
    }


}

registry.category("fields").add("ks_dashboard_list_view_preview", KsListViewPreview);