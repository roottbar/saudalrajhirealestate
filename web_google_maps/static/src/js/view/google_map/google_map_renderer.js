/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import rpc from "@web/core/network/rpc";
import * as GoogleMapUtils from "../../widgets/utils";
import { GoogleMapSidebar } from "./google_map_sidebar";

export class GoogleMapRenderer extends Component {
    static template = "web_google_maps.GoogleMapView.MapView";
    static components = { GoogleMapSidebar };

    setup() {
        this.mapContainerRef = useRef("map_container");
        this.sidebarRef = useRef("sidebar");
        this.rpc = useService("rpc");
        
        this.gmap = null;
        this.infoWindow = null;
        this.markers = [];
        this.markerCluster = null;
        this.theme = null;
        
        // Get properties from props
        this.viewTitle = this.props.arch?.attrs?.string || 'Google Maps';
        this.mapMode = this.props.mapMode || 'geometry';
        this.gestureHandling = this.props.gestureHandling || 'auto';
        
        this._initLibraryProperties();
        
        onMounted(() => {
            this._renderView();
        });
        
        onWillUnmount(() => {
            this._cleanup();
        });
    }

    /**
     * Initialize library-specific properties
     */
    _initLibraryProperties() {
        this.defaultMarkerColor = 'red';
        this.fieldLat = this.props.fieldLat;
        this.fieldLng = this.props.fieldLng;
        this.markerColor = this.props.markerColor;
        this.markerColors = this.props.markerColors;
        this.disableClusterMarker = this.props.disableClusterMarker;
        this.googleMapStyle = this.props.googleMapStyle;
        this.sidebarTitle = this.props.sidebarTitle;
        this.sidebarSubtitle = this.props.sidebarSubtitle;
        this.disableNavigation = this.props.disableNavigation;
    }

    /**
     * Initialize Google Maps
     */
    _initMap() {
        if (!this.gmap && this.mapContainerRef.el) {
            const mapElement = this.mapContainerRef.el.querySelector('.o_google_map_view');
            if (mapElement) {
                this.gmap = new google.maps.Map(mapElement, {
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    minZoom: 2,
                    maxZoom: 20,
                    fullscreenControl: true,
                    mapTypeControl: true,
                    gestureHandling: this.gestureHandling,
                });
                this.setMapTheme();
                this._postLoadMapGeometry();
            }
        }
        
        if (!this.infoWindow) {
            this.infoWindow = new google.maps.InfoWindow();
        }
    }

    /**
     * Set map theme/style
     */
    async setMapTheme() {
        if (this.googleMapStyle) {
            this._setMapTheme(this.googleMapStyle);
        } else if (!this.theme) {
            try {
                const data = await rpc('/web/map_theme');
                if (data && data.theme) {
                    this.theme = data.theme;
                    this._setMapTheme(data.theme);
                }
            } catch (error) {
                console.warn('Failed to load map theme', error);
            }
        }
    }

