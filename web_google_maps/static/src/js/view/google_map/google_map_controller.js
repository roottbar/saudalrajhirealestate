/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { Domain } from "@web/core/domain";
import { Context } from "@web/core/context";

const { useState } = owl;

export class GoogleMapController extends Component {
    static template = "web_google_maps.GoogleMapView";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.action = useService("action");
        this.state = useState({
            records: [],
            selectedRecord: null,
            is_marker_edit: false,
        });
    }
    get modelName() {
        return this.props.modelName;
    }
    
    get context() {
        return this.props.context;
    }
    
    get domain() {
        return this.props.domain;
    }
    
    get actionButtons() {
        return this.props.actionButtons;
    }
    
    get defaultButtons() {
        return this.props.defaultButtons;
    }
    
    get hasButtons() {
        return this.props.hasButtons;
    }
    async willStart() {
        await this._checkEditMarker();
    }
    _checkEditMarker() {
        if (this._isEditMarkerInContext()) {
            this._onEditMarker();
        }
    }
    _isEditMarkerInContext() {
        return this.context.edit_geo_field;
    }
        /**
         * @private
         * @param {Widget} kanbanRecord
         * @param {Object} params
         */
        _reloadAfterButtonClick: function (kanbanRecord, params) {
            const recordModel = this.model.localData[params.record.id];
            const group = this.model.localData[recordModel.parentID];
            const parent = this.model.localData[group.parentID];

            this.model.reload(params.record.id).then((db_id) => {
                const data = this.model.get(db_id);
                kanbanRecord.update(data);

                // Check if we still need to display the record. Some fields of the domain are
                // not guaranteed to be in data. This is for example the case if the action
                // contains a domain on a field which is not in the Kanban view. Therefore,
                // we need to handle multiple cases based on 3 variables:
                // domInData: all domain fields are in the data
                // activeInDomain: 'active' is already in the domain
                // activeInData: 'active' is available in the data

                const domain = (parent ? parent.domain : group.domain) || [];
                const domInData = _.every(domain, function (d) {
                    return d[0] in data.data;
                });
                const activeInDomain = _.pluck(domain, 0).indexOf('active') !== -1;
                const activeInData = 'active' in data.data;

                // Case # | domInData | activeInDomain | activeInData
                //   1    |   true    |      true      |      true     => no domain change
                //   2    |   true    |      true      |      false    => not possible
                //   3    |   true    |      false     |      true     => add active in domain
                //   4    |   true    |      false     |      false    => no domain change
                //   5    |   false   |      true      |      true     => no evaluation
                //   6    |   false   |      true      |      false    => no evaluation
                //   7    |   false   |      false     |      true     => replace domain
                //   8    |   false   |      false     |      false    => no evaluation

                // There are 3 cases which cannot be evaluated since we don't have all the
                // necessary information. The complete solution would be to perform a RPC in
                // these cases, but this is out of scope. A simpler one is to do a try / catch.

                if (domInData && !activeInDomain && activeInData) {
                    domain = domain.concat([['active', '=', true]]);
                } else if (!domInData && !activeInDomain && activeInData) {
                    domain = [['active', '=', true]];
                }
                let visible = null;
                try {
                    visible = new Domain(domain).compute(data.evalContext);
                } catch (e) {
                    return;
                }
                if (!visible) {
                    kanbanRecord.destroy();
                }
            });
        },
    async onButtonClicked(ev) {
        ev.stopPropagation();
        const attrs = ev.data.attrs;
        const record = ev.data.record;
        
        if (attrs.context) {
            attrs.context = new Context(attrs.context, {
                active_id: record.res_id,
                active_ids: [record.res_id],
                active_model: record.model,
            });
        }
        
        if (attrs.confirm) {
            const confirmed = await new Promise((resolve) => {
                this.dialog.add(Dialog, {
                    title: _t('Confirmation'),
                    body: attrs.confirm,
                    confirm: () => resolve(true),
                    cancel: () => resolve(false),
                });
            });
            if (!confirmed) return;
        }
        
        await this.action.doAction({
            ...attrs,
            context: { ...this.context, ...attrs.context },
        });
        
        this._reloadAfterButtonClick(ev.target, ev.data);
    }
    async onRecordDelete(event) {
        await this.orm.unlink(this.modelName, [event.data.id]);
        await this._reload();
    }
    async onUpdateRecord(ev) {
        const onSuccess = ev.data.onSuccess;
        const changes = { ...ev.data };
        delete changes.onSuccess;
        
        try {
            await this.orm.write(this.modelName, [ev.target.recordId], changes);
            if (onSuccess) onSuccess();
            await this._reload();
        } catch (error) {
            this.notification.add(_t("Error updating record"), { type: "danger" });
        }
    }
    async onArchiveRecords(ev) {
        const archive = ev.data.archive;
        const column = ev.target;
        const recordIds = column.records.map(r => r.id);
        
        if (recordIds.length) {
            try {
                const method = archive ? 'action_archive' : 'action_unarchive';
                await this.orm.call(this.modelName, method, [recordIds]);
                await this._reload();
            } catch (error) {
                this.notification.add(_t("Error archiving records"), { type: "danger" });
            }
        }
    }

    renderButtons() {
        // Buttons are now handled in the template
        return this.hasButtons;
    }
    _isMarkerEditable() {
        return this.state.records.length === 1 && this.props.mapLibrary === 'geometry';
    }
    onButtonMapCenter(event) {
        event.stopPropagation();
        const funcName = '_map_center_' + this.props.mapMode;
        if (this.props.renderer && this.props.renderer[funcName]) {
            this.props.renderer[funcName]();
        }
    }
    onButtonNew(event) {
        event.stopPropagation();
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: this.modelName,
            views: [[false, 'form']],
            target: 'current',
        });
    }
    _onEditMarker() {
        this.state.is_marker_edit = true;
        this._updateMarkerButtons();
        if (this.props.renderer) {
            this.props.renderer.setMarkerDraggable();
        }
    }
    _prepareGeolocationValues(marker) {
        return {
            [this.props.fieldLat]: marker.lat(),
            [this.props.fieldLng]: marker.lng(),
        };
    }
    async onButtonSaveMarker(event) {
        event.stopPropagation();
        
        if (!this.props.renderer) return;
        
        const markers = this.props.renderer.getMarkers();
        const markerPosition = markers[0].getPosition();
        
        this._updateMarkerButtons();
        const values = this._prepareGeolocationValues(markerPosition);
        
        try {
            await this.orm.write(this.modelName, this.state.records.map(r => r.id), values);
            this.state.is_marker_edit = false;
            this.props.renderer.disableMarkerDraggable();
            await this._reload();
            
            setTimeout(() => {
                this.action.restore();
            }, 2000);
        } catch (error) {
            this.notification.add(_t("Error saving marker position"), { type: "danger" });
        }
    }
    onButtonDiscardMarker(event) {
        event.stopPropagation();
        this.state.is_marker_edit = false;
        this._updateMarkerButtons();
        
        if (this.props.renderer) {
            this.props.renderer.disableMarkerDraggable();
        }
        
        if (this._isEditMarkerInContext()) {
            this.action.restore();
        } else {
            this._reload();
        }
    }
    _updateMarkerButtons() {
        // Button visibility is now handled in the template using state
    }
    _handleGeolocationFailed(error) {
        let msg = '';
        switch (error.code) {
            case error.PERMISSION_DENIED:
                msg = _t(
                    'User denied the request for Geolocation. Please update your configuration to allow browser detect your current location'
                );
                break;
            case error.POSITION_UNAVAILABLE:
                msg = _t('Location information is unavailable.');
                break;
            case error.TIMEOUT:
                msg = _t('The request to get user location timed out.');
                break;
            case error.UNKNOWN_ERROR:
                msg = _t('An unknown error occurred.');
                break;
        }
        if (msg) {
            this.notification.add(msg, { type: 'danger' });
        }
    }
    _handleGeolocationSuccess(position) {
        if (!this.props.renderer || !this.props.renderer.gmap) return;
        
        const latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        const marker = new google.maps.Marker({
            position: latLng,
            map: this.props.renderer.gmap,
        });
        this.props.renderer.gmap.panTo(marker.getPosition());
        google.maps.event.addListenerOnce(this.props.renderer.gmap, 'idle', () => {
            google.maps.event.trigger(this.props.renderer.gmap, 'resize');
            if (this.props.renderer.gmap.getZoom() < 19) this.props.renderer.gmap.setZoom(19);
            google.maps.event.trigger(marker, 'click');
        });
    }
    _geolocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                this._handleGeolocationSuccess.bind(this),
                this._handleGeolocationFailed.bind(this),
                { enableHighAccuracy: true }
            );
        }
    }
    
    async _reload() {
        // Reload functionality to be implemented based on the specific needs
    }
}

registry.category("views").add("google_map_controller", GoogleMapController);
