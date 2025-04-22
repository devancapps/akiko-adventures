const travelLinks = require('../config/travel-links.json');

/**
 * Generate a widget URL based on configuration
 * @param {string} widgetType - Type of widget (e.g., 'flight_search', 'hotel_search')
 * @param {Object} params - Additional parameters to override defaults
 * @param {boolean} useFallback - Whether to use fallback provider
 * @returns {string} Generated widget URL
 */
function generateWidgetUrl(widgetType, params = {}, useFallback = false) {
  const widget = travelLinks.widgets[widgetType];
  const config = useFallback ? widget.fallback : widget.primary;
  
  if (!config) {
    throw new Error(`No ${useFallback ? 'fallback' : 'primary'} configuration found for widget type: ${widgetType}`);
  }

  const allParams = {
    ...config.default_params,
    ...params
  };

  const queryString = Object.entries(allParams)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');

  return `${config.base_url}?${queryString}`;
}

/**
 * Get destination-specific affiliate link
 * @param {string} destination - Destination key (e.g., 'tokyo', 'london')
 * @param {string} linkType - Type of link (e.g., 'hotels', 'flights')
 * @param {boolean} useFallback - Whether to use fallback provider
 * @returns {Object} Link configuration object
 */
function getDestinationLink(destination, linkType, useFallback = false) {
  const destConfig = travelLinks.destinations[destination.toLowerCase()];
  if (!destConfig) {
    throw new Error(`No configuration found for destination: ${destination}`);
  }

  const links = destConfig.links[linkType];
  if (!links) {
    throw new Error(`No ${linkType} links found for destination: ${destination}`);
  }

  return useFallback ? links.fallback : links.primary;
}

/**
 * Generate a widget for a specific destination
 * @param {string} destination - Destination key
 * @param {string} widgetType - Type of widget
 * @param {Object} additionalParams - Additional parameters
 * @returns {string} HTML widget code
 */
function generateDestinationWidget(destination, widgetType, additionalParams = {}) {
  const destConfig = travelLinks.destinations[destination.toLowerCase()];
  if (!destConfig) {
    throw new Error(`No configuration found for destination: ${destination}`);
  }

  const linkConfig = destConfig.links[widgetType === 'flight_search' ? 'flights' : 'hotels'];
  const params = {
    ...linkConfig.primary.params,
    ...additionalParams
  };

  try {
    const widgetUrl = generateWidgetUrl(widgetType, params);
    return `<iframe src="${widgetUrl}" width="100%" height="300" frameborder="0"></iframe>`;
  } catch (error) {
    console.error(`Error generating widget: ${error.message}`);
    // Return fallback HTML if primary fails
    const fallbackLink = getDestinationLink(destination, widgetType === 'flight_search' ? 'flights' : 'hotels', true);
    return `<a href="${fallbackLink.url}" target="_blank" class="fallback-link">${fallbackLink.text}</a>`;
  }
}

/**
 * Generate newsletter content with affiliate links
 * @param {string} destination - Destination key
 * @returns {Object} Newsletter content with affiliate links
 */
function generateNewsletterContent(destination) {
  const destConfig = travelLinks.destinations[destination.toLowerCase()];
  if (!destConfig) {
    throw new Error(`No configuration found for destination: ${destination}`);
  }

  const hotelLink = getDestinationLink(destination, 'hotels');
  const flightLink = getDestinationLink(destination, 'flights');

  return {
    destination: destConfig.name,
    country: destConfig.country,
    hotelLink: hotelLink.url,
    hotelText: hotelLink.text,
    flightLink: flightLink.url,
    flightText: flightLink.text
  };
}

module.exports = {
  generateWidgetUrl,
  getDestinationLink,
  generateDestinationWidget,
  generateNewsletterContent
}; 