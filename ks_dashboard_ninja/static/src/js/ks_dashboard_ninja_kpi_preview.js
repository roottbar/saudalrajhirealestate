/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatFloat, formatInteger } from "@web/views/fields/formatters";
import { session } from "@web/session";
import { isBinSize } from "@web/core/utils/binary";
import { KsGlobalFunction } from "@ks_dashboard_ninja/js/ks_global_function";
import { renderToElement } from "@web/core/utils/render";

export class KsKpiPreview extends Component {
    static template = "ks_dashboard_ninja.KsKpiPreviewTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.supportedFieldTypes = ['char'];
        this.resetOnAnyFieldChange = true;

        this.file_type_magic_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        };
    }

    get recordData() {
        return this.props.record.data;
    }

    //        Number Formatter into shorthand function
    ksNumFormatter(num, digits) {
            var negative;
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: "k"
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "G"
                },
                {
                    value: 1E12,
                    symbol: "T"
                },
                {
                    value: 1E15,
                    symbol: "P"
                },
                {
                    value: 1E18,
                    symbol: "E"
                }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }
    }
    
    ksNumIndianFormatter(num, digits) {
            var negative;
            var si = [{
                value: 1,
                symbol: ""
            },
            {
                value: 1E3,
                symbol: "Th"
            },
            {
                value: 1E5,
                symbol: "Lakh"
            },
            {
                value: 1E7,
                symbol: "Cr"
            },
            {
                value: 1E9,
                symbol: "Arab"
            }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }

    }

    _render() {
        if (this.recordData.ks_model_id && this.recordData.ks_dashboard_item_type === "ks_kpi") {
            if (!this.recordData.ks_model_id_2) {
                if (!(this.recordData.ks_record_count_type === 'count')) {
                    if (this.recordData.ks_record_field) {
                        this.renderKpi();
                    } else {
                        return "Select a Record field ";
                    }
                } else {
                    this.renderKpi();
                }
            } else {
                if (!(this.recordData.ks_record_count_type_2 === 'count') && !(this.recordData.ks_record_count_type === 'count')) {
                    if (this.recordData.ks_record_field_2 && this.recordData.ks_record_field) {
                        this.renderKpi();
                    } else {
                        return "Select a Record fields ";
                    }
                } else if (!(this.recordData.ks_record_count_type_2 === 'count') && (this.recordData.ks_record_count_type === 'count')) {
                    if (this.recordData.ks_record_field_2) {
                        this.renderKpi();
                    } else {
                        return "Select a Record field";
                    }
                } else if ((this.recordData.ks_record_count_type_2 === 'count') && !(this.recordData.ks_record_count_type === 'count')) {
                    if (this.recordData.ks_record_field) {
                        this.renderKpi();
                    } else {
                        return "Select a Record field";
                    }
                } else {
                    this.renderKpi();
                }
            }
        } else {
            return "Select a Model first";
        }
    }
    ksSum(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data) {
        const self = this;
        const count = count_1 + count_2
        if (field.ks_multiplier_active){
            item_info['count'] = KsGlobalFunction._onKsGlobalFormatter(count* field.ks_multiplier, field.ks_data_format, field.ks_precision_digits);
            item_info['count_tooltip'] = formatFloat(count * field.ks_multiplier, {digits: [0, field.ks_precision_digits]});
        }else{
            item_info['count'] = KsGlobalFunction._onKsGlobalFormatter(count, field.ks_data_format, field.ks_precision_digits, field.ks_precision_digits);
            item_info['count_tooltip'] = formatFloat(count, {digits: [0, field.ks_precision_digits]});
        }
        if (field.ks_multiplier_active){
            count = count * field.ks_multiplier;
        }
        item_info['target_enable'] = field.ks_goal_enable;
        const ks_color = (target_1 - count) > 0 ? "red" : "green";
        item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
        item_info['ks_comparison'] = true;
        const target_deviation = (target_1 - count) > 0 ? Math.round(((target_1 - count) / target_1) * 100) : Math.round((Math.abs((target_1 - count)) / target_1) * 100);
        if (target_deviation !== Infinity) item_info.target_deviation = formatInteger(target_deviation) + "%";
        else {
            item_info.pre_arrow = false;
            item_info.target_deviation = target_deviation;
        }
        const target_progress_deviation = target_1 == 0 ? 0 : Math.round((count / target_1) * 100);
        item_info.target_progress_deviation = formatInteger(target_progress_deviation) + "%";
        $kpi_preview = $(renderToElement("ks_kpi_preview_template_2", item_info));
        $kpi_preview.find('.target_deviation').css({
            "color": ks_color
        }
        if (this.recordData.ks_target_view === "Progress Bar") {
            $kpi_preview.find('#ks_progressbar').val(target_progress_deviation)
        }
        return $kpi_preview
    }
    
    ksPercentage(count_1, count_2, field, item_info, target_1, $kpi_preview) {
        if (field.ks_multiplier_active){
            count_1 = count_1 * field.ks_multiplier;
            count_2 = count_2 * field.ks_multiplier;
        }
        let count = parseInt((count_1 / count_2) * 100);
        if (field.ks_multiplier_active){
            count = count * field.ks_multiplier;
        }
        if (!count) count = 0;
        item_info['count'] = count ? formatInteger(count) + "%" : "0%";
        item_info['count_tooltip'] = count ? count + "%" : "0%";
        item_info.target_progress_deviation = item_info['count']
        target_1 = target_1 > 100 ? 100 : target_1;
        item_info.target = target_1 + "%";
        item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
        const ks_color = (target_1 - count) > 0 ? "red" : "green";
        item_info['target_enable'] = field.ks_goal_enable;
        item_info['ks_comparison'] = false;
        item_info.target_deviation = item_info.target > 100 ? 100 : item_info.target;
        $kpi_preview = $(renderToElement("ks_kpi_preview_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": ks_color
            });
            if (this.recordData.ks_target_view === "Progress Bar") {
                $kpi_preview.find('#ks_progressbar').val(count)
            }
            return $kpi_preview;
    }
    
    renderKpi() {
        const self = this;
        const field = this.recordData;
        const kpi_data = JSON.parse(field.ks_kpi_data);
        const count_1 = kpi_data[0].record_data;
        const count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
        const target_1 = kpi_data[0].target;
        const ks_valid_date_selection = ['l_day', 't_week', 't_month', 't_quarter', 't_year'];
        const target_view = field.ks_target_view,
            pre_view = field.ks_prev_view;
        const ks_rgba_background_color = self._get_rgba_format(field.ks_background_color);
        const ks_rgba_font_color = self._get_rgba_format(field.ks_font_color)

        if (field.ks_goal_enable) {
            let diffrence = 0.0
            if(field.ks_multiplier_active){
                diffrence = (count_1 * field.ks_multiplier) - target_1
            }else{
                diffrence = count_1 - target_1
            }
            const acheive = diffrence >= 0 ? true : false;
            diffrence = Math.abs(diffrence);
            let deviation = Math.round((diffrence / target_1) * 100)
            if (deviation !== Infinity) deviation = deviation ? formatInteger(deviation) + '%' : 0 + '%';
        }
        if (field.ks_previous_period && ks_valid_date_selection.indexOf(field.ks_date_filter_selection) >= 0) {
            let previous_period_data = kpi_data[0].previous_period;
            let pre_diffrence = (count_1 - previous_period_data);
            if (field.ks_multiplier_active){
                previous_period_data = kpi_data[0].previous_period * field.ks_multiplier;
                pre_diffrence = (count_1 * field.ks_multiplier   - previous_period_data);
            }
            const pre_acheive = pre_diffrence > 0 ? true : false;
            pre_diffrence = Math.abs(pre_diffrence);
            const pre_deviation = previous_period_data ? formatInteger(parseInt((pre_diffrence / previous_period_data) * 100)) + '%' : "100%"
        }
        let target_progress_deviation = String(Math.round((count_1  / target_1) * 100));
        if(field.ks_multiplier_active){
            target_progress_deviation = String(Math.round(((count_1 * field.ks_multiplier) / target_1) * 100));
        }
        const ks_rgba_icon_color = self._get_rgba_format(field.ks_default_icon_color)
        const item_info = {
                count_1: self.ksNumFormatter(kpi_data[0]['record_data'], 1),
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
                name: field.name ? field.name : field.ks_model_id.data.display_name,
                target_progress_deviation:target_progress_deviation,
                icon_select: field.ks_icon_select,
                default_icon: field.ks_default_icon,
                icon_color: ks_rgba_icon_color,
                target_deviation: deviation,
                target_arrow: acheive ? 'up' : 'down',
                ks_enable_goal: field.ks_goal_enable,
                ks_previous_period: ks_valid_date_selection.indexOf(field.ks_date_filter_selection) >= 0 ? field.ks_previous_period : false,
                target: self.ksNumFormatter(target_1, 1),
                previous_period_data: previous_period_data,
                pre_deviation: pre_deviation,
                pre_arrow: pre_acheive ? 'up' : 'down',
                target_view: field.ks_target_view,
            }

            if (item_info.target_deviation === Infinity) item_info.target_arrow = false;
        item_info.target_progress_deviation = parseInt(item_info.target_progress_deviation) ? formatInteger(parseInt(item_info.target_progress_deviation)) : "0"
        if (field.ks_icon) {
            if (!isBinSize(field.ks_icon)) {
                // Use magic-word technique for detecting image type
                item_info['img_src'] = 'data:image/' + (self.file_type_magic_word[field.ks_icon[0]] || 'png') + ';base64,' + field.ks_icon;
            } else {
                item_info['img_src'] = session.url('/web/image', {
                    model: self.model,
                    id: JSON.stringify(self.res_id),
                    field: "ks_icon",
                    // unique forces a reload of the image when the record has been updated
                    unique: formatFloat(self.recordData.__last_update).replace(/[^0-9]/g, ''),
                });
            }
        }
            if (field.ks_multiplier_active){
                item_info['count_1'] = KsGlobalFunction._onKsGlobalFormatter(kpi_data[0]['record_data'] * field.ks_multiplier, field.ks_data_format, field.ks_precision_digits);
                item_info['count_1_tooltip'] = kpi_data[0]['record_data'] * field.ks_multiplier
            }else{
                item_info['count_1'] = KsGlobalFunction._onKsGlobalFormatter(kpi_data[0]['record_data'], field.ks_data_format, field.ks_precision_digits);
            }
            item_info['target'] = KsGlobalFunction._onKsGlobalFormatter(kpi_data[0].target, field.ks_data_format, field.ks_precision_digits);


        let $kpi_preview;
        if (!kpi_data[1]) {
            if (target_view === "Number" || !field.ks_goal_enable) {
                $kpi_preview = $(renderToElement("ks_kpi_preview_template", item_info));
            } else if (target_view === "Progress Bar" && field.ks_goal_enable) {
                $kpi_preview = $(renderToElement("ks_kpi_preview_template_3", item_info));
                $kpi_preview.find('#ks_progressbar').val(parseInt(item_info.target_progress_deviation));
            }

                if (field.ks_goal_enable) {
                    if (acheive) {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if (field.ks_previous_period && String(previous_period_data) && ks_valid_date_selection.indexOf(field.ks_date_filter_selection) >= 0) {
                    if (pre_acheive) {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if ($kpi_preview.find('.row').children().length !== 2) {
                    $kpi_preview.find('.row').children().addClass('text-center');
                }
            } else {
                switch (field.ks_data_comparison) {
                case "None":
                     if (field.ks_multiplier_active){
                        const count_tooltip = String(count_1 * field.ks_multiplier) + "/" + String(count_2 * field.ks_multiplier);
                        const count = String(self.ksNumFormatter(count_1 * field.ks_multiplier, 1)) + "/" + String(self.ksNumFormatter(count_2 * field.ks_multiplier, 1));
                        item_info['count'] = String(KsGlobalFunction._onKsGlobalFormatter(count_1 * field.ks_multiplier, field.ks_data_format, field.ks_precision_digits)) + "/" + String(KsGlobalFunction._onKsGlobalFormatter(count_2 * field.ks_multiplier, field.ks_data_format, field.ks_precision_digits));
                     }else{
                        const count_tooltip = String(count_1) + "/" + String(count_2);
                        const count = String(self.ksNumFormatter(count_1, 1)) + "/" + String(self.ksNumFormatter(count_2, 1));
                        item_info['count'] = String(KsGlobalFunction._onKsGlobalFormatter(count_1, field.ks_data_format, field.ks_precision_digits)) + "/" + String(KsGlobalFunction._onKsGlobalFormatter(count_2, field.ks_data_format, field.ks_precision_digits));
                     }

                    item_info['count_tooltip'] = count_tooltip
                    item_info['target_enable'] = false;
                    $kpi_preview = $(renderToElement("ks_kpi_preview_template_2", item_info));
                    break;
                    case "Sum":
                        $kpi_preview = self.ksSum(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Percentage":
                        $kpi_preview = self.ksPercentage(count_1, count_2, field, item_info, target_1, $kpi_preview);
                        break;
                case "Ratio":
                    const gcd = self.ks_get_gcd(Math.round(count_1), Math.round(count_2));
                    if (field.ks_data_format == 'exact'){
                        if (count_1 && count_2) {
                        item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                        item_info['count'] = formatFloat(count_1 / gcd, {digits: [0, field.ks_precision_digits]}) + ":" + formatFloat(count_2 / gcd, {digits: [0, field.ks_precision_digits]});
                        } else {
                        item_info['count_tooltip'] = count_1 + ":" + count_2;
                        item_info['count'] = count_1 + ":" + count_2
                               }
                      }else{
                        if (count_1 && count_2) {
                        item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                        item_info['count'] = KsGlobalFunction.ksNumFormatter(count_1 / gcd, 1) + ":" + KsGlobalFunction.ksNumFormatter(count_2 / gcd, 1);
                        }else {
                        item_info['count_tooltip'] = (count_1) + ":" + count_2;
                        item_info['count'] = KsGlobalFunction.ksNumFormatter(count_1, 1) + ":" + KsGlobalFunction.ksNumFormatter(count_2, 1);
                              }
                      }
                    item_info['target_enable'] = false;
                    $kpi_preview = $(renderToElement("ks_kpi_preview_template_2", item_info));
                    break;
                }
            }
        $kpi_preview.css({
            "background-color": ks_rgba_background_color,
            "color": ks_rgba_font_color,
        });
        return $kpi_preview;
    }

    ks_get_gcd(a, b) {
            return (b == 0) ? a : this.ks_get_gcd(b, a % b);
    }

    _get_rgba_format(val) {
        const rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
        rgba = rgba.map((v) => {
            return parseInt(v, 16)
        }).join(",");
        return "rgba(" + rgba + "," + val.split(',')[1] + ")";
    }
}

registry.category("fields").add("ks_dashboard_kpi_preview", KsKpiPreview);