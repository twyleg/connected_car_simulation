export function formatNumber(value, digits = 1) {
  return Number(value || 0).toFixed(digits);
}

export function metersToDisplay(value) {
  return `${Math.round(value || 0)} m`;
}

export function kmhFromMetersPerSecond(value) {
  return Number(value || 0) * 3.6;
}
