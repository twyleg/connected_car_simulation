export default {
  extendTemplateData({ modelState }) {
    return {
      value_class: modelState.state.value ? 'true' : 'false',
      value_label: modelState.state.value ? 'true' : 'false',
    };
  },
};
