/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { renderToFragment } from "@web/core/utils/render";
import { GoogleMapUtils } from "../utils";
import { GoogleMapSidebar } from "./google_map_sidebar";

export class GoogleMapRenderer extends Component {
    static template = "web_google_maps.GoogleMapView";
    
    setup() {
        this.mapRef = useRef("map");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.gmap = null;
        this.markers = [];
        this.markerCluster = null;
        this.infoWindow = null;
        this.editableMarkerDragEnd = null;
        
        onMounted(() => {
            this.initMap();
        });
        
        onWillUnmount(() => {
            this.destroyMap();
        });
    }
    
    get viewTitle() {
        return this.props.arch.attrs.string || 'Google Maps';
    }
    
    get fieldLat() {
        return this.props.fieldLat;
    }
    
    get fieldLng() {
        return this.props.fieldLng;
    }
    
    get markerColor() {
        return this.props.markerColor;
    }
    
    get markerColors() {
        return this.props.markerColors;
    }
    
    get defaultMarkerColor() {
        return 'red';
    }
    
    initMap() {
        if (!this.gmap && this.mapRef.el) {
            this.gmap = new google.maps.Map(this.mapRef.el, {
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                minZoom: 2,
                maxZoom: 20,
                fullscreenControl: true,
                mapTypeControl: true,
                gestureHandling: this.props.gestureHandling || 'auto',
            });
            
            this.infoWindow = new google.maps.InfoWindow();
            this.setMapTheme();
            this.renderGoogleMap();
        }
    }
    
    destroyMap() {
        if (this.editableMarkerDragEnd) {
            google.maps.event.removeListener(this.editableMarkerDragEnd);
        }
        if (this.gmap) {
            google.maps.event.clearInstanceListeners(this.gmap);
        }
    }
    
    async setMapTheme() {
        const googleMapStyle = this.props.googleMapStyle;
        if (googleMapStyle) {
            this._setMapTheme(googleMapStyle);
        } else if (!this.theme) {
            try {
                const data = await this.orm.call('ir.config_parameter', 'get_param', ['web_google_maps.map_theme']);
                if (data) {
                    this.theme = data;
                    this._setMapTheme(data);
                }
            } catch (error) {
                console.warn('Could not load map theme:', error);
            }
        }
    }
    
    _setMapTheme(style) {
        const themes = GoogleMapUtils.MAP_THEMES;
        if (!Object.prototype.hasOwnProperty.call(themes, style) || style === 'default') {
            return;
        }
        const styledMapType = new google.maps.StyledMapType(themes[style], {
            name: _t('Styled Map'),
        });
        this.gmap.setOptions({
            mapTypeControlOptions: {
                mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain', 'styled_map'],
            },
        });
        this.gmap.mapTypes.set('styled_map', styledMapType);
        this.gmap.setMapTypeId('styled_map');
    }
    
    _getIconColor(record) {
        if (this.markerColor) {
            return this.markerColor;
        }
        
        if (!this.markerColors) {
            return this.defaultMarkerColor;
        }
        
        let result = this.defaultMarkerColor;
        for (let i = 0; i < this.markerColors.length; i++) {
            const [color, expression] = this.markerColors[i];
            try {
                // Simple evaluation - in a real implementation, you'd want proper expression evaluation
                if (this._evaluateExpression(expression, record)) {
                    result = color;
                    break;
                }
            } catch (error) {
                console.warn('Error evaluating marker color expression:', error);
            }
        }
        return result;
    }
    
    _evaluateExpression(expression, record) {
        // Simplified expression evaluation - replace with proper implementation
        // This is a basic implementation for common cases
        if (expression.includes('company_type')) {
            if (expression.includes("=='person'")) {
                return record.data.company_type === 'person';
            }
            if (expression.includes("=='company'")) {
                return record.data.company_type === 'company';
            }
        }
        return false;
    }
    
    _createMarker(latLng, record, color) {
        const options = {
            position: latLng,
            map: this.gmap,
            optimized: true,
            _odooRecord: record,
            _odooMarkerColor: color,
            icon: {
                path: GoogleMapUtils.MARKER_ICON_SVG_PATH,
                fillColor: color,
                fillOpacity: 1,
                strokeWeight: 0.75,
                strokeColor: '#444',
                scale: 0.07,
                anchor: new google.maps.Point(
                    GoogleMapUtils.MARKER_ICON_WIDTH / 2,
                    GoogleMapUtils.MARKER_ICON_HEIGHT
                ),
            },
        };
        
        const title = record.data.name || record.data.display_name;
        if (title) {
            options.title = title;
        }
        
        return new google.maps.Marker(options);
    }
    
    getMarkers() {
        return this.markers || [];
    }
    
    clearMarkers() {
        if (this.markerCluster) {
            this.markerCluster.clearMarkers();
        }
        this.markers.splice(0);
    }
    
