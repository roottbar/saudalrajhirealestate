/** @odoo-module **/

import { registry } from "@web/core/registry";
import { GplacesAddressAutocompleteField, GplacesAutocompleteField } from "./gplaces_autocomplete";

const fieldRegistry = registry.category("fields");

fieldRegistry.add('gplaces_address_autocomplete', GplacesAddressAutocompleteField);
fieldRegistry.add('gplaces_autocomplete', GplacesAutocompleteField);
