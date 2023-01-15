odoo.define("base_dynamic_reports.DynamicRelationFilters", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  var RelationalFields = require("web.relational_fields");
  var StandaloneFieldManagerMixin = require("web.StandaloneFieldManagerMixin");
  var core = require("web.core");
  var QWeb = core.qweb;

  var DynamicRelationFilters = Widget.extend(StandaloneFieldManagerMixin, {
    init: function (parent, fields) {
      this._super.apply(this, arguments);
      StandaloneFieldManagerMixin.init.call(this);
      this.fields = fields;
      this.widgets = {};
    },
    willStart: function () {
      var self = this;
      var defs = [this._super.apply(this, arguments)];
      _.each(this.fields, function (field, fieldName) {
        defs.push(self._makeRelationWidget(field, fieldName));
      });
      return Promise.all(defs);
    },
    start: function () {
      var self = this;
      var $content = $(
        QWeb.render("DynamicReports.RelationWidgetTable", {
          fields: this.fields,
        })
      );
      self.$el.append($content);
      _.each(this.fields, function (field, fieldName) {
        self.widgets[fieldName].appendTo(
          $content.find("#" + fieldName + "_field")
        );
      });
      return this._super.apply(this, arguments);
    },
    _confirmChange: function () {
      var self = this;
      var result = StandaloneFieldManagerMixin._confirmChange.apply(
        this,
        arguments
      );
      var data = {};
      _.each(this.fields, function (filter, fieldName) {
        var value = self.widgets[fieldName].value;
        if (value.type === "list") {
          data[fieldName] = self.widgets[fieldName].value.res_ids;
        } else {
          data[fieldName] = self.widgets[fieldName].value.res_id;
        }
      });

      this.trigger_up("onChangeRelationFilters", data);
      return result;
    },
    _makeRelationWidget: function (fieldInfo, fieldName) {
      var self = this;
      var options = {};
      var domain = fieldInfo.domain || [];
      var type = fieldInfo.type || "many2many";
      options[fieldName] = {
        options: {
          no_create_edit: true,
          no_create: true,
        },
      };

      return this.model
        .makeRecord(
          fieldInfo.modelName,
          [
            {
              fields: [
                {
                  name: "id",
                  type: "integer",
                },
                {
                  name: "display_name",
                  type: "char",
                },
              ],
              name: fieldName,
              relation: fieldInfo.modelName,
              domain: domain,
              type: type,
              value: fieldInfo.value,
            },
          ],
          options
        )
        .then(function (recordID) {
          if (type === "many2one") {
            self.widgets[fieldName] = new RelationalFields.FieldMany2One(
              self,
              fieldName,
              self.model.get(recordID),
              { mode: "edit", noOpen: true }
            );
          } else {
            self.widgets[
              fieldName
            ] = new RelationalFields.FieldMany2ManyTags(
              self,
              fieldName,
              self.model.get(recordID),
              { mode: "edit" }
            );
          }
          self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
  });

  return DynamicRelationFilters;
});
