/** @odoo-module **/

const MARKER_ICON_SVG_PATH =
    'M172.268 501.67C26.97 291.031 0 269.413 0 192 0 85.961 85.961 0 192 0s192 85.961 192 192c0 77.413-26.97 99.031-172.268 309.67-9.535 13.774-29.93 13.773-39.464 0zM192 272c44.183 0 80-35.817 80-80s-35.817-80-80-80-80 35.817-80 80 35.817 80 80 80z';
const MARKER_ICON_WIDTH = 384;
const MARKER_ICON_HEIGHT = 512;

const MAP_THEMES = {
    default: [],
    aubergine: [
        {
            elementType: 'geometry',
            stylers: [{ color: '#1d2c4d' }],
        },
        {
            elementType: 'labels.text.fill',
            stylers: [{ color: '#8ec3b9' }],
        },
        {
            elementType: 'labels.text.stroke',
            stylers: [{ color: '#1a3646' }],
        },
        {
            featureType: 'administrative.country',
            elementType: 'geometry.stroke',
            stylers: [{ color: '#4b6878' }],
        },
        {
            featureType: 'road',
            elementType: 'geometry',
            stylers: [{ color: '#304a7d' }],
        },
        {
            featureType: 'water',
            elementType: 'geometry',
            stylers: [{ color: '#0e1626' }],
        },
    ],
};

/**
 * Parse marker colors from a string format to an array
 * @param {string} colorsStr - Color string in format "color1:condition1;color2:condition2"
 * @returns {Array} Array with color mappings [color, expression, expr]
 */
export function parseMarkersColor(colorsStr) {
    if (!colorsStr) {
        return false;
    }
    
    return colorsStr.split(';')
        .filter(Boolean)
        .map(function (colorPair) {
            const [color, expr] = colorPair.split(':');
            return [color?.trim(), expr?.trim(), expr?.trim()];
        });
}

/**
 * Get default marker color
 * @param {string} defaultColor - Default color to use
 * @returns {string} Color value
 */
export function getDefaultMarkerColor(defaultColor = 'red') {
    return defaultColor;
}

/**
 * Validate latitude value
 * @param {number} lat - Latitude value
 * @returns {boolean} True if valid
 */
export function isValidLatitude(lat) {
    return typeof lat === 'number' && lat >= -90 && lat <= 90;
}

/**
 * Validate longitude value
 * @param {number} lng - Longitude value
 * @returns {boolean} True if valid
 */
export function isValidLongitude(lng) {
    return typeof lng === 'number' && lng >= -180 && lng <= 180;
}

/**
 * Google Map utilities object
 */
export const GoogleMapUtils = {
    MAP_THEMES,
    MARKER_ICON_SVG_PATH,
    MARKER_ICON_WIDTH,
    MARKER_ICON_HEIGHT,
};
