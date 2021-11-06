class Map {

    constructor() {
      this.style = {
          'Point': new ol.style.Style({
            image: new ol.style.Circle({
              fill: new ol.style.Fill({color: 'rgba(255,255,0,0.4)'}),
              radius: 5,
              stroke: new ol.style.Stroke({color: '#ff0', width: 1}),
            }),
          }),
          'LineString': new ol.style.Style({
            stroke: new ol.style.Stroke({color: 'blue', width: 3}),
          }),
          'MultiLineString': new ol.style.Style({
            stroke: new ol.style.Stroke({color: 'red', width: 3}),
          }),
          'geoMarker': new ol.style.Style({
            image: new ol.style.Circle({
              radius: 7,
              fill: new ol.style.Fill({color: 'black'}),
              stroke: new ol.style.Stroke({color: 'white', width: 2}),
            }),
          }),
        };

        this.geoMarker = new ol.Feature({
          type: 'geoMarker',
          geometry: new ol.geom.Point(ol.proj.fromLonLat([10.547558, 52.176758])),
        });

        this.markerLayer = new ol.layer.Vector({
          source: new ol.source.Vector({
            features: [this.geoMarker]
          }),
          style: (function (feature) {
            return this.style[feature.get('type')];
          }).bind(this),
        });

        this.routeLayer = new ol.layer.Vector({
          source: new ol.source.Vector({
            url: 'ostfalia-wf-wob.gpx',
            format: new ol.format.GPX(),
          }),
          style: (function (feature) {
            return this.style[feature.getGeometry().getType()];
          }).bind(this),
        });

        this.mapLayer = new ol.layer.Tile({
            source: new ol.source.OSM()
        })

        this.map = new ol.Map({
          layers: [this.mapLayer, this.routeLayer, this.markerLayer],
          view: new ol.View({
            center: ol.proj.fromLonLat([10.547558, 52.176758]),
            zoom: 15
          }),
          target: 'map'
        });
    }

    setPosition(lon, lat) {
        this.geoMarker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])))
    }
}

class WebSocketConnection {

    constructor(map) {

        this.map = map
        this.socket = new WebSocket('ws://localhost:8081');

        this.socket.addEventListener('open', function (event) {
            socket.send('Connection Established');
        });

        this.socket.addEventListener('message', (function (event) {
            const pt = JSON.parse(event.data);
            this.map.setPosition(pt.lon, pt.lat);
        }).bind(this));

    }

}

var map = new Map();
var websocketConnection = new WebSocketConnection(map);
