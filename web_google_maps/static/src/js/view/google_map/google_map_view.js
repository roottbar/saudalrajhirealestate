/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { GoogleMapModel } from "./google_map_model";
import { GoogleMapRenderer } from "./google_map_renderer";
import { GoogleMapController } from "./google_map_controller";
import { parseMarkersColor } from "../../widgets/utils";

export const GoogleMapView = {
    type: "google_map",
    display_name: _t("Google Map"),
    icon: "fa-map-o",
    multiRecord: true,
    accesskey: "m",
    mobile_friendly: true,

    Controller: GoogleMapController,
    Renderer: GoogleMapRenderer,
    Model: GoogleMapModel,

    props: (genericProps, view) => {
        const { arch, relatedModels, resModel } = genericProps;
        const attrs = arch.attrs;
        
        const modes = ['geometry'];
        const defaultMode = 'geometry';
        const map_mode = attrs.mode ? (modes.indexOf(attrs.mode) > -1 ? attrs.mode : defaultMode) : defaultMode;
        
        const colors = parseMarkersColor(attrs.colors);
        
        return {
            ...genericProps,
            Model: GoogleMapModel,
            Renderer: GoogleMapRenderer,
            Controller: GoogleMapController,
            mapMode: map_mode,
            markerColor: attrs.color,
            markerColors: colors,
            fieldLat: attrs.lat,
            fieldLng: attrs.lng,
            gestureHandling: attrs.gesture_handling,
            googleMapStyle: attrs.map_style || false,
            disableClusterMarker: attrs.disable_cluster_marker ? !!JSON.parse(attrs.disable_cluster_marker) : false,
            sidebarTitle: attrs.sidebar_title || false,
            sidebarSubtitle: attrs.sidebar_subtitle || false,
            disableNavigation: attrs.disable_navigation ? !!JSON.parse(attrs.disable_navigation) : false,
            limit: attrs.limit || 80,
        };
    },
};

registry.category("views").add("google_map", GoogleMapView);

