odoo.define('petty_cash.import_action', function (require) {
    "use strict";

    var DataImport = require('base_import.import');

    DataImport.DataImport.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this._target = action.target;
            this._dialog_height = action.params.height || '860px';
            this.show_required = action.params.show_required || false;
            this.import_field = action.params.import_field || false;
            this.action_id = action.jsID;
            if (this.need_import()) {
                this.parentController = this.action_manager.getCurrentController();
            }
        },
        need_import: function () {
            return this._target == 'new' && this.import_field;
        },
        exit: function () {
            if (!this.need_import()) {
                return this._super.apply(this, arguments);
            }
            if (this.action_manager.currentDialogController) {
                this.action_manager.currentDialogController.onClose;
                this.action_manager._closeDialog({ silent: true });
            }

        },
        import_options: function () {
            var options = this._super.apply(this, arguments);
            var is_import = this.need_import();
            if (options && is_import) {
                var controller = this.getController();
                var model = controller.model;
                var petty_cash = model.get(controller.handle);

                _.extend(options, {
                    import_petty_cash_line: is_import,
                    import_field: petty_cash.fields[this.import_field].relation_field,
                    petty_cash_id: petty_cash.data['name'],
                });
            }
            return options;
        },
        getController: function () {
            return this.action_manager.getCurrentController().widget;
        },

        renderButtons: function (footer) {
            var self = this;
            this._super.apply(this, arguments)

            if (footer && self.need_import()) {
                var controller = self.action_manager.currentDialogController;

                var dialog = controller.dialog
                if (controller && dialog) {
                    controller.dialog.opened().then(function () {
                        dialog.$el.css("height", self._dialog_height);
                        dialog.$footer.append(self.$buttons);

                    });
                }

            }
        },
    });

});
