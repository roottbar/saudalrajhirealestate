/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

export const Utils = {
    GOOGLE_PLACES_COMPONENT_FORM: {
        street_number: 'short_name',
        route: 'long_name',
        locality: 'long_name',
        administrative_area_level_1: 'short_name',
        administrative_area_level_2: 'short_name',
        country: 'long_name',
        postal_code: 'short_name',
        postal_code_prefix: 'short_name',
    },

    ADDRESS_FORM: {
        street: ['street_number', 'route'],
        street2: ['administrative_area_level_2'],
        city: ['locality', 'administrative_area_level_2'],
        zip: ['postal_code', 'postal_code_prefix'],
        state_id: ['administrative_area_level_1'],
        country_id: ['country'],
    },

    /**
     * Fetch values for model fields
     * @param {string} model - Model name
     * @param {string} field_name - Field name
     * @param {*} value - Value to process
     * @returns {*} Processed value
     */
    fetchValues: function(model, field_name, value) {
        if (!model || !field_name || !value) {
            return value;
        }
        return value;
    },

    /**
     * Populate address fields from Google Places result
     * @param {Object} place - Google Places result
     * @param {Object} fillfields - Field mapping
     * @param {Object} delimiter - Field delimiters
     * @returns {Object} Populated address data
     */
    gmaps_populate_address: function(place, fillfields, delimiter) {
        if (!place || !place.address_components) {
            return {};
        }

        const result = {};
        const components = {};

        // Parse address components
        place.address_components.forEach(component => {
            const types = component.types;
            types.forEach(type => {
                if (this.GOOGLE_PLACES_COMPONENT_FORM[type]) {
                    const form = this.GOOGLE_PLACES_COMPONENT_FORM[type];
                    components[type] = component[form] || component.long_name;
                }
            });
        });

        // Map to Odoo fields
        Object.keys(fillfields).forEach(field => {
            const mapping = fillfields[field];
            if (Array.isArray(mapping)) {
                const values = [];
                mapping.forEach(component_type => {
                    if (components[component_type]) {
                        values.push(components[component_type]);
                    }
                });
                if (values.length > 0) {
                    const delim = delimiter[field] || ' ';
                    result[field] = values.join(delim);
                }
            } else if (components[mapping]) {
                result[field] = components[mapping];
            }
        });

        return result;
    },

    /**
     * Populate places data
     * @param {Object} place - Google Places result
     * @param {Object} fillfields - Field mapping
     * @returns {Object} Populated places data
     */
    gmaps_populate_places: function(place, fillfields) {
        if (!place) {
            return {};
        }

        const result = {};
        
        // Add geometry data if available
        if (place.geometry && place.geometry.location) {
            result.latitude = place.geometry.location.lat();
            result.longitude = place.geometry.location.lng();
        }

        // Add place details
        if (place.name) {
            result.name = place.name;
        }
        if (place.formatted_address) {
            result.formatted_address = place.formatted_address;
        }
        if (place.place_id) {
            result.place_id = place.place_id;
        }

        return result;
    },

    /**
     * Fetch country state information
     * @param {string} model - Model name
     * @param {string} country - Country code or name
     * @param {string} state - State code or name
     * @returns {Promise} State ID
     */
    fetchCountryState: async function(model, country, state) {
        if (!model || !country || !state) {
            return false;
        }

        try {
            const result = await rpc('/web/dataset/call_kw', {
                model: 'res.country.state',
                method: 'search',
                args: [[
                    ['name', 'ilike', state],
                    ['country_id.name', 'ilike', country]
                ]],
                kwargs: {
                    limit: 1
                }
            });

            return result.length > 0 ? result[0] : false;
        } catch (error) {
            console.error('Error fetching country state:', error);
            return false;
        }
    },

    /**
     * Validate coordinates
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @returns {boolean} True if valid
     */
    isValidCoordinates: function(lat, lng) {
        return typeof lat === 'number' && typeof lng === 'number' &&
               lat >= -90 && lat <= 90 &&
               lng >= -180 && lng <= 180;
    },

    /**
     * Format address string
     * @param {Object} address - Address components
     * @returns {string} Formatted address
     */
    formatAddress: function(address) {
        if (!address) {
            return '';
        }

        const parts = [];
        if (address.street) parts.push(address.street);
        if (address.street2) parts.push(address.street2);
        if (address.city) parts.push(address.city);
        if (address.state) parts.push(address.state);
        if (address.zip) parts.push(address.zip);
        if (address.country) parts.push(address.country);

        return parts.join(', ');
    }
};

export default Utils;