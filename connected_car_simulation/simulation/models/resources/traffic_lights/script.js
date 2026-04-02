const trafficLightFeatureStyles = {
  red: new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_red.png',
      scale: 0.1,
    }),
  }),
  yellow: new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_yellow.png',
      scale: 0.1,
    }),
  }),
  green: new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, -0.1],
      src: 'img/traffic_light_green.png',
      scale: 0.1,
    }),
  }),
};

function buildTimingVisualization(period, ratio, t) {
  const normalizedPeriod = Number(period || 0);
  const yellowFraction = normalizedPeriod > 0 ? Math.min(1, 1 / normalizedPeriod) : 0;
  const redFraction = Math.max(0, Math.min(1, Number(ratio || 0)));
  const greenFraction = Math.max(0, 1 - redFraction - yellowFraction);
  const progress = normalizedPeriod > 0 ? Math.min(1, Number(t || 0) / normalizedPeriod) : 0;

  return {
    redFraction,
    yellowFraction,
    greenFraction,
    progress,
  };
}

export default {
  extendTemplateData({ helpers, modelState }) {
    const state = modelState.state;
    const timing = buildTimingVisualization(state.period, state.ratio, state.t);
    return {
      state_upper: `${state.state || ''}`.toUpperCase(),
      position_display: helpers.metersToDisplay(state.position_on_route ?? 0),
      period_display: `${helpers.formatNumber(state.period, 1)} s`,
      ratio_display: helpers.formatNumber(state.ratio, 2),
      time_display: `${helpers.formatNumber(state.t, 2)} s`,
      red_width: `${timing.redFraction * 100}%`,
      yellow_width: `${timing.yellowFraction * 100}%`,
      green_width: `${timing.greenFraction * 100}%`,
      progress_left: `${timing.progress * 100}%`,
    };
  },

  onOverlayUpdate({ feature, indicatorElement, modelState }) {
    const state = modelState.state.state || 'red';
    feature.setStyle(trafficLightFeatureStyles[state] || trafficLightFeatureStyles.red);
    indicatorElement.innerHTML = '';
    indicatorElement.classList.add('is-hidden');
  },
};
