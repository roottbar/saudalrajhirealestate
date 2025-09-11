/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { Dialog } from "@web/core/dialog/dialog";
import { download } from "@web/core/network/download";


export class KsDashboardImportController extends ListController {

    _getActionMenuItems(state) {
        if (!this.hasActionMenus || !this.selectedRecords.length) {
            return null;
        }
        const props = super._getActionMenuItems(...arguments);
        const otherActionItems = [];
        if (this.model.config.resModel === "ks_dashboard_ninja.board") {
        if (this.isExportEnable) {
            otherActionItems.push({
                 description: _t("Export Dashboard"),
                callback: () => this.ks_dashboard_export()
            });
        }
        if (this.archiveEnabled) {
            otherActionItems.push({
                description: _t("Archive"),
                callback: () => {
                    this.dialogService.add(Dialog, {
                        title: _t("Confirmation"),
                        body: _t("Are you sure that you want to archive all the selected records?"),
                        confirm: () => this._toggleArchiveState(true),
                    });
                }
            }, {
                description: _t("Unarchive"),
                callback: () => this._toggleArchiveState(false)
            });
        }
        if (this.activeActions.delete) {
            otherActionItems.push({
                description: _t("Delete"),
                callback: () => this._onDeleteSelectedRecords()
            });
        }} else {
            if (this.isExportEnable) {
                otherActionItems.push({
                    description: _t("Export"),
                    callback: () => this._onExportData()
                });
            }
            if (this.archiveEnabled) {
                otherActionItems.push({
                    description: _t("Archive"),
                    callback: () => {
                        this.dialogService.add(Dialog, {
                            title: _t("Confirmation"),
                            body: _t("Are you sure that you want to archive all the selected records?"),
                            confirm: () => this._toggleArchiveState(true),
                        });
                    }
                }, {
                    description: _t("Unarchive"),
                    callback: () => this._toggleArchiveState(false)
                });
            }
            if (this.activeActions.delete) {
                otherActionItems.push({
                    description: _t("Delete"),
                    callback: () => this._onDeleteSelectedRecords()
                });
            }
        }
        return Object.assign(props, {
            items: Object.assign({}, this.toolbarActions, { other: otherActionItems }),
            context: state.getContext(),
            domain: state.getDomain(),
            isDomainSelected: this.isDomainSelected,
        });
    }

    ks_dashboard_export() {
        this.ks_on_dashboard_export(this.getSelectedIds());
    }

    async ks_on_dashboard_export(ids) {
        try {
            const result = await this.orm.call('ks_dashboard_ninja.board', 'ks_dashboard_export', [JSON.stringify(ids)]);
            const name = "dashboard_ninja";
            const data = {
                "header": name,
                "dashboard_data": result,
            };
            
            await download({
                url: '/ks_dashboard_ninja/export/dashboard_json',
                data: {
                    data: JSON.stringify(data)
                },
            });
        } catch (error) {
            this.notification.add(error.message, { type: 'danger' });
        }
    }
}

registry.category("views").add("ks_dashboard_import_list", {
    ...registry.category("views").get("list"),
    Controller: KsDashboardImportController,
});