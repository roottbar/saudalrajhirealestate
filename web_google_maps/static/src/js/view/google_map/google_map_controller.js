/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class GoogleMapController extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.is_marker_edit = false;
        this.renderer = null;
    }

    /**
     * Check if marker editing is available in context
     */
    _isEditMarkerInContext() {
        const context = this.props.context || {};
        return context.edit_geo_field;
    }

    /**
     * Check if marker is editable
     */
    _isMarkerEditable() {
        const is_editable = this.props.model?.data?.length === 1 && this.props.mapMode === 'geometry';
        return is_editable;
    }

    /**
     * Handle button click to center map
     */
    _onButtonMapCenter(event) {
        event.stopPropagation();
        if (this.renderer) {
            const func_name = '_map_center_' + this.props.mapMode;
            if (this.renderer[func_name]) {
                this.renderer[func_name].call(this.renderer);
            }
        }
    }

    /**
     * Handle button click to create new record
     */
    _onButtonNew(event) {
        event.stopPropagation();
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: this.props.resModel,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    /**
     * Enable marker editing mode
     */
    _onEditMarker() {
        this.is_marker_edit = true;
        if (this.renderer) {
            this.renderer.setMarkerDraggable();
        }
    }

    /**
     * Prepare geolocation values from marker position
     */
    _prepareGeolocationValues(marker) {
        return {
            [this.props.fieldLat]: marker.lat(),
            [this.props.fieldLng]: marker.lng(),
        };
    }

    /**
     * Save marker position
     */
    async _onButtonSaveMarker(event) {
        event.stopPropagation();
        if (!this.renderer) return;
        
        const markers = this.renderer.getMarkers();
        if (markers.length === 0) return;
        
        const marker_position = markers[0].getPosition();
        const values = this._prepareGeolocationValues(marker_position);
        
        try {
            const resIds = this.props.model?.resIds || [];
            await this.orm.write(this.props.resModel, resIds, values);
            
            this.is_marker_edit = false;
            if (this.renderer) {
                this.renderer.disableMarkerDraggable();
            }
            
            // Reload the view
            await this.props.model?.load();
            
            this.notification.add(_t("Marker position saved successfully"), {
                type: "success",
            });
            
            // Go back in history after a short delay
            setTimeout(() => {
                window.history.back();
            }, 2000);
        } catch (error) {
            this.notification.add(_t("Failed to save marker position"), {
                type: "danger",
            });
        }
    }

    /**
     * Discard marker changes
     */
    _onButtonDiscardMarker(event) {
        event.stopPropagation();
        this.is_marker_edit = false;
        
        if (this.renderer) {
            this.renderer.disableMarkerDraggable();
        }

        if (this._isEditMarkerInContext()) {
            window.history.back();
        } else {
            // Reload the view
            if (this.props.model) {
                this.props.model.load();
            }
        }
    }

    /**
     * Handle geolocation error
     */
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

    /**
     * Handle geolocation success
     */
    _handleGeolocationSuccess(position) {
        if (!this.renderer || !this.renderer.gmap) return;
        
        const latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        const marker = new google.maps.Marker({
            position: latLng,
            map: this.renderer.gmap,
        });
        
        this.renderer.gmap.panTo(marker.getPosition());
        google.maps.event.addListenerOnce(this.renderer.gmap, 'idle', () => {
            google.maps.event.trigger(this.renderer.gmap, 'resize');
            if (this.renderer.gmap.getZoom() < 19) {
                this.renderer.gmap.setZoom(19);
            }
            google.maps.event.trigger(marker, 'click');
        });
    }

    /**
     * Geolocate user location
     */
    _geolocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                this._handleGeolocationSuccess.bind(this),
                this._handleGeolocationFailed.bind(this),
                { enableHighAccuracy: true }
            );
        }
    }

    /**
     * Open a record in form view
     */
    openRecord(resId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: this.props.resModel,
            res_id: resId,
            views: [[false, 'form']],
            target: 'current',
        });
    }
}

GoogleMapController.template = "web_google_maps.GoogleMapView";

