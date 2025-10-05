/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import rpc from "@web/core/network/rpc";
import * as Utils from "./utils";

/**
 * Base Google Places Autocomplete Field
 */
export class GplacesAutocompleteField extends Component {
    static template = "web_google_maps.GplacesAutocompleteField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.inputRef = useRef("input");
        this.notification = useService("notification");
        this.orm = useService("orm");
        
        this.places_autocomplete = null;
        this.component_form = Utils.GOOGLE_PLACES_COMPONENT_FORM;
        this.address_form = Utils.ADDRESS_FORM;
        this.fillfields_delimiter = {
            street: ' ',
            street2: ', ',
        };
        this.fillfields = {};
        this.lng = false;
        this.lat = false;
        this.display_name = 'name';
        this.autocomplete_settings = null;
        
        onMounted(() => {
            this._prepareWidget();
        });
        
        onWillUnmount(() => {
            this._cleanup();
        });
    }

    /**
     * Prepare widget and initialize Google Places Autocomplete
     */
    async _prepareWidget() {
        try {
            // Get autocomplete settings
            const settings = await rpc('/web/google_autocomplete_conf');
            this.autocomplete_settings = settings;
            
            // Initialize Google Places Autocomplete
            if (this.inputRef.el && typeof google !== 'undefined' && google.maps) {
                this._initAutocomplete();
            }
        } catch (error) {
            console.warn('Failed to initialize Google Places Autocomplete', error);
        }
    }

    /**
     * Initialize Google Places Autocomplete
     */
    _initAutocomplete() {
        const options = this._getAutocompleteOptions();
        
        this.places_autocomplete = new google.maps.places.Autocomplete(
            this.inputRef.el,
            options
        );
        
        google.maps.event.addListener(
            this.places_autocomplete,
            'place_changed',
            this._onPlaceChanged.bind(this)
        );
    }

    /**
     * Get autocomplete options
     */
    _getAutocompleteOptions() {
        const options = {
            types: ['geocode'],
        };
        
        if (this.autocomplete_settings) {
            if (this.autocomplete_settings.api_key) {
                // API key is already loaded globally
            }
            if (this.autocomplete_settings.lang) {
                // Language is set in the global Google Maps API load
            }
        }
        
        return options;
    }

    /**
     * Handle place changed event
     */
    _onPlaceChanged() {
        const place = this.places_autocomplete.getPlace();
        
        if (!place || !place.geometry) {
            this.notification.add(_t('No details available for input'), {
                type: 'warning',
            });
            return;
        }
        
        // Update the field value
        const displayValue = place[this.display_name] || place.formatted_address || '';
        if (this.props.record) {
            this.props.record.update({
                [this.props.name]: displayValue,
            });
        }
        
        // Fill other fields if configured
        this._fillRelatedFields(place);
    }

    /**
     * Fill related fields with place data
     */
    async _fillRelatedFields(place) {
        if (!this.props.record) return;
        
        const updates = {};
        
        // Handle geolocation fields
        if (this.lat && this.lng && place.geometry) {
            updates[this.lat] = place.geometry.location.lat();
            updates[this.lng] = place.geometry.location.lng();
        }
        
        // Handle address components
        if (place.address_components) {
            this._processAddressComponents(place.address_components, updates);
        }
        
        // Apply all updates at once
        if (Object.keys(updates).length > 0) {
            await this.props.record.update(updates);
        }
    }

    /**
     * Process Google Places address components
     */
    _processAddressComponents(components, updates) {
        // This is a simplified version - in production would handle all address parts
        components.forEach(component => {
            const types = component.types;
            
            // Example: Map street number and route to street field
            if (types.includes('street_number') || types.includes('route')) {
                // Handle street address
            }
            if (types.includes('locality')) {
                // Handle city
            }
            if (types.includes('postal_code')) {
                // Handle postal code
            }
            // ... etc
        });
    }

    /**
     * Cleanup
     */
    _cleanup() {
        if (this.places_autocomplete) {
            google.maps.event.clearInstanceListeners(this.places_autocomplete);
            this.places_autocomplete = null;
        }
    }

    /**
     * Handle input change
     */
    onChange(ev) {
        if (this.props.record) {
            this.props.record.update({
                [this.props.name]: ev.target.value,
            });
        }
    }
}

/**
 * Google Places Address Autocomplete Field
 * Extended version with address-specific handling
 */
export class GplacesAddressAutocompleteField extends GplacesAutocompleteField {
    static template = "web_google_maps.GplacesAddressAutocompleteField";

    setup() {
        super.setup();
        // Address-specific setup
        this.force_override = false;
    }

    _getAutocompleteOptions() {
        const options = super._getAutocompleteOptions();
        options.types = ['address'];
        return options;
    }

    /**
     * Enhanced address component processing
     */
    _processAddressComponents(components, updates) {
        const addressParts = {
            street_number: '',
            route: '',
            locality: '',
            postal_code: '',
            country: '',
            state: '',
        };
        
        components.forEach(component => {
            const type = component.types[0];
            const value = component.long_name || component.short_name;
            
            if (type === 'street_number') {
                addressParts.street_number = value;
            } else if (type === 'route') {
                addressParts.route = value;
            } else if (type === 'locality') {
                addressParts.locality = value;
            } else if (type === 'postal_code') {
                addressParts.postal_code = value;
            } else if (type === 'country') {
                addressParts.country = component.short_name;
            } else if (type === 'administrative_area_level_1') {
                addressParts.state = component.short_name;
            }
        });
        
        // Map to Odoo fields
        if (this.address_form) {
            if (this.address_form.street && (addressParts.street_number || addressParts.route)) {
                updates[this.address_form.street] = 
                    [addressParts.street_number, addressParts.route].filter(Boolean).join(' ');
            }
            if (this.address_form.city && addressParts.locality) {
                updates[this.address_form.city] = addressParts.locality;
            }
            if (this.address_form.zip && addressParts.postal_code) {
                updates[this.address_form.zip] = addressParts.postal_code;
            }
        }
    }
}

