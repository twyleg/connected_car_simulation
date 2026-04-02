import { formatNumber, kmhFromMetersPerSecond, metersToDisplay } from './utils.js';

const baseStyles = {
  Point: new ol.style.Style({
    image: new ol.style.Circle({
      fill: new ol.style.Fill({ color: 'rgba(255,255,0,0.4)' }),
      radius: 5,
      stroke: new ol.style.Stroke({ color: '#ff0', width: 1 }),
    }),
  }),
  LineString: new ol.style.Style({
    stroke: new ol.style.Stroke({ color: '#4dd0a8', width: 4 }),
  }),
  MultiLineString: new ol.style.Style({
    stroke: new ol.style.Stroke({ color: [99, 179, 255, 0.9], width: 6 }),
  }),
  geoMarker: new ol.style.Style({
    image: new ol.style.Circle({
      radius: 8,
      fill: new ol.style.Fill({ color: '#08111f' }),
      stroke: new ol.style.Stroke({ color: '#ecf3ff', width: 3 }),
    }),
  }),
};

const apiBaseUrl = `${window.location.protocol}//${window.location.host}`;
const websocketProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const websocketUrl = `${websocketProtocol}://${window.location.hostname}:8081`;
function toTemplateValue(value) {
  if (typeof value === 'number') {
    return Number.isInteger(value) ? `${value}` : formatNumber(value, 2);
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (value === null || value === undefined) {
    return '';
  }
  return `${value}`;
}

const pluginHelpers = {
  formatNumber,
  kmhFromMetersPerSecond,
  metersToDisplay,
  ol,
};

function createTemplateData(modelState, extraTemplateData = {}) {
  return {
    ...modelState.state,
    display_name: modelState.display_name,
    model_id: modelState.model_id,
    model_type: modelState.model_type,
    ...extraTemplateData,
  };
}

function renderTemplate(template, templateData) {
  if (!template) {
    return '';
  }

  return template.replace(/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g, (_, key) => toTemplateValue(templateData[key]));
}

class ModelUiResourceManager {

  constructor() {
    this.styleElementsByModelType = new Map();
    this.pluginPromisesByModelType = new Map();
    this.pluginUrlsByModelType = new Map();
  }

  ensureResources(modelState) {
    this.ensureStyle(modelState);
    return this.ensurePlugin(modelState);
  }

  ensureStyle(modelState) {
    const cssText = modelState.ui.style_css;
    if (!cssText || this.styleElementsByModelType.has(modelState.model_type)) {
      return;
    }

    const styleElement = document.createElement('style');
    styleElement.dataset.modelType = modelState.model_type;
    styleElement.textContent = cssText;
    document.head.appendChild(styleElement);
    this.styleElementsByModelType.set(modelState.model_type, styleElement);
  }

  ensurePlugin(modelState) {
    const scriptText = modelState.ui.script_js;
    if (!scriptText) {
      return Promise.resolve(null);
    }

    const existingPluginPromise = this.pluginPromisesByModelType.get(modelState.model_type);
    if (existingPluginPromise !== undefined) {
      return existingPluginPromise;
    }

    const blob = new Blob([scriptText], { type: 'text/javascript' });
    const objectUrl = URL.createObjectURL(blob);
    this.pluginUrlsByModelType.set(modelState.model_type, objectUrl);

    const pluginPromise = import(objectUrl)
      .then((module) => module.default ?? module)
      .catch((error) => {
        console.error(`Failed to load model UI plugin for ${modelState.model_type}`, error);
        return null;
      });

    this.pluginPromisesByModelType.set(modelState.model_type, pluginPromise);
    return pluginPromise;
  }
}

class GenericModelOverlay {

  constructor(modelId, mapPosition, uiPluginManager, ui) {
    this.modelId = modelId;
    this.mapPosition = mapPosition;
    this.uiPluginManager = uiPluginManager;
    this.ui = ui;
    this.popupOffset = { x: 0, y: 0 };
    this.dragState = null;
    this.plugin = null;
    this.pluginInitialized = false;
    this.templateData = {};

    this.feature = new ol.Feature({
      type: 'modelMarker',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([mapPosition.lon, mapPosition.lat])),
    });

    this.markerElement = document.createElement('div');
    this.markerElement.className = 'model-indicator-host';

    this.popupElement = document.createElement('div');
    this.popupElement.className = 'simulation-popup-anchor';

    this.popupCard = document.createElement('div');
    this.popupCard.className = 'simulation-popup';
    this.popupElement.appendChild(this.popupCard);

    this.popupOverlay = new ol.Overlay({
      element: this.popupElement,
      position: this.feature.getGeometry().getCoordinates(),
    });

    this.indicatorOverlay = new ol.Overlay({
      element: this.markerElement,
      position: this.feature.getGeometry().getCoordinates(),
      positioning: 'center-center',
    });

    this.markerElement.addEventListener('click', (event) => {
      this.ui.suppressMapClicks();
      event.preventDefault();
      event.stopPropagation();
      this.openPopup();
    });

    this.popupElement.addEventListener('pointerdown', (event) => {
      const closeButton = event.target.closest('.simulation-popup-close');
      if (closeButton === null) {
        return;
      }

      this.ui.suppressMapClicks(500);
      event.preventDefault();
      event.stopPropagation();
      this.closePopup();
    }, true);

    this.popupElement.addEventListener('mousedown', (event) => {
      const header = event.target.closest('.simulation-popup-header');
      const closeButton = event.target.closest('.simulation-popup-close');
      if (header === null || closeButton !== null) {
        return;
      }

      this.dragState = {
        startX: event.clientX,
        startY: event.clientY,
        originX: this.popupOffset.x,
        originY: this.popupOffset.y,
      };
      this.ui.suppressMapClicks();
      event.stopPropagation();
      event.preventDefault();
    });

    this.popupElement.addEventListener('click', (event) => {
      this.ui.suppressMapClicks();
      event.preventDefault();
      event.stopPropagation();
      if (event.target.closest('.simulation-popup-close') !== null) {
        this.closePopup();
      }
    });

    this.popupElement.addEventListener('dblclick', (event) => {
      this.ui.suppressMapClicks();
      event.preventDefault();
      event.stopPropagation();
    });

    document.addEventListener('mousemove', (event) => {
      if (this.dragState === null) {
        return;
      }

      this.popupOffset = {
        x: this.dragState.originX + (event.clientX - this.dragState.startX),
        y: this.dragState.originY + (event.clientY - this.dragState.startY),
      };
      this.applyPopupOffset();
    });

    document.addEventListener('mouseup', () => {
      this.dragState = null;
    });
  }

  async update(modelState) {
    this.plugin = await this.uiPluginManager.ensureResources(modelState);
    const coordinate = ol.proj.fromLonLat([modelState.map_position.lon, modelState.map_position.lat]);
    this.feature.setGeometry(new ol.geom.Point(coordinate));
    this.popupOverlay.setPosition(coordinate);
    this.indicatorOverlay.setPosition(coordinate);

    const pluginContext = {
      feature: this.feature,
      helpers: pluginHelpers,
      indicatorElement: this.markerElement,
      mapPosition: modelState.map_position,
      modelState,
      overlay: this,
      popupElement: this.popupElement,
      popupCard: this.popupCard,
      templateData: createTemplateData(modelState),
    };
    if (this.plugin?.extendTemplateData !== undefined) {
      const extraTemplateData = this.plugin.extendTemplateData(pluginContext) || {};
      pluginContext.templateData = createTemplateData(modelState, extraTemplateData);
    }
    this.templateData = pluginContext.templateData;

    if (this.plugin !== null && !this.pluginInitialized) {
      this.plugin.onOverlayCreate?.({
        ...pluginContext,
        templateData: this.templateData,
      });
      this.pluginInitialized = true;
    }

    this.feature.setStyle(null);
    this.markerElement.classList.remove('is-hidden');
    if (this.plugin?.renderIndicator !== undefined) {
      const indicatorHtml = this.plugin.renderIndicator({
        ...pluginContext,
        templateData: this.templateData,
      });
      this.markerElement.innerHTML = indicatorHtml || '';
    } else {
      this.markerElement.innerHTML = renderTemplate(modelState.ui.indicator_html, this.templateData) || '<div class="model-indicator default-indicator"></div>';
    }

    if (this.plugin?.renderTooltip !== undefined) {
      this.popupCard.innerHTML = this.plugin.renderTooltip({
        ...pluginContext,
        templateData: this.templateData,
      }) || '';
    } else {
      this.popupCard.innerHTML = renderTemplate(modelState.ui.tooltip_html, this.templateData) || `
        <div class="simulation-popup-header">
          <span class="simulation-popup-title">${modelState.display_name}</span>
          <button type="button" class="simulation-popup-close" aria-label="Close popup">x</button>
        </div>
        <div class="simulation-popup-body">
          <pre class="vehicle-json">${JSON.stringify(modelState.state, null, 2)}</pre>
        </div>
      `;
    }

    if (this.plugin?.onOverlayUpdate !== undefined) {
      this.plugin.onOverlayUpdate({
        ...pluginContext,
        templateData: this.templateData,
      });
    }
    this.applyPopupOffset();
  }

  openPopup() {
    this.popupElement.classList.add('open');
  }

  closePopup() {
    this.ui.suppressMapClicks();
    this.popupElement.classList.remove('open');
  }

  focusOnMap(map) {
    const coordinate = this.feature.getGeometry().getCoordinates();
    const view = map.getView();
    view.cancelAnimations();
    view.setCenter(coordinate);
  }

  applyPopupOffset() {
    this.popupCard.style.transform = `translate(calc(-50% + ${this.popupOffset.x}px), calc(-100% + ${this.popupOffset.y}px))`;
  }

  destroy() {
    if (this.pluginInitialized && this.plugin?.onOverlayDestroy !== undefined) {
      this.plugin.onOverlayDestroy({
        feature: this.feature,
        indicatorElement: this.markerElement,
        overlay: this,
        popupElement: this.popupElement,
        popupCard: this.popupCard,
        templateData: this.templateData,
      });
    }
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
    this.modelCountField = document.getElementById('simulation_model_count');
    this.vehicleLatitudeField = document.getElementById('vehicle_latitude');
    this.vehicleLongitudeField = document.getElementById('vehicle_longitude');
    this.targetVelocityValueField = document.getElementById('target_velocity_value');
    this.accelerationSliderValueField = document.getElementById('acceleration_slider_value');

    this.vehiclePositionSlider.oninput = () => {
      this.positionValueField.textContent = metersToDisplay(this.vehiclePositionSlider.value);
      $.get(`${apiBaseUrl}/api/actions/set_vehicle_position`, { position: this.vehiclePositionSlider.value });
    };

    this.targetVelocitySlider.oninput = () => {
      this.targetVelocityValueField.textContent = `${this.targetVelocitySlider.value} km/h`;
      this.pushVehicleOutput();
    };

    this.accelerationSlider.oninput = () => {
      this.accelerationSliderValueField.textContent = `${formatNumber(this.accelerationSlider.value)} m/s²`;
      this.pushVehicleOutput();
    };

    $.get(`${apiBaseUrl}/api/actions/get_route_information`, (data) => {
      this.vehiclePositionSlider.max = parseInt(data.length, 10);
      this.routeLengthField.textContent = metersToDisplay(data.length);
    });
  }

  pushVehicleOutput() {
    $.get(`${apiBaseUrl}/api/actions/set_vehicle_output`, {
      acceleration: this.accelerationSlider.value,
      target_velocity: this.targetVelocitySlider.value,
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
    this.modelCountField.textContent = simulationState.models.length;
  }
}

class UI {

  constructor() {
    this.controlMenu = new ControlMenu();
    this.followVehicle = false;
    this.suppressMapClicksUntil = 0;
    this.latestVehicleCoordinate = null;
    this.overlaysByModelId = new Map();
    this.uiPluginManager = new ModelUiResourceManager();
    this.centerVehicleButton = document.getElementById('center_vehicle_button');
    this.followVehicleButton = document.getElementById('follow_vehicle_button');
    this.modelOverviewList = document.getElementById('simulation_model_list');

    this.routeLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        url: 'routes/ostfalia-wf-wob.gpx',
        format: new ol.format.GPX(),
      }),
      style: (feature) => baseStyles[feature.getGeometry().getType()],
    });

    this.vehicleMarker = new ol.Feature({
      type: 'geoMarker',
      geometry: new ol.geom.Point(ol.proj.fromLonLat([10.547558, 52.176758])),
    });

    this.vehicleMarkerLayer = new ol.layer.Vector({
      source: new ol.source.Vector({
        features: [this.vehicleMarker],
      }),
      style: (feature) => baseStyles[feature.get('type')],
    });

    this.modelMarkerLayer = new ol.layer.Vector({
      source: new ol.source.Vector({}),
      style: (feature) => feature.getStyle(),
    });

    this.osmLayer = new ol.layer.Tile({
      source: new ol.source.OSM(),
    });

    this.map = new ol.Map({
      layers: [this.osmLayer, this.routeLayer, this.vehicleMarkerLayer, this.modelMarkerLayer],
      view: new ol.View({
        center: ol.proj.fromLonLat([10.547558, 52.176758]),
        zoom: 15,
      }),
      target: 'map',
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

    this.modelOverviewList.addEventListener('click', (event) => {
      const row = event.target.closest('[data-model-id]');
      if (row === null) {
        return;
      }

      const modelOverlay = this.overlaysByModelId.get(row.dataset.modelId);
      if (modelOverlay === undefined) {
        return;
      }

      this.disableFollowVehicle();
      modelOverlay.focusOnMap(this.map);
      modelOverlay.openPopup();
    });

    this.map.on('click', (evt) => {
      const originalTarget = evt.originalEvent?.target;
      if (originalTarget instanceof Element) {
        if (originalTarget.closest('.simulation-popup-anchor') !== null || originalTarget.closest('.model-indicator-host') !== null) {
          return;
        }
      }

      if (Date.now() < this.suppressMapClicksUntil) {
        return;
      }

      let selectedFeature;
      this.map.forEachFeatureAtPixel(evt.pixel, (feature) => {
        selectedFeature = feature;
      });

      this.overlaysByModelId.forEach((overlay) => {
        if (overlay.feature === selectedFeature) {
          overlay.openPopup();
        }
      });
    });

    this.updateFollowVehicleButton();
  }

  suppressMapClicks(durationMs = 250) {
    this.suppressMapClicksUntil = Date.now() + durationMs;
  }

  disableFollowVehicle() {
    if (!this.followVehicle) {
      return;
    }

    this.followVehicle = false;
    this.updateFollowVehicleButton();
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
        duration: 250,
      });
      return;
    }

    view.setCenter(this.latestVehicleCoordinate);
  }

  updateFollowVehicleButton() {
    this.followVehicleButton.textContent = this.followVehicle ? 'Follow vehicle: On' : 'Follow vehicle: Off';
    this.followVehicleButton.classList.toggle('active', this.followVehicle);
  }

  findOrCreateModelOverlay(modelState) {
    let overlay = this.overlaysByModelId.get(modelState.model_id);
    if (overlay !== undefined) {
      return overlay;
    }

    overlay = new GenericModelOverlay(modelState.model_id, modelState.map_position, this.uiPluginManager, this);
    this.overlaysByModelId.set(modelState.model_id, overlay);
    this.modelMarkerLayer.getSource().addFeature(overlay.feature);
    this.map.addOverlay(overlay.indicatorOverlay);
    this.map.addOverlay(overlay.popupOverlay);
    return overlay;
  }

  async renderModelOverview(modelState) {
    const plugin = await this.uiPluginManager.ensureResources(modelState);
    let templateData = createTemplateData(modelState);
    if (plugin?.extendTemplateData !== undefined) {
      const extraTemplateData = plugin.extendTemplateData({
        helpers: pluginHelpers,
        modelState,
        templateData,
      }) || {};
      templateData = createTemplateData(modelState, extraTemplateData);
    }
    const wrapper = document.createElement('button');
    wrapper.type = 'button';
    wrapper.className = 'topic-list-row topic-list-card';
    wrapper.dataset.modelId = modelState.model_id;
    if (plugin?.renderOverview !== undefined) {
      wrapper.innerHTML = plugin.renderOverview({
        helpers: pluginHelpers,
        modelState,
        templateData,
      }) || '';
    } else {
      wrapper.innerHTML = renderTemplate(modelState.ui.overview_html, templateData) || `
        <article class="model-card">
          <header class="model-card-header">
            <strong class="model-card-title">${modelState.display_name}</strong>
            <span class="topic-state-pill">${modelState.model_type}</span>
          </header>
          <pre class="vehicle-json">${JSON.stringify(modelState.state, null, 2)}</pre>
        </article>
      `;
    }
    return wrapper;
  }

  async syncModels(models) {
    this.modelOverviewList.innerHTML = '';

    const activeIds = new Set();
    for (const modelState of models) {
      activeIds.add(modelState.model_id);
      this.modelOverviewList.appendChild(await this.renderModelOverview(modelState));

      if (modelState.map_position === null) {
        continue;
      }

      const overlay = this.findOrCreateModelOverlay(modelState);
      await overlay.update(modelState);
    }

    Array.from(this.overlaysByModelId.keys()).forEach((modelId) => {
      if (activeIds.has(modelId)) {
        return;
      }

      const overlay = this.overlaysByModelId.get(modelId);
      overlay.destroy();
      this.modelMarkerLayer.getSource().removeFeature(overlay.feature);
      this.map.removeOverlay(overlay.indicatorOverlay);
      this.map.removeOverlay(overlay.popupOverlay);
      this.overlaysByModelId.delete(modelId);
    });

    if (models.length === 0) {
      this.modelOverviewList.innerHTML = '<div class="topic-list-empty">No simulation models loaded for the current scenario.</div>';
    }
  }

  async handleSimulationStateUpdate(simulationState) {
    this.controlMenu.handleSimulationStateUpdate(simulationState);
    await this.syncModels(simulationState.models || []);

    const vehicleLon = simulationState.vehicle_state.position_coordinates.lon;
    const vehicleLat = simulationState.vehicle_state.position_coordinates.lat;
    this.latestVehicleCoordinate = ol.proj.fromLonLat([vehicleLon, vehicleLat]);
    this.setVehiclePosition(vehicleLon, vehicleLat);

    if (this.followVehicle) {
      this.centerOnVehicle(false);
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
