odoo.define('suprema_attendance.DeviceConnection', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');

    var _t = core._t;

    var DeviceConnection = Widget.extend({
        template: 'suprema_attendance.DeviceStatus',
        events: {
            'click .js_test_connection': '_onTestConnection',
        },

        init: function(parent, device_id) {
            this._super.apply(this, arguments);
            this.device_id = device_id;
        },

        _onTestConnection: function() {
            var self = this;
            this.$('.js_test_connection').prop('disabled', true);
            
            ajax.jsonRpc('/suprema/device/status', 'call', {
                device_id: this.device_id,
            }).then(function(result) {
                if (result.error) {
                    self.do_notify(_t("Error"), result.error, true);
                } else {
                    self.do_notify(_t("Success"), _t("Device is connected and working properly"));
                }
            }).always(function() {
                self.$('.js_test_connection').prop('disabled', false);
            });
        },
    });

    core.action_registry.add('suprema_device_connection', DeviceConnection);

    return {
        DeviceConnection: DeviceConnection,
    };
});