# Create A Custom Model

This example shows how to add a custom simulation model to the connected car simulation by following the `ExampleModel` pattern.

## Overview

A custom model consists of:

- a Python model class
- a Python factory class
- optional UI resources:
  - `overview.html`
  - `indicator.html`
  - `tooltip.html`
  - `style.css`
  - `script.js`
- a config section that declares model instances
- registration code that tells `ConnectedCarSimulation` which factory belongs to which XML tag

The working reference implementation is:

- [example_model.py](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/example_model.py)
- [extended_simulation.py](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/extended_simulation.py)
- [config.xml](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/config.xml)

## 1. Create The Model Class

Create a class that inherits from `SimulationModel`.

Example:

```python
class ExampleModel(SimulationModel):
    TOGGLE_PERIOD_SECONDS = 2.0

    def __init__(self, identifier: int, position_on_route: float):
        self.identifier = identifier
        self.position_on_route = position_on_route
        self.value = False
        self.last_toggle_timestamp = 0.0
```

Your model should implement:

- `model_id`
- `model_type`
- `display_name` (optional but recommended)
- `update(context)`
- `get_state()`
- `get_vehicle_input()`

Optional:

- `get_position_on_route()`
- `html_overview()`
- `html_indicator()`
- `html_tooltip()`
- `css_styles()`
- `script_module()`

## 2. Update The Model Over Time

The simulation calls `update(context)` on every simulation step.

`context` contains:

- `route`
- `vehicle_state`
- `previous_simulation_state`
- `simulation_timestamp`

Example:

```python
def update(self, context: SimulationStepContext) -> None:
    if (context.simulation_timestamp - self.last_toggle_timestamp) < self.TOGGLE_PERIOD_SECONDS:
        return

    self.value = not self.value
    self.last_toggle_timestamp = context.simulation_timestamp
```

Use `previous_simulation_state` if your model must react to the last published simulation state rather than only its own internal fields.

## 3. Return Model State

`get_state()` should return the state that is published to the UI.

Example:

```python
def get_state(self) -> Dict[str, Any]:
    return {
        "id": self.identifier,
        "value": self.value,
        "position_on_route": self.position_on_route,
    }
```

If you want the model to appear on the map, include either:

- `position_on_route` and implement `get_position_on_route()`, or
- direct coordinates via `lon` and `lat`

## 4. Return Vehicle Input

`get_vehicle_input()` defines what is exposed to external vehicle controllers.

Example:

```python
def get_vehicle_input(self) -> Dict[str, Any]:
    return self.get_state()
```

The data is grouped by `model_type` in the vehicle input payload.

## 5. Create The Factory

Factories create one model instance from one XML element.

Example:

```python
class ExampleModelFactory(SimulationModelFactory):
    def create(self, config: Dict[str, Any], route: Route) -> Optional[ExampleModel]:
        identifier = int(config.attrib["id"])
        position_on_route = float(config.attrib["position_on_route"])
        return ExampleModel(identifier, position_on_route)
```

The `config` argument is the matching XML element.

## 6. Add UI Resources

Store UI resources in a folder next to the model, for example:

```text
examples/extension/models/resources/
```

The example model uses:

- [overview.html](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/resources/overview.html)
- [indicator.html](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/resources/indicator.html)
- [tooltip.html](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/resources/tooltip.html)
- [style.css](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/resources/style.css)
- [script.js](/home/twyleg/dev/workspace/connected_car_simulation/examples/extension/models/resources/script.js)

Load them from the model class:

```python
def html_overview(self) -> str:
    return (RESOURCES_DIR / "overview.html").read_text(encoding="utf-8")
```

Do the same for indicator, tooltip, CSS, and script if needed.

## 7. Use Template Variables In HTML

The HTML resources can use placeholders like:

```html
{{display_name}}
{{position_on_route}}
{{value}}
```

These are filled from:

- `modelState.state`
- `display_name`
- `model_id`
- `model_type`
- extra values returned by `script.js`

## 8. Use `script.js` For Derived UI Data

`script.js` is optional. It is useful when the HTML needs derived values.

The example uses:

```js
export default {
  extendTemplateData({ modelState }) {
    return {
      value_class: modelState.state.value ? 'true' : 'false',
      value_label: modelState.state.value ? 'true' : 'false',
    };
  },
};
```

That makes `{{value_class}}` and `{{value_label}}` available to the HTML templates.

Supported hooks currently include:

- `extendTemplateData(context)`
- `renderOverview(context)`
- `renderIndicator(context)`
- `renderTooltip(context)`
- `onOverlayCreate(context)`
- `onOverlayUpdate(context)`
- `onOverlayDestroy(context)`

Use `extendTemplateData` first. Only use the render or lifecycle hooks if templated HTML is not enough.

## 9. Add CSS In `style.css`

`style.css` is injected once per `model_type` in the browser.

Use it for model-specific visuals so package CSS stays generic.

## 10. Declare Model Instances In XML

Add a config section with one XML element per model instance.

Example:

```xml
<ConnectedCarSimulationConfig>
    <ExampleModels>
        <ExampleModel id="1" position_on_route="50.0"/>
        <ExampleModel id="2" position_on_route="100.0"/>
    </ExampleModels>
</ConnectedCarSimulationConfig>
```

The package config is loaded first. Your extension config is merged on top of it.

## 11. Register The Custom Model

Register the factory and XML tag in your startup code.

Example:

```python
connected_car_simulation = ConnectedCarSimulation(
    config_file_path=FILE_DIR / "config.xml",
)
connected_car_simulation.load_builtin_models()
connected_car_simulation.load_custom_model(
    model_factory=ExampleModelFactory,
    config_tag="ExampleModel",
)
await connected_car_simulation.run()
```

`config_tag="ExampleModel"` must match the XML element name used in the config.

## 12. Summary

To add a new custom model:

1. Create a `SimulationModel`
2. Create a `SimulationModelFactory`
3. Add optional UI resources
4. Add model instances to XML
5. Register the factory with `load_custom_model(...)`

The `ExampleModel` in this folder is the reference implementation for that workflow.
