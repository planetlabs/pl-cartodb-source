var http = require('http');
var url = require('url');
var ol = require('openlayers');
var debounce = require('lodash/function/debounce');

var templateCache = {};

/**
 * CartoDB detail.  We are using CartoDB to render scene footprints at low zoom
 * levels.  This starts with a "visualization" in the Planet account named
 * "Planet Scenes Ortho":
 *
 *     https://planet.cartodb.com/viz/f78f58aa-5e04-11e4-8a77-0e4fddd5de28/map
 *
 * The layer we are interested in is just the footprints layer (we don't need
 * anything else from the visualization).  To get the layer identifier (this is
 * "layergroupid" in CartoDB terms), we have to instantiate a new map.  The
 * map identifier comes in the visualization layer list:
 *
 *     http://planet.cartodb.com/api/v2/viz/
 *         f78f58aa-5e04-11e4-8a77-0e4fddd5de28/viz.json
 *
 * The layers[1].options.named_map.name is what we want from that:
 *
 *     tpl_f78f58aa_5e04_11e4_8a77_0e4fddd5de28
 *
 * To get the identifier we need to access tiles, we have to "instantiate" a
 * new map by POSTing an empty JSON object to the maps API:
 *
 *     curl -X POST -H 'Content-Type: application/json' -d '{}' \
 *       https://planet.cartodb.com/api/v1/map/named/
 *       tpl_f78f58aa_5e04_11e4_8a77_0e4fddd5de28
 *
 */

/**
 * TODO: Move this to ol.source.CartoDB
 */
function CartoDBSource(options) {
  this.userId_ = options.user;
  this.mapId_ = options.map;
  this.params_ = options.params || {};
  delete options.user;
  delete options.map;
  ol.source.XYZ.call(this, options);
  this.initializeMap_();
}

ol.inherits(CartoDBSource, ol.source.XYZ);

CartoDBSource.prototype.getParams = function() {
  return this.params_;
};

CartoDBSource.prototype.updateParams = function(params) {
  for (var key in params) {
    this.params_[key] = params[key];
  }
  this.initializeMap_();
};

CartoDBSource.prototype.setParams = function(params) {
  this.params_ = params || {};
  this.initializeMap_();
};

/**
 * Issue a request to initialize the CartoDB map.
 */
CartoDBSource.prototype.initializeMap_ = debounce(function() {
  var paramHash = JSON.stringify(this.params_);
  if (templateCache[paramHash]) {
    this.applyParams_(templateCache[paramHash]);
    return;
  }
  var protocol = window.location.protocol;
  var mapUrl = protocol + '//' + this.userId_ +
      '.cartodb.com/api/v1/map/named/' + this.mapId_;

  var config = url.parse(mapUrl);
  config.method = 'POST';
  config.withCredentials = false;

  var req = http.request(config, this.handleInitResponse_.bind(this, paramHash));
  req.setHeader('Content-Type', 'application/json');
  req.write(JSON.stringify(this.params_) + '\n');
  req.end();
}, 50);

/**
 * Handle map initialization response.
 * @param {http.IncomingMessage} res Server response.
 */
CartoDBSource.prototype.handleInitResponse_ = function(paramHash, res) {
  var body = '';
  res.on('data', function(chunk) {
    body += String(chunk);
  });
  res.on('end', function() {
    var data = JSON.parse(body);
    this.applyParams_(data);
    templateCache[paramHash] = data;
  }.bind(this));
};

CartoDBSource.prototype.applyParams_ = function(data) {
  var layerId = data.layergroupid;
  // TODO: use protocol when CartoDB cdn_url.https is fixed
  // jscs:disable
  var tilesUrl = 'https://' + data.cdn_url.https + '/' + this.userId_ +
      '/api/v1/map/' + layerId + '/{z}/{x}/{y}.png';
  // jscs:enable
  this.setUrl(tilesUrl);
};

module.exports = CartoDBSource;
