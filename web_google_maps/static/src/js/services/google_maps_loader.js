/** @odoo-module **/
import { registry } from "@web/core/registry";

const googleMapsLoaderService = {
    async start(env) {
        const orm = env.services?.orm;

        const getParam = async (key, def = "") => {
            try {
                if (orm) {
                    return await orm.call("ir.config_parameter", "get_param", [key, def]);
                }
            } catch (e) {
                // ignore and use default
            }
            return def;
        };

        const apiKey = await getParam("web_google_maps.api_key", "");
        const lang = await getParam("web_google_maps.lang_localization", "");
        const libs = await getParam("web_google_maps.libraries", "places");
        const region = await getParam("web_google_maps.region_localization", "");

        let url = "https://maps.googleapis.com/maps/api/js?v=quarterly";
        if (libs) url += `&libraries=${encodeURIComponent(libs)}`;
        if (apiKey) url += `&key=${encodeURIComponent(apiKey)}`;
        if (lang) url += `&language=${encodeURIComponent(lang)}`;
        if (region) url += `&region=${encodeURIComponent(region)}`;

        if (!document.querySelector('script[data-google-maps-loader="1"]')) {
            const s = document.createElement("script");
            s.src = url;
            s.defer = true;
            s.dataset.googleMapsLoader = "1";
            document.head.appendChild(s);
        }

        if (!document.querySelector('script[data-gmaps-markerclusterer="1"]')) {
            const m = document.createElement("script");
            m.src = "https://unpkg.com/@googlemaps/markerclusterer/dist/index.min.js";
            m.defer = true;
            m.dataset.gmapsMarkerclusterer = "1";
            document.head.appendChild(m);
        }
    },
};

registry.category("services").add("web_google_maps_loader", googleMapsLoaderService);