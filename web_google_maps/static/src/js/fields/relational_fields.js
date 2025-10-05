/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { GoogleMapRenderer } from "../view/google_map/google_map_renderer";
import { parseMarkersColor } from "../widgets/utils";

/**
 * Patch X2Many fields to support google_map view
 */
patch(X2ManyField.prototype, {
    /**
     * Get the renderer for the sub-view
     */
    get rendererComponent() {
        if (this.activeField?.viewMode === 'google_map') {
            return GoogleMapRenderer;
        }
        return super.rendererComponent;
    },

    /**
     * Get props for the google map renderer
     */
    get rendererProps() {
        const props = super.rendererProps;
        
        if (this.activeField?.viewMode === 'google_map') {
            const arch = this.activeField.ArchParser?.arch;
            if (arch) {
                const attrs = arch.attrs || {};
                const colors = parseMarkersColor(attrs.colors);
                
                Object.assign(props, {
                    mapMode: attrs.mode || 'geometry',
                    fieldLat: attrs.lat,
                    fieldLng: attrs.lng,
                    markerColor: attrs.color,
                    markerColors: colors,
                    disableClusterMarker: attrs.disable_cluster_marker ? 
                        JSON.parse(attrs.disable_cluster_marker) : false,
                    gestureHandling: attrs.gesture_handling || 'cooperative',
                    googleMapStyle: attrs.map_style || 'default',
                    sidebarTitle: attrs.sidebar_title,
                    sidebarSubtitle: attrs.sidebar_subtitle,
                });
            }
        }
        
        return props;
    },
});

