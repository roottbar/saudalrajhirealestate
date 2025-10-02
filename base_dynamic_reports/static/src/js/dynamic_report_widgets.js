odoo.define("base_dynamic_reports.DynamicReportWidget", function (require) {
  "use strict";

  var Widget = require("web.Widget");

  var DynamicReportWidget = Widget.extend({
    init: function (parent) {
      this._super.apply(this, arguments);
    },
    start: function () {
      return this._super.apply(this, arguments);
    },
  });

  return DynamicReportWidget;
});
