/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { relational_fields } from "@web/views/fields/relational_fields";
import { pyUtils } from "@web/core/py_js/py_utils";
import { GoogleMapRenderer } from "../renderers/google_map_renderer";
import { Utils } from "../utils";

const { useState, useRef } = owl;

    const FieldX2ManyGoogleMap = {
        setup() {
            this._super();
            this.orm = useService("orm");
            this.notification = useService("notification");
            if (this.props.archInfo && this.props.archInfo.tag === 'google_map') {
                this.mapMode = this.props.archInfo.mode ? this.props.archInfo.mode : 'geometry';
            }
        },
        async _render() {
            if (!this.props.archInfo) {
                return this._super();
            }
            const arch = this.props.archInfo;
            if (
                arch.tag == 'google_map' &&
                !this.el.className.includes('o_field_x2many_google_map')
            ) {
                const func_name = '_render_map_' + this.mapMode;
                this.renderer = this[func_name].call(this, arch);
                this.el.classList.add('o_field_x2many', 'o_field_x2many_google_map');
                return this.renderer.mount(this.el);
            }
            return this._super();
        },
        _getRenderer() {
            if (this.props.archInfo.tag === 'google_map') {
                return GoogleMapRenderer;
            }
            return this._super();
        },
        _render_map_geometry(arch) {
            // TODO: this must be taken from record/model permission
            const record_options = {
                editable: true,
                deletable: true,
                read_only_mode: this.props.readonly,
            };
            let colors;
            if (arch.attrs.colors) {
                colors = Utils.parseMarkersColor(arch.attrs.colors);
            }
            const Renderer = this._getRenderer();
            return new Renderer(this, this.props.value, {
                arch: arch,
                record_options: record_options,
                viewType: 'google_map',
                fieldLat: arch.attrs.lat,
                fieldLng: arch.attrs.lng,
                markerColor: arch.attrs.color,
                markerColors: colors,
                disableClusterMarker:
                    arch.attrs.disable_cluster_marker !== undefined
                        ? !!pyUtils.py_eval(arch.attrs.disable_cluster_marker)
                        : false,
                gestureHandling: arch.attrs.gesture_handling || 'cooperative',
                mapMode: this.mapMode,
                googleMapStyle: arch.attrs.map_style || 'default',
                sidebarTitle: arch.attrs.sidebar_title,
                sidebarSubtitle: arch.attrs.sidebar_subtitle,
            });
        },
        /**
         * Override
         */
        _renderButtons() {
            this._super();
            if (this.props.archInfo.tag === 'google_map') {
                const func_name = '_render_map_button_' + this.mapMode;
                this[func_name].call(this);
            }
        },
        _render_map_button_geometry() {
            const options = { create_text: this.props.nodeOptions.create_text, widget: this };
            this.buttonsRef = useRef('buttons');
            // Render buttons using OWL template system
            this.env.qweb.addTemplate('GoogleMapView.InlineFormButtons');
        },
        _onMapCenter(event) {
            event.preventDefault();
            event.stopPropagation();
            const func_name = '_map_center_' + this.renderer.mapMode;
            this.renderer[func_name].call(this.renderer);
        },
    };

    // Apply mixin to relational fields
    Object.assign(relational_fields.FieldOne2Many.prototype, FieldX2ManyGoogleMap);
    Object.assign(relational_fields.FieldMany2Many.prototype, FieldX2ManyGoogleMap);
