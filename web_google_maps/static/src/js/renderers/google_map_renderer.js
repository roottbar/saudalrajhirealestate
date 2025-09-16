/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { Utils } from "../utils";

const { useState, useRef, onMounted, onWillUnmount } = owl;

export class GoogleMapRenderer extends Component {
    static template = "web_google_maps.GoogleMapRenderer";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.mapRef = useRef("map");
        
        this.state = useState({
            map: null,
            markers: [],
            infoWindow: null,
            markerCluster: null,
        });

        this.mapOptions = {
            zoom: 10,
            center: { lat: 24.7136, lng: 46.6753 }, // Default to Riyadh
            mapTypeId: 'roadmap',
            gestureHandling: this.props.gestureHandling || 'cooperative',
        };

        onMounted(() => this._initializeMap());
        onWillUnmount(() => this._cleanup());
    }

    async _initializeMap() {
        if (!window.google || !window.google.maps) {
            console.error('Google Maps API not loaded');
            return;
        }

        try {
            this.state.map = new google.maps.Map(this.mapRef.el, this.mapOptions);
            this.state.infoWindow = new google.maps.InfoWindow();
            
            await this._loadMarkers();
            this._setupMapEvents();
        } catch (error) {
            console.error('Error initializing Google Map:', error);
            this.notification.add(_t("Error initializing Google Map"), {
                type: "danger",
            });
        }
    }

    async _loadMarkers() {
        if (!this.props.records || !this.props.records.length) {
            return;
        }

        this._clearMarkers();
        const markers = [];

        for (const record of this.props.records) {
            const marker = await this._createMarker(record);
            if (marker) {
                markers.push(marker);
            }
        }

        this.state.markers = markers;
        this._setupMarkerCluster();
        this._fitMapBounds();
    }

    async _createMarker(record) {
        const lat = record[this.props.fieldLat];
        const lng = record[this.props.fieldLng];

        if (!Utils.isValidCoordinates(lat, lng)) {
            return null;
        }

        const position = { lat: parseFloat(lat), lng: parseFloat(lng) };
        const markerOptions = {
            position: position,
            map: this.state.map,
            title: record.display_name || record.name || '',
        };

        // Set marker color if specified
        if (this.props.markerColor) {
            const color = this._getMarkerColor(record);
            if (color) {
                markerOptions.icon = {
                    url: `https://maps.google.com/mapfiles/ms/icons/${color}-dot.png`,
                };
            }
        }

        const marker = new google.maps.Marker(markerOptions);
        
        // Add click event for info window
        marker.addListener('click', () => {
            this._showInfoWindow(marker, record);
        });

        return marker;
    }

    _getMarkerColor(record) {
        if (!this.props.markerColors) {
            return this.props.markerColor || 'red';
        }

        // Check conditions for colored markers
        for (const [condition, color] of Object.entries(this.props.markerColors)) {
            if (this._evaluateCondition(record, condition)) {
                return color;
            }
        }

        return this.props.markerColor || 'red';
    }

    _evaluateCondition(record, condition) {
        // Simple condition evaluation - can be extended
        const [field, operator, value] = condition.split(' ');
        const recordValue = record[field];

        switch (operator) {
            case '=':
            case '==':
                return recordValue == value;
            case '!=':
                return recordValue != value;
            case '>':
                return parseFloat(recordValue) > parseFloat(value);
            case '<':
                return parseFloat(recordValue) < parseFloat(value);
            default:
                return false;
        }
    }

    _showInfoWindow(marker, record) {
        const content = this._buildInfoWindowContent(record);
        this.state.infoWindow.setContent(content);
        this.state.infoWindow.open(this.state.map, marker);
    }

    _buildInfoWindowContent(record) {
        let content = `<div class="map-info-window">`;
        content += `<h6>${record.display_name || record.name || 'Record'}</h6>`;
        
        if (this.props.sidebarTitle && record[this.props.sidebarTitle]) {
            content += `<p><strong>${record[this.props.sidebarTitle]}</strong></p>`;
        }
        
        if (this.props.sidebarSubtitle && record[this.props.sidebarSubtitle]) {
            content += `<p>${record[this.props.sidebarSubtitle]}</p>`;
        }
        
        content += `</div>`;
        return content;
    }

    _setupMarkerCluster() {
        if (this.props.disableClusterMarker || !this.state.markers.length) {
            return;
        }

        if (window.MarkerClusterer) {
            this.state.markerCluster = new MarkerClusterer(this.state.map, this.state.markers, {
                imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
            });
        }
    }

    _fitMapBounds() {
        if (!this.state.markers.length) {
            return;
        }

        const bounds = new google.maps.LatLngBounds();
        this.state.markers.forEach(marker => {
            bounds.extend(marker.getPosition());
        });

        this.state.map.fitBounds(bounds);
        
        // Ensure minimum zoom level
        google.maps.event.addListenerOnce(this.state.map, 'bounds_changed', () => {
            if (this.state.map.getZoom() > 15) {
                this.state.map.setZoom(15);
            }
        });
    }

    _setupMapEvents() {
        if (!this.props.editable) {
            return;
        }

        // Add click event for creating new markers
        this.state.map.addListener('click', (event) => {
            this._onMapClick(event);
        });
    }

    _onMapClick(event) {
        if (this.props.readonly) {
            return;
        }

        const lat = event.latLng.lat();
        const lng = event.latLng.lng();
        
        this.env.bus.trigger('map:marker:create', {
            lat: lat,
            lng: lng,
        });
    }

    _clearMarkers() {
        if (this.state.markerCluster) {
            this.state.markerCluster.clearMarkers();
            this.state.markerCluster = null;
        }

        this.state.markers.forEach(marker => {
            marker.setMap(null);
        });
        this.state.markers = [];
    }

    _cleanup() {
        this._clearMarkers();
        
        if (this.state.infoWindow) {
            this.state.infoWindow.close();
        }
    }

    // Public methods for external control
    centerMap(lat, lng) {
        if (this.state.map && Utils.isValidCoordinates(lat, lng)) {
            this.state.map.setCenter({ lat: parseFloat(lat), lng: parseFloat(lng) });
        }
    }

    setZoom(zoom) {
        if (this.state.map && typeof zoom === 'number') {
            this.state.map.setZoom(zoom);
        }
    }

    refresh() {
        this._loadMarkers();
    }
}

registry.category("renderers").add("google_map_renderer", GoogleMapRenderer);