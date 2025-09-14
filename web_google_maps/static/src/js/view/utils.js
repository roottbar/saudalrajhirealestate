/** @odoo-module **/

/**
 * Parse marker colors from a string format to an object
 * @param {string} colorsStr - Color string in format "color1:condition1;color2:condition2"
 * @returns {Object} Object with color mappings
 */
export function parseMarkersColor(colorsStr) {
    if (!colorsStr) {
        return {};
    }
    
    const colors = {};
    const colorPairs = colorsStr.split(';');
    
    colorPairs.forEach(pair => {
        if (pair.trim()) {
            const [color, condition] = pair.split(':');
            if (color && condition) {
                colors[condition.trim()] = color.trim();
            }
        }
    });
    
    return colors;
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