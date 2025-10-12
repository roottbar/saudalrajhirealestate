/** @odoo-module */
// Ensure the client action module is loaded at startup so its registration
// in the actions registry happens before any menu triggers it.
odoo.define('ks_dashboard_ninja.boot', function(require){
    require('ks_dashboard_ninja.ks_dashboard');
});