    _onHandleMarker(marker) {
        const markers = this.getMarkers();
        const existingRecords = [];
        
        if (markers.length > 0) {
            const position = marker.getPosition();
            markers.forEach((_cMarker) => {
                if (position && position.equals(_cMarker.getPosition())) {
                    marker.setMap(null);
                    existingRecords.push(_cMarker._odooRecord);
                }
            });
        }
        
        this.markers.push(marker);
        google.maps.event.addListener(marker, 'click', () => {
            this._markerInfoWindow(marker, existingRecords);
        });
    }
    
    _markerInfoWindow(marker, currentRecords = []) {
        const markerDiv = document.createElement('div');
        markerDiv.className = 'o_kanban_view';
        
        const markerContent = document.createElement('div');
        markerContent.className = 'o_kanban_group';
        
        // Add existing records
        currentRecords.forEach((record) => {
            const recordElement = this._generateMarkerInfoWindow(record);
            markerContent.appendChild(recordElement);
        });
        
        // Add current marker record
        const currentRecordElement = this._generateMarkerInfoWindow(marker._odooRecord);
        markerContent.appendChild(currentRecordElement);
        
        markerDiv.appendChild(markerContent);
        
        this.infoWindow.setContent(markerDiv);
        this.infoWindow.open(this.gmap, marker);
    }
    
    _generateMarkerInfoWindow(record) {
        const div = document.createElement('div');
        div.className = 'o_kanban_record';
        
        const title = record.data.display_name || record.data.name || '';
        const email = record.data.email || '';
        const phone = record.data.phone || '';
        
        div.innerHTML = `
            <div class="oe_kanban_details">
                <strong class="o_kanban_record_title">${title}</strong>
                ${email ? `<div>${email}</div>` : ''}
                ${phone ? `<div>${phone}</div>` : ''}
                <button class="btn btn-primary btn-sm mt-2" data-record-id="${record.id}">
                    ${_t('Open Record')}
                </button>
            </div>
        `;
        
        // Add click handler for the button
        const button = div.querySelector('button');
        if (button) {
            button.addEventListener('click', (ev) => {
                ev.preventDefault();
                this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: record.model,
                    res_id: record.id,
                    views: [[false, 'form']],
                    target: 'current',
                });
            });
        }
        
        return div;
    }
    
    _renderMarkers() {
        const records = this.props.list.records;
        
        records.forEach((record) => {
            const color = this._getIconColor(record);
            const lat = typeof record.data[this.fieldLat] === 'number' ? record.data[this.fieldLat] : 0.0;
            const lng = typeof record.data[this.fieldLng] === 'number' ? record.data[this.fieldLng] : 0.0;
            
            if (lat !== 0.0 || lng !== 0.0) {
                const latLng = new google.maps.LatLng(lat, lng);
                const marker = this._createMarker(latLng, record, color);
                this._onHandleMarker(marker);
            }
        });
    }
    
    _initMarkerCluster() {
        if (!this.props.disableClusterMarker) {
            const markers = this.getMarkers();
            if (!this.markerCluster && window.markerClusterer) {
                this.markerCluster = new markerClusterer.MarkerClusterer({ 
                    map: this.gmap, 
                    markers 
                });
            } else if (this.markerCluster) {
                this.markerCluster.addMarkers(markers);
            }
        }
    }
    
    _mapCenterGeometry() {
        const mapBounds = new google.maps.LatLngBounds();
        this.markers.forEach((marker) => {
            mapBounds.extend(marker.getPosition());
        });
        
        if (!mapBounds.isEmpty()) {
            this.gmap.fitBounds(mapBounds);
            google.maps.event.addListenerOnce(this.gmap, 'idle', () => {
                google.maps.event.trigger(this.gmap, 'resize');
                if (this.gmap.getZoom() > 17) {
                    this.gmap.setZoom(17);
                }
            });
        }
    }
    
    renderGoogleMap() {
        // Reset markers
        this.clearMarkers();
        
        // Create markers
        this._renderMarkers();
        
        // Handle marker clusterer
        this._initMarkerCluster();
        
        // Center the map
        this._mapCenterGeometry();
    }
    
    onToggleRightSidenav() {
        const sidebar = this.mapRef.el?.querySelector('.o_map_right_sidebar');
        if (sidebar) {
            sidebar.classList.toggle('closed');
            sidebar.classList.toggle('open');
            
            const button = sidebar.querySelector('.toggle_right_sidenav > button');
            if (button) {
                button.classList.toggle('closed');
            }
            
            if (sidebar.classList.contains('closed') && this.gmap) {
                const currentCenter = this.gmap.getCenter();
                google.maps.event.trigger(this.gmap, 'resize');
                this.gmap.setCenter(currentCenter);
            }
        }
    }
}
