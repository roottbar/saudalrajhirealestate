/** @odoo-module **/

import { registry } from "@web/core/registry";
import { GoogleMapView } from "./google_map/google_map_view";

registry.category("views").add("google_map", GoogleMapView);

