/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Utils } from "../utils";

const { useState } = owl;

    export class GplaceAutocomplete extends Component {
        static template = "web_google_maps.GplaceAutocomplete";
        static props = {
            ...standardFieldProps,
        };

        setup() {
            this.rpc = useService("rpc");
            this.notification = useService("notification");
            
            this.places_autocomplete = false;
            this.component_form = Utils.GOOGLE_PLACES_COMPONENT_FORM;
            this.address_form = Utils.ADDRESS_FORM;
            this.fillfields_delimiter = {
                street: ' ',
                street2: ', ',
            };
            this.fillfields = {};
            // Longitude, field's name that hold longitude
            this.lng = false;
            // Latitude, field's name that hold latitude
            this.lat = false;
            // Google address form/places instance attribute to be assigned to the field
            this.display_name = 'name';
            // Utilize the default `fillfields` and then combined it with the fillfields options given if any
            // or overwrite the default values and used the `fillfields` provided in the view options instead.
            // This option will be applied only on `fillfields` and `address_form`
            this.force_override = false;
            this.autocomplete_settings = null;
        }
        async willStart() {
            this.setDefault();
            try {
                this.autocomplete_settings = await this.rpc('/web/google_autocomplete_conf');
            } catch (error) {
                console.error('Failed to load autocomplete settings:', error);
            }
        }
        async onMounted() {
            await this.prepareWidgetOptions();
        }
        /**
         * Set widget default value
         */
        setDefault: function () {},
        /**
         * get fields type
         */
        getFillFieldsType: function () {
            return [];
        },
        /**
         * Prepare widget options
         */
        prepareWidgetOptions: async function () {
            if (this.props.readonly === false) {
                // update 'fillfields', 'component_form', 'delimiter' if exists
                const options = this.props.record.fields[this.props.name].options || {};
                    if (options.component_form) {
                        this.component_form = Object.assign({}, this.component_form, options.component_form);
                    }
                    if (options.delimiter) {
                        this.fillfields_delimiter = Object.assign({}, this.fillfields_delimiter, options.delimiter);
                    }
                    if (options.lat) {
                        this.lat = options.lat;
                    }
                    if (options.lng) {
                        this.lng = options.lng;
                    }
                    if (options.address_form) {
                        if (this.force_override) {
                            this.address_form = options.address_form;
                        } else {
                            this.address_form = Object.assign({}, this.address_form, options.address_form);
                        }
                    }
                    if (options.display_name) {
                        this.display_name = options.display_name;
                    }

                this.target_fields = this.getFillFieldsType();
                const self = await this.initGplacesAutocomplete();
                self._geolocate();
            }
        },
        /**
         * Geolocate
         * @private
         */
        _geolocate: function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    const geolocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };

                    const circle = new google.maps.Circle({
                        center: geolocation,
                        radius: position.coords.accuracy,
                    });

                    this.places_autocomplete.setBounds(circle.getBounds());
                });
            }
        },
        /**
         * @private
         */
        _prepareValue: function (model, field_name, value) {
            model = typeof model !== 'undefined' ? model : false;
            field_name = typeof field_name !== 'undefined' ? field_name : false;
            value = typeof value !== 'undefined' ? value : false;
            return Utils.fetchValues(model, field_name, value);
        },
        /**
         * @private
         */
        _populateAddress: function (place, fillfields, delimiter) {
            place = typeof place !== 'undefined' ? place : false;
            fillfields = typeof fillfields !== 'undefined' ? fillfields : this.fillfields;
            delimiter = typeof delimiter !== 'undefined' ? delimiter : this.fillfields_delimiter;
            return Utils.gmaps_populate_address(place, fillfields, delimiter);
        },
        /**
         * Map google address into Odoo fields
         * @param {*} place
         * @param {*} fillfields
         */
        _populatePlaces: function (place, fillfields) {
            place = typeof place !== 'undefined' ? place : false;
            fillfields = typeof fillfields !== 'undefined' ? fillfields : this.fillfields;
            return Utils.gmaps_populate_places(place, fillfields);
        },
        /**
         * Get country's state
         * @param {*} model
         * @param {*} country
         * @param {*} state
         */
        _getCountryState: function (model, country, state) {
            model = typeof model !== 'undefined' ? model : false;
            country = typeof country !== 'undefined' ? country : false;
            state = typeof state !== 'undefined' ? state : false;
            return Utils.fetchCountryState(model, country, state);
        },
        /**
         * Set country's state
         * @param {*} model
         * @param {*} country
         * @param {*} state
         */
        setCountryState: async function (model, country, state) {
            if (model && country && state) {
                const result = await this._getCountryState(model, country, state);
                const value = { [this.address_form.state_id]: result };
                this._onUpdateWidgetFields(value);
            }
        },
        /**
         * Set geolocation fields
         * @param {*} latitude
         * @param {*} longitude
         */
        _setGeolocation: function (latitude, longitude) {
            const res = {};
            if (_.intersection(_.keys(this.record.fields), [this.lat, this.lng]).length === 2) {
                res[this.lat] = latitude;
                res[this.lng] = longitude;
            }
            return res;
        },
        /**
         * Apply the changes
         * @param {*} values
         */
        _onUpdateWidgetFields(values = {}) {
            this.props.update(values);
        }
        /**
         * Initialize google autocomplete
         * Return promise
         */
        initGplacesAutocomplete: function () {
            return $.when();
        },
        willUnmount() {
            if (this.places_autocomplete) {
                google.maps.event.clearInstanceListeners(this.places_autocomplete);
            }
            // Remove all PAC container in DOM if any
            const pacContainers = document.querySelectorAll('.pac-container');
            pacContainers.forEach(container => container.remove());
        }
        /**
         * List of Google autocomplete data fields, for more detail check on
         * https://developers.google.com/maps/documentation/javascript/places-autocomplete#specify-data-fields
         * @returns Array
         */
        get_google_fields_restriction: function () {
            return [];
        },
    });

    export class GplaceAddressAutocompleteField extends GplaceAutocomplete {
        static template = "web_google_maps.GplaceAddressAutocomplete";
        /**
         * @param {*} values
         */
        _onUpdateWidgetFields(values = {}) {
            if (values.hasOwnProperty(this.lat) || values.hasOwnProperty(this.lng)) {
                const geometry = {
                    [this.lat]: values[this.lat],
                    [this.lng]: values[this.lng],
                };
                // need to delay the call to apply the geolocation fields
                // send these value with address fields won't update the geolocation fields
                setTimeout(() => {
                    this.props.update(geometry);
                }, 500);
                delete values[this.lat];
                delete values[this.lng];
            }
            this.props.update(values);
        }
        /**
         * @override
         */
        setDefault() {
            super.setDefault();
            this.fillfields = {
                [this.address_form.street]: ['street_number', 'route'],
                [this.address_form.street2]: [
                    'administrative_area_level_3',
                    'administrative_area_level_4',
                    'administrative_area_level_5',
                ],
                [this.address_form.city]: ['locality', 'administrative_area_level_2'],
                [this.address_form.zip]: 'postal_code',
                [this.address_form.state_id]: 'administrative_area_level_1',
                [this.address_form.country_id]: 'country',
            };
            // possible value: `address_format` or `no_address_format`
            // address_format: widget will populate address returned by Google to Odoo address fields
            // no_address_format: no populate address, will take address and the geolocation data.
            this.address_mode = 'address_format';
            // Autocomplete request types
            this.autocomplete_types = ['address'];
        },
        /**
         * @override
         */
        async prepareWidgetOptions() {
            const options = this.props.record.fields[this.props.name].options || {};
            if (options.mode) {
                this.address_mode =
                    Utils.ADDRESS_MODE.indexOf(options.mode) != -1
                        ? options.mode
                        : 'address_format';
            }
            if (this.props.readonly === false) {
                if (options.force_override) {
                    this.force_override = true;
                }
                if (options.fillfields) {
                    if (this.force_override) {
                        this.fillfields = options.fillfields;
                    } else {
                        this.fillfields = Object.assign({}, this.fillfields, options.fillfields);
                    }
                }
                if (options.types) {
                    this.autocomplete_types = options.types;
                }
            }
            await super.prepareWidgetOptions();
        }
        /**
         * Get fields attributes
         * @override
         */
        getFillFieldsType() {
            const res = super.getFillFieldsType();

            if (this._isValid && this.address_mode === 'address_format') {
                Object.keys(this.fillfields).forEach((field_name) => {
                    const field = this.props.record.fields[field_name];
                    if (field) {
                        res.push({
                            name: field_name,
                            type: field.type,
                            relation: field.relation,
                        });
                    }
                });
            }
            return res;
        }
        /**
         * Callback function for places_change event
         */
        handlePopulateAddress() {
            const place = this.places_autocomplete.getPlace();
            if (this.address_mode === 'no_address_format') {
                const location_geometry = this._setGeolocation(
                    place.geometry.location.lat(),
                    place.geometry.location.lng()
                );
                if (this.inputRef && this.inputRef.el) {
                    this.inputRef.el.value = place[this.display_name] || place.name;
                }
                this._onUpdateWidgetFields(location_geometry);
            } else if (place.hasOwnProperty('address_components')) {
                const google_address = this._populateAddress(place);
                this.populateAddress(place, google_address);
                if (this.inputRef && this.inputRef.el) {
                    this.inputRef.el.value = place.name;
                }
            }
        },
        /**
         * Populate address form the Google place
         * @param {*} place
         * @param {*} parse_address
         */
        async populateAddress(place, parse_address) {
            const requests = [];
            let index_of_state = _.findIndex(this.target_fields, (f) => f.name === this.address_form.state_id);
            const target_fields = this.target_fields.slice();
            const field_state = index_of_state > -1 ? target_fields.splice(index_of_state, 1)[0] : false;

            target_fields.forEach((field) => {
                requests.push(this._prepareValue(field.relation, field.name, parse_address[field.name]));
            });
            // Set geolocation
            const partner_geometry = this._setGeolocation(place.geometry.location.lat(), place.geometry.location.lng());
            Object.entries(partner_geometry).forEach(([field, val]) => {
                requests.push(this._prepareValue(false, field, val));
            });

            const result = await Promise.all(requests);
            const changes = {};
            result.forEach((vals) => {
                Object.entries(vals).forEach(([key, val]) => {
                    if (typeof val === 'object') {
                        changes[key] = val;
                    } else {
                        changes[key] = this._parseValue(val);
                    }
                });
            });
            this._onUpdateWidgetFields(changes);
            if (this.inputRef && this.inputRef.el) {
                this.inputRef.el.value = parse_address[this.display_name] || place.name;
            }
            if (field_state) {
                const country = changes[this.address_form.country_id]
                    ? changes[this.address_form.country_id]['id']
                    : false;
                const state_code = parse_address[this.address_form.state_id];
                this.setCountryState(field_state.relation, country, state_code);
            }
        },
        /**
         * @override
         * @return {Object}
         */
        get_google_fields_restriction: function () {
            return ['address_components', 'name', 'geometry', 'formatted_address'];
        },
        /**
         * Override
         * Initialiaze places autocomplete
         */
        initGplacesAutocomplete() {
            return new Promise((resolve) => {
                setTimeout(() => {
                    if (!this.places_autocomplete && this.inputRef && this.inputRef.el) {
                        const google_fields = this.get_google_fields_restriction();
                        this.places_autocomplete = new google.maps.places.Autocomplete(this.inputRef.el, {
                            types: this.autocomplete_types,
                            fields: google_fields,
                        });
                        if (this.autocomplete_settings) {
                            this.places_autocomplete.setOptions(this.autocomplete_settings);
                        }
                    }
                    // When the user selects an address from the dropdown, populate the address fields in the form.
                    if (this.places_autocomplete) {
                        this.places_autocomplete.addListener('place_changed', this.handlePopulateAddress.bind(this));
                    }
                    resolve(this);
                }, 300);
            });
        }
        /**
         * @override
         */
        isValid() {
            super.isValid();
            this._isValid = true;
            let unknown_fields;
            if (this.address_mode === 'address_format') {
                let fields = Object.keys(this.fillfields);
                if (this.lat && this.lng) {
                    fields = fields.concat([this.lat, this.lng]);
                }
                unknown_fields = fields.filter((field) => !this.props.record.fields.hasOwnProperty(field));
            } else if (this.address_mode === 'no_address_format' && this.lat && this.lng) {
                unknown_fields = [this.lat, this.lng].filter((field) => !this.props.record.fields.hasOwnProperty(field));
            }
            if (unknown_fields && unknown_fields.length > 0) {
                this.notification.add(
                    _t('The following fields are invalid: <ul><li>' + unknown_fields.join('</li><li>') + '</li></ul>'),
                    { type: 'warning' }
                );
                this._isValid = false;
            }
            return this._isValid;
        }
        willUnmount() {
            if (this.places_autocomplete) {
                google.maps.event.clearInstanceListeners(this.places_autocomplete);
            }
            super.willUnmount();
        }
    });

    export class GplacesAutocompleteField extends GplaceAutocomplete {
        static template = "web_google_maps.GplacesAutocomplete";
        setDefault() {
            super.setDefault();
            this.fillfields = {
                general: {
                    name: 'name',
                    website: 'website',
                    phone: ['international_phone_number', 'formatted_phone_number'],
                },
                address: {
                    street: ['street_number', 'route'],
                    street2: [
                        'administrative_area_level_3',
                        'administrative_area_level_4',
                        'administrative_area_level_5',
                    ],
                    city: ['locality', 'administrative_area_level_2'],
                    zip: 'postal_code',
                    state_id: 'administrative_area_level_1',
                    country_id: 'country',
                },
            };
            this.address_mode = 'address_format';
            // Autocomplete request types
            this.autocomplete_types = ['establishment'];
        },
        async prepareWidgetOptions() {
            const options = this.props.record.fields[this.props.name].options || {};
            if (options.mode) {
                console.warn('Option `mode` are not supported!');
            }
            if (this.props.readonly === false && options) {
                if (options.force_override) {
                    this.force_override = true;
                }
                if (options.fillfields) {
                    if (options.fillfields.address) {
                        if (this.force_override) {
                            this.fillfields['address'] = options.fillfields.address;
                        } else {
                            this.fillfields['address'] = Object.assign(
                                {},
                                this.fillfields.address,
                                options.fillfields.address
                            );
                        }
                    }
                    if (options.fillfields.general) {
                        if (this.force_override) {
                            this.fillfields['general'] = options.fillfields.general;
                        } else {
                            this.fillfields['general'] = Object.assign(
                                {},
                                this.fillfields.general,
                                options.fillfields.general
                            );
                        }
                    }
                    if (options.fillfields.geolocation) {
                        this.fillfields['geolocation'] = options.fillfields.geolocation;
                    }
                }
            }
            await super.prepareWidgetOptions();
        }
        getFillFieldsType() {
            const res = super.getFillFieldsType();
            if (this._isValid && this.address_mode === 'address_format') {
                Object.values(this.fillfields).forEach((option) => {
                    Object.keys(option).forEach((field_name) => {
                        const field = this.props.record.fields[field_name];
                        if (field) {
                            res.push({
                                name: field_name,
                                type: field.type,
                                relation: field.relation,
                            });
                        }
                    });
                });
            }
            return res;
        }
        _onUpdateWidgetFields(values = {}) {
            let geometry = {};
            if (this.lat && this.lng) {
                geometry[this.lat] = values[this.lat];
                geometry[this.lng] = values[this.lng];
            } else if (this.fillfields.geolocation) {
                Object.entries(this.fillfields.geolocation).forEach(([field, alias]) => {
                    if (alias === 'latitude' && values[field]) {
                        geometry[field] = values[field];
                    }
                    if (alias === 'longitude' && values[field]) {
                        geometry[field] = values[field];
                    }
                });
            }
            if (Object.keys(geometry).length > 0) {
                setTimeout(() => {
                    this.props.update(geometry);
                }, 500);
                Object.keys(geometry).forEach((field) => delete values[field]);
            }
            this.props.update(values);
        }
        /**
         *
         * @param {number} lat
         * @param {number} lng
         */
        _setGeolocation(lat, lng) {
            const res = {};
            if (this.lat && this.lng) {
                return super._setGeolocation(lat, lng);
            } else if (this.fillfields.geolocation) {
                Object.entries(this.fillfields.geolocation).forEach(([field, alias]) => {
                    if (alias === 'latitude') {
                        res[field] = lat;
                    }
                    if (alias === 'longitude') {
                        res[field] = lng;
                    }
                });
            }
            return res;
        }
        async handlePopulateAddress() {
            const place = this.places_autocomplete.getPlace();
            if (place.hasOwnProperty('address_components')) {
                const values = {};
                const requests = [];
                const index_of_state = this.target_fields.findIndex((f) => f.name === this.address_form.state_id);
                const target_fields = this.target_fields.slice();
                const field_state = index_of_state > -1 ? target_fields.splice(index_of_state, 1)[0] : false;
                // Get address
                const google_address = this._populateAddress(place, this.fillfields.address, this.fillfields_delimiter);
                Object.assign(values, google_address);
                // Get place (name, website, phone)
                const google_place = this._populatePlaces(place, this.fillfields.general);
                Object.assign(values, google_place);
                // Set place geolocation
                const google_geolocation = this._setGeolocation(
                    place.geometry.location.lat(),
                    place.geometry.location.lng()
                );
                Object.assign(values, google_geolocation);

                target_fields.forEach((field) => {
                    requests.push(this._prepareValue(field.relation, field.name, values[field.name]));
                });

                const result = await Promise.all(requests);
                const changes = {};
                result.forEach((vals) => {
                    Object.entries(vals).forEach(([key, val]) => {
                        if (typeof val === 'object') {
                            changes[key] = val;
                        } else {
                            changes[key] = this._parseValue(val);
                        }
                    });
                });
                this._onUpdateWidgetFields(changes);
                if (field_state) {
                    const country = changes[this.address_form.country_id]
                        ? changes[this.address_form.country_id]['id']
                        : false;
                    const state_code = google_address[this.address_form.state_id];
                    this.setCountryState(field_state.relation, country, state_code);
                }
                if (this.inputRef && this.inputRef.el) {
                    this.inputRef.el.value = changes[this.display_name] || place.name;
                }
            }
        },
        /**
         * @override
         */
        get_google_fields_restriction() {
            return [
                'address_components',
                'name',
                'website',
                'geometry',
                'international_phone_number',
                'formatted_phone_number',
            ];
        }
        initGplacesAutocomplete: function () {
            return new Promise((resolve) => {
                setTimeout(() => {
                    if (!this.places_autocomplete) {
                        const google_fields = this.get_google_fields_restriction();
                        this.places_autocomplete = new google.maps.places.Autocomplete(this.$input.get(0), {
                            types: this.autocomplete_types,
                            fields: google_fields,
                        });
                        if (this.autocomplete_settings) {
                            this.places_autocomplete.setOptions(this.autocomplete_settings);
                        }
                    }
                    // When the user selects an address from the dropdown, populate the address fields in the form.
                    this.places_autocomplete.addListener('place_changed', this.handlePopulateAddress.bind(this));
                    resolve(this);
                }, 300);
            });
        },
        /**
         * @override
         */
        isValid() {
            super.isValid();
            let unknown_fields = null;
            const invalid_fields = [];
            for (let option in this.fillfields) {
                unknown_fields = Object.keys(this.fillfields[option]).filter(
                    (field) => !this.props.record.fields.hasOwnProperty(field)
                );
                if (unknown_fields.length > 0) {
                    this.notification.add(
                        _t('The following fields are invalid: <ul><li>' +
                            unknown_fields.join('</li><li>') +
                            '</li></ul>'),
                        { type: 'warning' }
                    );
                    invalid_fields.push(unknown_fields);
                }
            }
            this._isValid = !(invalid_fields.length > 0);
            return this._isValid;
        }
        willUnmount() {
            if (this.places_autocomplete) {
                google.maps.event.clearInstanceListeners(this.places_autocomplete);
            }
            super.willUnmount();
        }
    });

    // Register the field components
    registry.category("fields").add("gplace_address_autocomplete", GplaceAddressAutocompleteField);
    registry.category("fields").add("gplaces_autocomplete", GplacesAutocompleteField);
