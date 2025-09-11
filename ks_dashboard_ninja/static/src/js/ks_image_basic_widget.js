/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { FieldBinaryImage } from "@web/views/fields/binary/binary_field";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

    class KsImageWidget extends FieldBinaryImage {
        static template = 'KsFieldBinaryImage';

        setup() {
            super.setup();
            this.ksSelectedIcon = false;
            this.ks_icon_set = ['home', 'puzzle-piece', 'clock-o', 'comments-o', 'car', 'calendar', 'calendar-times-o', 'bar-chart', 'commenting-o', 'star-half-o', 'address-book-o', 'tachometer', 'search', 'money', 'line-chart', 'area-chart', 'pie-chart', 'check-square-o', 'users', 'shopping-cart', 'truck', 'user-circle-o', 'user-plus', 'sun-o', 'paper-plane', 'rss', 'gears', 'check', 'book'];
        }

        get events() {
            return {
                ...super.events,
                'click .ks_icon_container_list': this.ks_icon_container_list.bind(this),
                'click .ks_image_widget_icon_container': this.ks_image_widget_icon_container.bind(this),
                'click .ks_icon_container_open_button': this.ks_icon_container_open_button.bind(this),
                'click .ks_fa_icon_search': this.ks_fa_icon_search.bind(this),
                'keyup .ks_modal_icon_input': this.ks_modal_icon_input_enter.bind(this),
            };
        }

        _render() {
            const url = this.placeholder;
            if (this.value) {
                $(this.el).find('> img').remove();
                $(this.el).find('> span').remove();
                $('<span>').addClass('fa fa-' + this.recordData.ks_default_icon + ' fa-5x').appendTo($(this.el)).css('color', 'black');
            } else {
                const $img = $(renderToElement("FieldBinaryImage-img", {
                    widget: this,
                    url: url
                }));
                $(this.el).find('> img').remove();
                $(this.el).find('> span').remove();
                $(this.el).prepend($img);
            }

            const $ks_icon_container_modal = $(renderToElement('ks_icon_container_modal_template', {
                ks_fa_icons_set: this.ks_icon_set
            }));

            $ks_icon_container_modal.prependTo($(this.el));
        }

        //This will show modal box on clicking on open icon button.
        ks_image_widget_icon_container(e) {
            $('#ks_icon_container_modal_id').modal({
                show: true,
            });
        }


        ks_icon_container_list(e) {
            this.ksSelectedIcon = $(e.currentTarget).find('span').attr('id').split('.')[1];
            $('.ks_icon_container_list').each(function() {
                $(this).removeClass('ks_icon_selected');
            });

            $(e.currentTarget).addClass('ks_icon_selected');
            $('.ks_icon_container_open_button').show();
        }

        //Imp :  Hardcoded for svg file only. If different file, change this code to dynamic.
        ks_icon_container_open_button(e) {
            this._setValue(this.ksSelectedIcon);
        }

        ks_fa_icon_search(e) {
            $(this.el).find('.ks_fa_search_icon').remove();
            let ks_fa_icon_name = $(this.el).find('.ks_modal_icon_input')[0].value;
            if (ks_fa_icon_name.slice(0, 3) === "fa-") {
                ks_fa_icon_name = ks_fa_icon_name.slice(3);
            }
            const ks_fa_icon_render = $('<div>').addClass('ks_icon_container_list ks_fa_search_icon');
            $('<span>').attr('id', 'ks.' + ks_fa_icon_name.toLocaleLowerCase()).addClass("fa fa-" + ks_fa_icon_name.toLocaleLowerCase() + " fa-4x").appendTo($(ks_fa_icon_render));
            $(ks_fa_icon_render).appendTo($(this.el).find('.ks_icon_container_grid_view'));
        }

        ks_modal_icon_input_enter(e) {
            if (e.keyCode == 13) {
                $(this.el).find('.ks_fa_icon_search').click();
            }
        }
    }

    registry.category("fields").add('ks_image_widget', KsImageWidget);

    export { KsImageWidget };