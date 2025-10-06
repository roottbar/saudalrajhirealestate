/** @odoo-module **/

import { session } from "@web/session";
import { formatFloat } from "@web/core/utils/numbers";

export const KsGlobalFunction = {
    ksNumIndianFormatter: function(num, digits) {
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
    },

    ksNumFormatter: function(num, digits) {
        var negative;
        var si = [{
            value: 1,
            symbol: ""
        },
        {
            value: 1E3,
            symbol: "K"
        },
        {
            value: 1E6,
            symbol: "M"
        },
        {
            value: 1E9,
            symbol: "B"
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
    },

    ksFormatValue: function(value, field_type, field_name, data_format) {
        var formatted_value = value;
        
        if (field_type === 'monetary') {
            var currency_id = session.get_currency(data_format.currency_id);
            if (currency_id) {
                formatted_value = formatFloat(value, {
                    digits: currency_id.digits,
                    currency_id: currency_id.id,
                });
            } else {
                formatted_value = formatFloat(value);
            }
        } else if (field_type === 'float') {
            formatted_value = formatFloat(value);
        } else if (field_type === 'integer') {
            formatted_value = parseInt(value);
        }
        
        return formatted_value;
    },

    ksGetRGBAColor: function(color, opacity) {
        if (!color) return 'rgba(255,255,255,1)';
        
        var colorArray = color.split(',');
        if (colorArray.length === 2) {
            var hex = colorArray[0];
            var alpha = opacity || colorArray[1] || 1;
            
            // Convert hex to RGB
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            if (result) {
                return `rgba(${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}, ${alpha})`;
            }
        }
        
        return color;
    },

    ksGetDarkColor: function(color, opacity, percent) {
        if (!color) return '#000000';
        
        var colorArray = color.split(',');
        var hex = colorArray[0];
        var alpha = opacity || colorArray[1] || 1;
        
        // Convert hex to RGB
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (result) {
            var r = parseInt(result[1], 16);
            var g = parseInt(result[2], 16);
            var b = parseInt(result[3], 16);
            
            // Darken the color
            var factor = (100 + (percent || -20)) / 100;
            r = Math.round(r * factor);
            g = Math.round(g * factor);
            b = Math.round(b * factor);
            
            // Ensure values are within 0-255 range
            r = Math.max(0, Math.min(255, r));
            g = Math.max(0, Math.min(255, g));
            b = Math.max(0, Math.min(255, b));
            
            return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')},${alpha}`;
        }
        
        return color;
    },

    ksGetRandomColor: function() {
        var letters = '0123456789ABCDEF';
        var color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },

    ksConvertToFloat: function(value) {
        if (typeof value === 'string') {
            return parseFloat(value.replace(/,/g, ''));
        }
        return parseFloat(value) || 0;
    },

    ksGetDateRange: function(date_filter) {
        var today = new Date();
        var start_date, end_date;
        
        switch(date_filter) {
            case 'l_day':
                start_date = new Date(today);
                end_date = new Date(today);
                break;
            case 't_week':
                var first = today.getDate() - today.getDay();
                start_date = new Date(today.setDate(first));
                end_date = new Date(today.setDate(first + 6));
                break;
            case 't_month':
                start_date = new Date(today.getFullYear(), today.getMonth(), 1);
                end_date = new Date(today.getFullYear(), today.getMonth() + 1, 0);
                break;
            case 't_quarter':
                var quarter = Math.floor((today.getMonth() + 3) / 3);
                start_date = new Date(today.getFullYear(), (quarter - 1) * 3, 1);
                end_date = new Date(today.getFullYear(), quarter * 3, 0);
                break;
            case 't_year':
                start_date = new Date(today.getFullYear(), 0, 1);
                end_date = new Date(today.getFullYear(), 11, 31);
                break;
            default:
                start_date = null;
                end_date = null;
        }
        
        return {
            start_date: start_date,
            end_date: end_date
        };
    }
};