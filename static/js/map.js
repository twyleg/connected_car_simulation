const styles = {
  'Point': new ol.style.Style({
    image: new ol.style.Circle({
      fill: new ol.style.Fill({ color: 'rgba(255,255,0,0.4)' }),
      radius: 5,
      stroke: new ol.style.Stroke({ color: '#ff0', width: 1 }),
    }),
  }),
  'LineString': new ol.style.Style({
    stroke: new ol.style.Stroke({ color: '#4dd0a8', width: 4 }),
  }),
  'MultiLineString': new ol.style.Style({
    stroke: new ol.style.Stroke({ color: [99, 179, 255, 0.9], width: 6 }),
  }),
  'geoMarker': new ol.style.Style({
    image: new ol.style.Circle({
      radius: 8,
      fill: new ol.style.Fill({ color: '#08111f' }),
      stroke: new ol.style.Stroke({ color: '#ecf3ff', width: 3 }),
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

const apiBaseUrl = `${window.location.protocol}//${window.location.host}`;
const websocketProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const websocketUrl = `${websocketProtocol}://${window.location.hostname}:8081`;

function formatNumber(value, digits = 1) {
  return Number(value || 0).toFixed(digits);
}

function metersToDisplay(value) {
  return `${Math.round(value || 0)} m`;
}

function kmhFromMetersPerSecond(value) {
  return Number(value || 0) * 3.6;
}

class TrafficLight {

  constructor(id, lon, lat) {
    this.id = id;
    this.lon = lon;
    this.lat = lat;
    this.state = 'red';

    this.feature = new ol.Feature({
      type: 'traffic_light_red',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([this.lon, this.lat])),
    });

    this.popupOverlay = this.createPopupOverlay();
    this.popupOverlay.setPosition(this.feature.getGeometry().getCoordinates());
  }

  createPopupOverlay() {
    const popupElem = document.createElement('div');
    popupElem.title = `Traffic Light [${this.id}]`;
    $('body').append(popupElem);

    $(popupElem).popover({
      container: popupElem,
      placement: 'top',
      animation: false,
      html: true,
      content: '',
    });

    return new ol.Overlay({
      element: popupElem
    });
  }

  openPopup() {
    $(this.popupOverlay.getElement()).popover('show');
  }

  isPopupOpen() {
    return $(this.popupOverlay.getElement()).find('.popover-body').length === 1;
  }

  setPopupContent(content) {
    $(this.popupOverlay.getElement()).attr('data-content', content);
    if (this.isPopupOpen()) {
      this.openPopup();
    }
  }

  update(trafficLightState) {
    if (trafficLightState.state === 'red') {
      this.feature.setStyle(styles['traffic_light_red']);
    } else if (trafficLightState.state === 'yellow') {
      this.feature.setStyle(styles['traffic_light_yellow']);
    } else {
      this.feature.setStyle(styles['traffic_light_green']);
    }

    this.setPopupContent(
      `state: ${trafficLightState.state}` +
      `<br>period: ${trafficLightState.period}` +
      `<br>ratio: ${trafficLightState.ratio}` +
      `<br>time: ${trafficLightState.t.toFixed(3)}`
    );
  }
}

class ControlMenu {

  constructor() {
    this.vehiclePositionSlider = document.getElementById('position_slider');
    this.targetVelocitySlider = document.getElementById('target_velocity_slider');
    this.accelerationSlider = document.getElementById('acceleration_slider');
    this.vehicleInformationField = document.getElementById('vehicle_information');
    this.positionValueField = document.getElementById('position_value');
    this.routeLengthField = document.getElementById('route_length');
    this.currentSpeedField = document.getElementById('vehicle_speed');
    this.targetSpeedField = document.getElementById('target_speed');
    this.accelerationValueField = document.getElementById('acceleration_value');
    this.trafficLightCountField = document.getElementById('traffic_light_count');
    this.vehicleLatitudeField = document.getElementById('vehicle_latitude');
    this.vehicleLongitudeField = document.getElementById('vehicle_longitude');
    this.targetVelocityValueField = document.getElementById('target_velocity_value');
    this.accelerationSliderValueField = document.getElementById('acceleration_slider_value');

    this.vehiclePositionSlider.oninput = (() => {
      this.positionValueField.textContent = metersToDisplay(this.vehiclePositionSlider.value);
      $.get(`${apiBaseUrl}/api/set_vehicle_position`, { position: this.vehiclePositionSlider.value });
    });

    this.targetVelocitySlider.oninput = (() => {
      this.targetVelocityValueField.textContent = `${this.targetVelocitySlider.value} km/h`;
      this.pushVehicleOutput();
    });

    this.accelerationSlider.oninput = (() => {
      this.accelerationSliderValueField.textContent = `${formatNumber(this.accelerationSlider.value)} m/s²`;
      this.pushVehicleOutput();
    });

    $.get(`${apiBaseUrl}/api/get_route_information`, (data) => {
      this.vehiclePositionSlider.max = parseInt(data.length, 10);
      this.routeLengthField.textContent = metersToDisplay(data.length);
    });
  }

  pushVehicleOutput() {
    $.get(`${apiBaseUrl}/api/set_vehicle_output`, {
      acceleration: this.accelerationSlider.value,
      target_velocity: this.targetVelocitySlider.value
    });
  }

  updateVehicleInformation(vehicleInformation) {
    const currentVelocityInKmh = kmhFromMetersPerSecond(vehicleInformation.current_velocity);
    const targetVelocityInKmh = kmhFromMetersPerSecond(vehicleInformation.target_velocity);
    const coordinates = vehicleInformation.position_coordinates;

    this.vehicleInformationField.textContent = JSON.stringify(vehicleInformation, null, 2);
    this.vehiclePositionSlider.value = vehicleInformation.position_on_route;
    this.positionValueField.textContent = metersToDisplay(vehicleInformation.position_on_route);
    this.currentSpeedField.textContent = formatNumber(currentVelocityInKmh);
    this.targetSpeedField.textContent = formatNumber(targetVelocityInKmh);
    this.accelerationValueField.textContent = formatNumber(vehicleInformation.max_acceleration);
    this.vehicleLatitudeField.textContent = formatNumber(coordinates.lat, 6);
    this.vehicleLongitudeField.textContent = formatNumber(coordinates.lon, 6);

    if (document.activeElement !== this.targetVelocitySlider) {
      this.targetVelocitySlider.value = Math.round(targetVelocityInKmh);
      this.targetVelocityValueField.textContent = `${Math.round(targetVelocityInKmh)} km/h`;
    }

    if (document.activeElement !== this.accelerationSlider) {
      this.accelerationSlider.value = formatNumber(vehicleInformation.max_acceleration);
      this.accelerationSliderValueField.textContent = `${formatNumber(vehicleInformation.max_acceleration)} m/s²`;
    }
  }

  handleSimulationStateUpdate(simulationState) {
    this.updateVehicleInformation(simulationState.vehicle_state);
    this.trafficLightCountField.textContent = simulationState.traffic_lights_state.length;
  }
}

class UI {

  constructor() {
    this.trafficLightsByIdMap = new Map();
    this.controlMenu = new ControlMenu();
    this.followVehicle = false;
    this.latestVehicleCoordinate = null;
    this.centerVehicleButton = document.getElementById('center_vehicle_button');
    this.followVehicleButton = document.getElementById('follow_vehicle_button');

    this.routeLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        url: 'routes/ostfalia-wf-wob.gpx',
        format: new ol.format.GPX(),
      }),
      style: (feature) => styles[feature.getGeometry().getType()],
    });

    this.vehicleMarker = new ol.Feature({
      type: 'geoMarker',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([10.547558, 52.176758])),
    });

    this.vehicleMarkerLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        features: [this.vehicleMarker]
      }),
      style: (feature) => styles[feature.get('type')],
    });

    this.trafficLightLayer = new ol.layer.Vector({
      source: new ol.source.Vector({}),
      style: (feature) => styles[feature.get('type')],
    });

    this.osmLayer = new ol.layer.Tile({
      source: new ol.source.OSM()
    });

    this.map = new ol.Map({
      layers: [this.osmLayer, this.routeLayer, this.vehicleMarkerLayer, this.trafficLightLayer],
      view: new ol.View({
        center: ol.proj.fromLonLat([10.547558, 52.176758]),
        zoom: 15
      }),
      target: 'map'
    });

    this.centerVehicleButton.addEventListener('click', () => {
      this.centerOnVehicle();
    });

    this.followVehicleButton.addEventListener('click', () => {
      this.followVehicle = !this.followVehicle;
      this.updateFollowVehicleButton();
      if (this.followVehicle) {
        this.centerOnVehicle();
      }
    });

    this.updateFollowVehicleButton();

    this.map.on('click', (evt) => {
      let trafficLightFeature;

      this.map.forEachFeatureAtPixel(evt.pixel, (feature) => {
        trafficLightFeature = feature;
      });

      for (const trafficLight of this.trafficLightsByIdMap.values()) {
        if (trafficLightFeature === trafficLight.feature) {
          trafficLight.openPopup();
        }
      }
    });
  }

  setVehiclePosition(lon, lat) {
    this.vehicleMarker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
  }

  centerOnVehicle(animate = true) {
    if (this.latestVehicleCoordinate === null) {
      return;
    }

    const view = this.map.getView();
    view.cancelAnimations();

    if (animate) {
      view.animate({
        center: this.latestVehicleCoordinate,
        duration: 250
      });
      return;
    }

    view.setCenter(this.latestVehicleCoordinate);
  }

  updateFollowVehicleButton() {
    this.followVehicleButton.textContent = this.followVehicle ? 'Follow vehicle: On' : 'Follow vehicle: Off';
    this.followVehicleButton.classList.toggle('active', this.followVehicle);
  }

  findOrCreateTrafficLight(trafficLightState) {
    const id = trafficLightState.id;
    let trafficLight = this.trafficLightsByIdMap.get(id);

    if (trafficLight === undefined) {
      trafficLight = new TrafficLight(id, trafficLightState.lon, trafficLightState.lat);
      this.trafficLightsByIdMap.set(id, trafficLight);
      this.trafficLightLayer.getSource().addFeature(trafficLight.feature);
      this.map.addOverlay(trafficLight.popupOverlay);
    }

    return trafficLight;
  }

  handleSimulationStateUpdate(simulationState) {
    this.controlMenu.handleSimulationStateUpdate(simulationState);

    const vehicleLon = simulationState.vehicle_state.position_coordinates.lon;
    const vehicleLat = simulationState.vehicle_state.position_coordinates.lat;
    this.latestVehicleCoordinate = ol.proj.fromLonLat([vehicleLon, vehicleLat]);
    this.setVehiclePosition(vehicleLon, vehicleLat);

    if (this.followVehicle) {
      this.centerOnVehicle(false);
    }

    for (let i = 0; i < simulationState.traffic_lights_state.length; i += 1) {
      const trafficLightState = simulationState.traffic_lights_state[i];
      const trafficLight = this.findOrCreateTrafficLight(trafficLightState);
      trafficLight.update(trafficLightState);
    }
  }
}

class WebSocketConnection {

  constructor(ui) {
    this.ui = ui;
    this.statusElement = document.getElementById('connection_status');
    this.socket = new WebSocket(websocketUrl);

    this.socket.addEventListener('open', () => {
      this.statusElement.textContent = 'Socket online';
      this.statusElement.classList.remove('offline');
      this.statusElement.classList.add('online');
    });

    this.socket.addEventListener('close', () => {
      this.statusElement.textContent = 'Socket offline';
      this.statusElement.classList.remove('online');
      this.statusElement.classList.add('offline');
    });

    this.socket.addEventListener('error', () => {
      this.statusElement.textContent = 'Socket error';
      this.statusElement.classList.remove('online');
      this.statusElement.classList.add('offline');
    });

    this.socket.addEventListener('message', (event) => {
      const simulationState = JSON.parse(event.data).simulation_state;
      this.ui.handleSimulationStateUpdate(simulationState);
    });
  }
}

const ui = new UI();
const websocketConnection = new WebSocketConnection(ui);
