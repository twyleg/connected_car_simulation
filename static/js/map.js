const styles = {
  'Point': new ol.style.Style({
    image: new ol.style.Circle({
      fill: new ol.style.Fill({ color: 'rgba(255,255,0,0.4)' }),
      radius: 5,
      stroke: new ol.style.Stroke({ color: '#ff0', width: 1 }),
    }),
  }),
  'LineString': new ol.style.Style({
    stroke: new ol.style.Stroke({ color: 'blue', width: 3 }),
  }),
  'MultiLineString': new ol.style.Style({
    stroke: new ol.style.Stroke({ color: [255, 0, 0, 0.8], width: 6 }),
  }),
  'geoMarker': new ol.style.Style({
    image: new ol.style.Circle({
      radius: 7,
      fill: new ol.style.Fill({ color: 'black' }),
      stroke: new ol.style.Stroke({ color: 'white', width: 2 }),
    }),
  }),
  'traffic_light_red': new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_red.png',
      scale: 0.1,
    }),
  }),
  'traffic_light_yellow': new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_yellow.png',
      scale: 0.1,
    }),
  }),
  'traffic_light_green': new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_green.png',
      scale: 0.1,
    }),
  }),
};



class TrafficLight {

  constructor(id, lon, lat) {

    this.id = id
    this.lon = lon
    this.lat = lat
    this.state = "red"

    this.feature = new ol.Feature({
      type: 'traffic_light_red',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([this.lon, this.lat])),
    });

    this.popupOverlay = this.createPopupOverlay()
    this.popupOverlay.setPosition(this.feature.getGeometry().getCoordinates());
  }
  
  createPopupOverlay() {

    var popupElem = document.createElement("div");
    popupElem.title = 'Traffic Light [' + this.id + '] <button id="popovercloseid" type="button" class="close">&times;</button>'
    $("body").append(popupElem);
    
    $(popupElem).popover({
      container: popupElem,
      placement: 'top',
      animation: false,
      html: true,
      content: '',
    });

    var popupOverlay = new ol.Overlay({
      element: popupElem
    });
    
    return popupOverlay
  }

  openPopup() {
    $(this.popupOverlay.getElement()).popover('show');
  }

  closePopup() {
    $(this.popupOverlay.getElement()).popover('hide');
  }

  isPopupOpen() {
    return $(this.popupOverlay.getElement()).find(".popover-body").length == 1
  }

  setPopupContent(content) {
    $(this.popupOverlay.getElement()).attr('data-content', content)
    if(this.isPopupOpen()) {
      this.openPopup()
    }
  } 

  update(trafficLightState) {
    if (trafficLightState.state === "red") {
      this.feature.setStyle(styles['traffic_light_red'])
    } else if (trafficLightState.state === "yellow") {
      this.feature.setStyle(styles['traffic_light_yellow'])
    } else {
      this.feature.setStyle(styles['traffic_light_green'])
    }

    this.setPopupContent('state: ' + trafficLightState.state +
                        '<br>period: ' + trafficLightState.period +
                        '<br>ratio: ' + trafficLightState.ratio +
                        '<br>time: ' + trafficLightState.t.toFixed(3))
  }
}


class ControlMenu {

  constructor() {

    this.vehiclePositionSlider = document.getElementById("position_slider")
    this.vehicleInformationField = document.getElementById("vehicle_information")

    this.vehiclePositionSlider.oninput = function() {
      $.get("http://localhost:8080/api/set_vehicle_position", { position: this.value})
    } 

    $.get("http://localhost:8080/api/get_route_information", (function(data) {
      this.vehiclePositionSlider.max = parseInt(data.length)
      console.log(data.length)
    }).bind(this))

  }

  updateVehicleInformation(vehicleInformation) {
    this.vehicleInformationField.innerHTML = "Vehicle state: " + JSON.stringify(vehicleInformation, null, 5)
    this.vehiclePositionSlider.value = vehicleInformation.position_on_route
  }

  handleSimulationStateUpdate(simulationState) {
    this.updateVehicleInformation(simulationState.vehicle_state)
  }

}


class UI {

  constructor() {

    this.trafficLightsByIdMap = new Map()
    this.controlMenu = new ControlMenu()

    this.routeLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        url: 'routes/ostfalia-wf-wob.gpx',
        format: new ol.format.GPX(),
      }),
      style: (function (feature) {
        return styles[feature.getGeometry().getType()];
      }).bind(this),
    });

    this.vehicleMarker = new ol.Feature({
      type: 'geoMarker',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([10.547558, 52.176758])),
    });

    this.vehicleMarkerLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        features: [this.vehicleMarker]
      }),
      style: (function (feature) {
        return styles[feature.get('type')];
      }).bind(this),
    });

    this.trafficLightLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
      }),
      style: (function (feature) {
        return styles[feature.get('type')];
      }).bind(this),
    });

    this.osmLayer = new ol.layer.Tile({
      source: new ol.source.OSM()
    })

    this.map = new ol.Map({
      layers: [this.osmLayer, this.routeLayer, this.vehicleMarkerLayer, this.trafficLightLayer],
      view: new ol.View({
        center: ol.proj.fromLonLat([10.547558, 52.176758]),
        zoom: 15
      }),
      target: 'map'
    });

    this.map.on('click', (function (evt) {

      var trafficLightFeature = undefined

      this.map.forEachFeatureAtPixel(evt.pixel, (function (feature) {
        trafficLightFeature = feature
      }).bind(this))
      
      for (const [id, trafficLight] of this.trafficLightsByIdMap.entries()) {
        if(trafficLightFeature === trafficLight.feature){
          trafficLight.openPopup()
        }
      }
    }).bind(this));
  }

  setVehiclePosition(lon, lat) {
    this.vehicleMarker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])))
  }

  findOrCreateTrafficLight(trafficLightState) {
    var id = trafficLightState.id
    var trafficLight = this.trafficLightsByIdMap.get(id)

    if (trafficLight === undefined) {
      var trafficLight = new TrafficLight(id, trafficLightState.lon, trafficLightState.lat)
      this.trafficLightsByIdMap.set(id, trafficLight)
      this.trafficLightLayer.getSource().addFeature(trafficLight.feature)
      this.map.addOverlay(trafficLight.popupOverlay)
    }
    return trafficLight
  }

  handleSimulationStateUpdate(simulationState) {

    this.controlMenu.handleSimulationStateUpdate(simulationState)

    var vehicle_lon = simulationState.vehicle_state.position_coordinates.lon
    var vehicle_lat = simulationState.vehicle_state.position_coordinates.lat
    this.setVehiclePosition(vehicle_lon, vehicle_lat);

    for (let i=0; i<simulationState.traffic_lights_state.length; i++) {
      var trafficLightState = simulationState.traffic_lights_state[i]

      var trafficLight = this.findOrCreateTrafficLight(trafficLightState)
      trafficLight.update(trafficLightState)
    }
  }
}

class WebSocketConnection {

  constructor(ui) {

    this.ui = ui
    this.socket = new WebSocket('ws://localhost:8081');

    this.socket.addEventListener('open', function (event) {
      // socket.send('Connection Established');
    });

    this.socket.addEventListener('message', (function (event) {
      const simulationState = JSON.parse(event.data).simulation_state;
      this.ui.handleSimulationStateUpdate(simulationState)
    }).bind(this));
  }
}

var ui = new UI();
var websocketConnection = new WebSocketConnection(ui);

