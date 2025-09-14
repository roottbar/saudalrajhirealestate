/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { evaluateExpr } from "@web/core/py_js/py";

import { GoogleMapModel } from "./google_map_model";
import { GoogleMapRenderer } from "./google_map_renderer";
import { GoogleMapController } from "./google_map_controller";
import { parseMarkersColor } from "../utils";

export const googleMapView = {
    type: "google_map",
    display_name: _t("Google Map"),
    icon: "fa fa-map-o",
    multiRecord: true,
    Controller: GoogleMapController,
    Model: GoogleMapModel,
    Renderer: GoogleMapRenderer,
    searchMenuTypes: ["filter", "groupBy", "favorite"],
    buttonTemplate: "web_google_maps.GoogleMapView.Buttons",
    props(genericProps, view, config) {
        const { arch, fields } = view;
        const attrs = arch.attrs;
        
        const modes = ['geometry'];
        const defaultMode = 'geometry';
        const map_mode = attrs.mode && modes.includes(attrs.mode) ? attrs.mode : defaultMode;
        
        const colors = parseMarkersColor(attrs.colors);
        
        return {
            ...genericProps,
            Model: GoogleMapModel,
            Renderer: GoogleMapRenderer,
            Controller: GoogleMapController,
            arch,
            fields,
            mapMode: map_mode,
            markerColor: attrs.color,
            markerColors: colors,
            fieldLat: attrs.lat,
            fieldLng: attrs.lng,
            gestureHandling: attrs.gesture_handling,
            googleMapStyle: attrs.map_style || false,
            disableClusterMarker: attrs.disable_cluster_marker ? evaluateExpr(attrs.disable_cluster_marker) : false,
            sidebarTitle: attrs.sidebar_title || false,
            sidebarSubtitle: attrs.sidebar_subtitle || false,
            disableNavigation: attrs.disable_navigation ? evaluateExpr(attrs.disable_navigation) : false,
        };
    },
};

registry.category("views").add("google_map", googleMapView);