    /**
     * Apply theme to map
     */
    _setMapTheme(style) {
        const themes = GoogleMapUtils.MAP_THEMES;
        if (!themes || !themes[style] || style === 'default' || !this.gmap) {
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

    /**
     * Post-load map initialization for geometry mode
     */
    _postLoadMapGeometry() {
        // Add geolocate button
        if (this.gmap) {
            const geolocateBtn = document.createElement('button');
            geolocateBtn.className = 'btn btn-primary o-map-button-geolocate';
            geolocateBtn.innerHTML = '<i class="fa fa-crosshairs"></i>';
            geolocateBtn.title = _t('Find My Location');
            geolocateBtn.style.cssText = 'margin: 10px; background-color: white; border: 2px solid white; border-radius: 3px; box-shadow: 0 2px 6px rgba(0,0,0,.3); cursor: pointer; padding: 8px;';
            
            geolocateBtn.addEventListener('click', (ev) => {
                ev.preventDefault();
                if (this.props.controller) {
                    this.props.controller._geolocate();
                }
            });
            
            this.gmap.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(geolocateBtn);
        }
    }

    /**
     * Get marker icon color for a record
     */
    _getIconColor(record) {
        if (this.markerColor) {
            return this.markerColor;
        }

        if (!this.markerColors) {
            return this.defaultMarkerColor;
        }

        let result = this.defaultMarkerColor;
        for (let i = 0; i < this.markerColors.length; i++) {
            const color = this.markerColors[i][0];
            const expression = this.markerColors[i][1];
            // Simple expression evaluation - in production would use py.js
            try {
                if (eval(expression)) {
                    result = color;
                    break;
                }
            } catch (e) {
                console.warn('Failed to evaluate color expression', e);
            }
        }
        return result;
    }

    /**
     * Create a marker for a record
     */
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

        const title = record.data?.display_name || record.data?.name || '';
        if (title) {
            options.title = title;
        }

        return new google.maps.Marker(options);
    }

    /**
     * Handle marker click and show info window
     */
    _onHandleMarker(marker) {
        this.markers.push(marker);
        google.maps.event.addListener(marker, 'click', () => {
            this._showMarkerInfoWindow(marker);
        });
    }

    /**
     * Show info window for marker
     */
    _showMarkerInfoWindow(marker) {
        const record = marker._odooRecord;
        if (!record) return;

        const content = document.createElement('div');
        content.className = 'o_map_marker_info';
        
        const title = document.createElement('h6');
        title.textContent = record.data?.display_name || record.data?.name || 'Unknown';
        content.appendChild(title);
        
        const openBtn = document.createElement('button');
        openBtn.className = 'btn btn-primary btn-sm mt-2';
        openBtn.textContent = _t('Open');
        openBtn.addEventListener('click', () => {
            if (this.props.controller) {
                this.props.controller.openRecord(record.res_id);
            }
        });
        content.appendChild(openBtn);
        
        this.infoWindow.setContent(content);
        this.infoWindow.open(this.gmap, marker);
    }

    /**
     * Render markers on map
     */
    _renderMarkers() {
        const data = this.props.model?.data || [];
        
        data.forEach((record) => {
            const lat = typeof record.data[this.fieldLat] === 'number' ? record.data[this.fieldLat] : 0.0;
            const lng = typeof record.data[this.fieldLng] === 'number' ? record.data[this.fieldLng] : 0.0;
            
            if (lat !== 0.0 || lng !== 0.0) {
                const latLng = new google.maps.LatLng(lat, lng);
                const color = this._getIconColor(record);
                const marker = this._createMarker(latLng, record, color);
                this._onHandleMarker(marker);
            }
        });
    }

    /**
     * Initialize marker clustering
     */
    _initMarkerCluster() {
        if (!this.disableClusterMarker && this.markers.length > 0) {
            if (typeof markerClusterer !== 'undefined') {
                if (!this.markerCluster) {
                    this.markerCluster = new markerClusterer.MarkerClusterer({
                        map: this.gmap,
                        markers: this.markers
                    });
                } else {
                    this.markerCluster.addMarkers(this.markers);
                }
            }
        }
    }

    /**
     * Center map on markers
     */
    _map_center_geometry() {
        if (!this.gmap || this.markers.length === 0) return;
        
        const mapBounds = new google.maps.LatLngBounds();
        this.markers.forEach((marker) => {
            mapBounds.extend(marker.getPosition());
        });
        
        this.gmap.fitBounds(mapBounds);
        
        google.maps.event.addListenerOnce(this.gmap, 'idle', () => {
            google.maps.event.trigger(this.gmap, 'resize');
            if (this.gmap.getZoom() > 17) {
                this.gmap.setZoom(17);
            }
        });
    }

    /**
     * Get all markers
     */
    getMarkers() {
        return this.markers || [];
    }

    /**
     * Clear all markers
     */
    clearMarkers() {
        if (this.markerCluster) {
            this.markerCluster.clearMarkers();
        }
        
        this.markers.forEach(marker => marker.setMap(null));
        this.markers = [];
    }

    /**
     * Make marker draggable for editing
     */
    setMarkerDraggable() {
        if (this.markers.length > 0) {
            const marker = this.markers[0];
            marker.setOptions({
                optimized: false,
                draggable: true,
                animation: google.maps.Animation.BOUNCE,
            });
            
            google.maps.event.addListenerOnce(this.gmap, 'idle', () => {
                google.maps.event.trigger(this.gmap, 'resize');
            });
        }
    }

    /**
     * Disable marker dragging
     */
    disableMarkerDraggable() {
        if (this.markers.length > 0) {
            this.markers[0].setOptions({
                draggable: false,
                animation: null,
            });
        }
    }

    /**
     * Main render method
     */
    async _renderView() {
        this.clearMarkers();
        this._initMap();
        this._renderMarkers();
        this._initMarkerCluster();
        this._map_center_geometry();
    }

    /**
     * Cleanup on unmount
     */
    _cleanup() {
        if (this.gmap) {
            google.maps.event.clearInstanceListeners(this.gmap);
        }
        this.clearMarkers();
    }

    /**
     * Toggle sidebar
     */
    onToggleRightSidenav(ev) {
        const sidebar = this.sidebarRef.el?.querySelector('.o_map_right_sidebar');
        if (sidebar) {
            sidebar.classList.toggle('closed');
            sidebar.classList.toggle('open');
            
            if (sidebar.classList.contains('closed') && this.gmap) {
                const currentCenter = this.gmap.getCenter();
                google.maps.event.trigger(this.gmap, 'resize');
                this.gmap.setCenter(currentCenter);
            }
        }
    }
}
