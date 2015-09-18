# CartoDB Source for OpenLayers

This is an OpenLayers interface to CartoDB

## Usage

```js
var ol = require('openlayers');
var CartoDBSource = require('pl-cartodb-source');

var cartoDBLayer = new ol.layer.Tile({
  title: 'Coverage',
  visible: true,
  source: new CartoDBSource({
    user: 'planet',
    map: 'scene_coverage_v2'
  })
});

var map = new ol.Map({
  layers: cartoDBLayer
});
```
