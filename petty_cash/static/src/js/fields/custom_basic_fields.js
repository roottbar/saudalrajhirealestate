odoo.define('petty_cash.custom_basic_fields', function (require) {
    "use strict";
    var basic_fields = require('web.basic_fields');

    basic_fields.FieldBinaryFile.include({
        init: function () {
            this._super.apply(this, arguments);
            this.max_upload_size = 2 * 1024 * 1024; // 2Mo
        }
    });
});