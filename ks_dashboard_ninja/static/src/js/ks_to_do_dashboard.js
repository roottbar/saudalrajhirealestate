/** @odoo-module **/

import { KsDashboard } from "@ks_dashboard_ninja/js/ks_dashboard";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

const { QWeb } = owl;

export class KsToDoDashboardFilter extends KsDashboard {
         events: _.extend({}, KsDashboard.prototype.events, {
        'click .ks_edit_content': '_onKsEditTask',
        'click .ks_delete_content': '_onKsDeleteContent',
        'click .header_add_btn': '_onKsAddTask',
//        'click .ks_add_section': '_onKsAddSection',
        'click .ks_li_tab': '_onKsUpdateAddButtonAttribute',
        'click .ks_do_item_active_handler': '_onKsActiveHandler',
    }

        ksRenderDashboardItems(items) {
            const self = this;
            for (let i = 0; i < items.length; i++) {
                if (items[i] && items[i].ks_dashboard_item_type === 'ks_to_do') {
                    self.ksDashboardItemRender(items[i].id, items[i]);
                }
            }
        },

        ksRenderToDoDashboardView(item){
            const self = this;
            const item_title = item.name;
            const item_id = item.id;
            const list_to_do_data = JSON.parse(item.ks_to_do_data)
            const ks_header_color = self._ks_get_rgba_format(item.ks_header_bg_color);
            const ks_font_color = self._ks_get_rgba_format(item.ks_font_color);
            const ks_rgba_button_color = self._ks_get_rgba_format(item.ks_button_color);
            const $ksItemContainer = self.ksRenderToDoView(item);
            const $ks_gridstack_container = $(QWeb.render('ks_to_do_dashboard_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                item_id: item_id,
                to_do_view_data: list_to_do_data,
                 ks_rgba_button_color:ks_rgba_button_color,
            })).addClass('ks_dashboarditem_id')
            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"background-color": ks_header_color });
            $ks_gridstack_container.find('.ks_card_header').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_li_tab').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_list_view_heading').addClass('ks_bg_to_color').css({"color": ks_font_color + ' !important' });
            $ks_gridstack_container.find('.ks_to_do_card_body').append($ksItemContainer)
            return $ks_gridstack_container;
        },

        ksRenderToDoView(item, ks_tv_play=false) {
            const self = this;
            const item_id = item.id;
            const list_to_do_data = JSON.parse(item.ks_to_do_data);
            const $todoViewContainer = $(QWeb.render('ks_to_do_dashboard_inner_container', {
                ks_to_do_view_name: "Test",
                to_do_view_data: list_to_do_data,
                item_id: item_id,
                ks_tv_play: ks_tv_play
            }));

            return $todoViewContainer
        },

        _onKsEditTask(e){
            const self = this;
            const ks_description_id = e.currentTarget.dataset.contentId;
            const ks_item_id = e.currentTarget.dataset.itemId;
            const ks_section_id = e.currentTarget.dataset.sectionId;
            const ks_description = $(e.currentTarget.parentElement.parentElement).find('.ks_description').attr('value');

            const $content = "<div><input type='text' class='ks_description' value='"+ ks_description +"' placeholder='Task'></input></div>"
            const dialog = new Dialog(this, {
            title: _t('Edit Task'),
            size: 'medium',
            $content: $content,
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    const content = $(e.currentTarget.parentElement.parentElement).find('.ks_description').val();
                    if (content.length === 0){
                        content = ks_description;
                    }
                    self.onSaveTask(content, parseInt(ks_description_id), parseInt(ks_item_id), parseInt(ks_section_id));
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        onSaveTask(content, ks_description_id, ks_item_id, ks_section_id){
            const self = this;
            this.orm.call('ks_to.do.description', 'write', [ks_description_id, {
                "ks_description": content
            }]).then(() => {
                self.ksFetchUpdateItem(ks_item_id).then(() => {
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                });
            });
        },

        _onKsDeleteContent(e){
            const self = this;
            const ks_description_id = e.currentTarget.dataset.contentId;
            const ks_item_id = e.currentTarget.dataset.itemId;
            const ks_section_id = e.currentTarget.dataset.sectionId;

            Dialog.confirm(this, (_t("Are you sure you want to remove this task?")), {
                confirm_callback: () => {
                    self.orm.call('ks_to.do.description', 'unlink', [parseInt(ks_description_id)]).then(() => {
                        self.ksFetchUpdateItem(ks_item_id).then(function(){
                            $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                            $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                            $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                            $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                        });
                    });
                },
            });
        },

        _onKsAddTask(e){
            const self = this;
            const ks_section_id = e.currentTarget.dataset.sectionId;
            const ks_item_id = e.currentTarget.dataset.itemId;
            const $content = "<div><input type='text' class='ks_section' placeholder='Task' required></input></div>"
            const dialog = new Dialog(this, {
            title: _t('New Task'),
            $content: $content,
            size: 'medium',
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    const content = $(e.currentTarget.parentElement.parentElement).find('.ks_section').val();
                    if (content.length === 0){
//                        this.do_notify(false, _t('Successfully sent to printer!'));
                    }
                    else{
                        self._onCreateTask(content, parseInt(ks_section_id), parseInt(ks_item_id));
                    }
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        _onCreateTask(content, ks_section_id, ks_item_id){
            const self = this;
            this.orm.call('ks_to.do.description', 'create', [{
                        ks_to_do_header_id: ks_section_id,
                        ks_description: content,
                    }]).then(() => {
                    self.ksFetchUpdateItem(ks_item_id).then(() => {
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                    });

                });
        },


        _onKsUpdateAddButtonAttribute(e){
            const item_id = e.currentTarget.dataset.itemId;
            const sectionId = e.currentTarget.dataset.sectionId;
            $(".header_add_btn[data-item-id=" + item_id + "]").attr('data-section-id', sectionId);
        },

        ksFetchUpdateItem(ks_item_id){
            const self = this;
            return this.orm.call('ks_dashboard_ninja.item', 'ks_fetch_item', [[parseInt(ks_item_id)]]).then((result) => {
                const ks_item_data = result[ks_item_id];
                self.ks_dashboard_data.ks_item_data[ks_item_id] = ks_item_data;
                self.ksDashboardItemRender(ks_item_id, ks_item_data);
            });
        },

        _onKsAddSection(e){
            const self = this;
            const ks_item_id = e.currentTarget.dataset.itemId;
            const $content = "<div><input type='text' class='ks_section' placeholder='Section' required></input></div>"
            const dialog = new Dialog(this, {
            title: _t('New Section'),
            $content: $content,
            size: 'medium',
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    const content = $(e.currentTarget.parentElement.parentElement).find('.ks_section').val();
                    if (content.length === 0){
//                        this.do_notify(false, _t('Successfully sent to printer!'));
                    }
                    else{
                        self._onCreateSection(content, parseInt(ks_item_id));
                    }
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        _onCreateSection(content, ks_item_id){
            const self = this;
            this.orm.call('ks_to.do.header', 'create', [{
                ks_to_do_item_id: ks_item_id,
                ks_to_do_header: content,
            }]).then(() => {
                self.ksFetchUpdateItem(ks_item_id).then(() => {
                    $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                    $(".ks_li_tab[data-item-id=" + ks_item_id + "]:first").addClass('active');
                    $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                    $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                    $(".ks_tab_section[data-item-id=" + ks_item_id + "]:first").addClass('active');
                    $(".ks_tab_section[data-item-id=" + ks_item_id + "]:first").addClass('show');
                    const first_section_id = $(".ks_li_tab[data-item-id=" + ks_item_id + "]:first").attr('data-section-id');
                    $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', first_section_id);
                });
            });
        },

        _onKsDeleteSection(e){
            const self = this;
            const ks_section_id = e.currentTarget.dataset.sectionId;
            const ks_item_id = e.currentTarget.dataset.itemId;

            Dialog.confirm(this, (_t("Are you sure you want to remove this section?")), {
                confirm_callback: () => {
                    self.orm.call('ks_to.do.header', 'unlink', [parseInt(ks_section_id)]).then(() => {
                        self.ksFetchUpdateItem(ks_item_id).then(() => {
                            $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_li_tab[data-item-id=" + ks_item_id + "]:first").addClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]:first").addClass('active');
                            $(".ks_tab_section[data-item-id=" + ks_item_id + "]:first").addClass('show');
                            const first_section_id = $(".ks_li_tab[data-item-id=" + ks_item_id + "]:first").attr('data-section-id');
                            $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', first_section_id);
                        });
                    });
                },
            });
        },

        _onKsActiveHandler(e){
            const self = this;
            const ks_item_id = e.currentTarget.dataset.itemId;
            const content_id = e.currentTarget.dataset.contentId;
            const ks_task_id = e.currentTarget.dataset.contentId;
            const ks_section_id = e.currentTarget.dataset.sectionId;
            let ks_value = e.currentTarget.dataset.valueId;
            if (ks_value== 'True'){
                ks_value = false
            }else{
                ks_value = true
            }
            self.content_id = content_id;
            this.orm.call('ks_to.do.description', 'write', [content_id, {
                        "ks_active": ks_value
                    }]).then(() => {
                    self.ksFetchUpdateItem(ks_item_id).then(() => {
                        $(".ks_li_tab[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_li_tab[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('active');
                        $(".ks_tab_section[data-item-id=" + ks_item_id + "]").removeClass('show');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('active');
                        $(".ks_tab_section[data-section-id=" + ks_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + ks_item_id + "]").attr('data-section-id', ks_section_id);
                    });
                });
        }
}

registry.category("actions").add("ks_to_do_dashboard_filter", KsToDoDashboardFilter);