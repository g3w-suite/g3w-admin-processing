import json
import subprocess
from pathlib import Path

from behave import given, then, when


@given('project layers from raster and vector providers')
def project_layers(context):
    context.layers = [
        {'id': name, 'name': name, 'baselayer': base, 'source': {'type': provider}}
        for name, provider, base in [
            ('file', 'gdal', False),
            ('postgres', 'postgresraster', False),
            ('wcs', 'wcs', False),
            ('wms', 'wms', False),
            ('arcgis', 'arcgismapserver', False),
            ('legacy', 'raster', False),
            ('vector', 'ogr', False),
            ('base', 'gdal', True),
            ('excluded', 'gdal', False),
        ]
    ]


@when('the raster selector is initialized')
def initialize_selector(context):
    component = Path(__file__).resolve().parents[2] / 'static' / 'qprocessing' / 'js' / 'components' / 'InputPrjRasterLayer.js'
    script = """
        const fs = require('node:fs');
        const layers = JSON.parse(fs.readFileSync(0, 'utf8'));
        global.g3w = {
          app: { getPlugin: () => ({ config: { exclude_layers: ['excluded'] } }) },
          state: { project: { getLayers: () => layers.map(state => ({ state })) } },
        };
        global.document = { head: { insertAdjacentHTML() {} } };
        const source = fs.readFileSync(process.argv[1]);
        import(`data:text/javascript;base64,${source.toString('base64')}`).then(({ default: component }) => {
          const instance = { state: { input: { options: { values: [] } }, validate: {} } };
          component.created.call(instance);
          process.stdout.write(JSON.stringify({ options: instance.state.input.options.values, value: instance.value }));
        });
    """
    result = subprocess.run(
        ['node', '-e', script, str(component)], input=json.dumps(context.layers), text=True,
        stdout=subprocess.PIPE, check=True,
    )
    context.selector = json.loads(result.stdout)


@then('only eligible raster layers are listed')
def check_layers(context):
    assert [option['value'] for option in context.selector['options']] == [
        'file', 'postgres', 'wcs', 'wms', 'arcgis', 'legacy',
    ]


@then('the first raster layer is selected')
def check_selection(context):
    assert context.selector['value'] == 'file'
