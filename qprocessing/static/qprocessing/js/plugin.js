(async function() { try {

  const BASE_URL = `${initConfig.group.plugins.qprocessing.baseUrl}qprocessing/js`;

  const { ApplicationState } = g3wsdk.core;
  const { Plugin }           = g3wsdk.core.plugin;
  const { ProjectsRegistry } = g3wsdk.core.project;
  const { GUI, Panel }       = g3wsdk.gui;

  new class extends Plugin {
    constructor() {
      super({ name: 'qprocessing' });

      // i18n
      const VM = new Vue();
      const i18n = async lang => {
        this.setLocale({ [lang]: (await import(`${BASE_URL}/i18n/${lang}.js`)).default });
      };

      VM.$watch(() => ApplicationState.language, i18n);

      // Show loading plugin icon
      this.setHookLoading({ loading: true });

      GUI.isReady().then(async() => {

         if (!this.registerPlugin(this.config.gid)) {
          return;
        }
 
        await i18n(ApplicationState.language);
        
        this.emitChangeSelectedFeatures            = () => this.emit('change-selected-features');
        this.registersSelectedFeatureLayersEvent   = this.registersSelectedFeatureLayersEvent.bind(this);
        this.unregistersSelectedFeatureLayersEvent = this.unregistersSelectedFeatureLayersEvent.bind(this);
  
        // layer fields based on layerId and datatype
        this.layerFields = {};

        this.createSideBarComponent({
          data: () => ({ models: this.config.models, service: this }),
          template: /* html */`
            <ul
              id    = "g3w-client-plugin-qprocessing"
              class = "treeview-menu g3w-tools menu-items"
            >
              <li
                v-for       = "model in models"
                :key        = "model.id"
                @click.stop = "service.showPanel(model)"
              >
                <i :class="g3wtemplate.getFontClass('tool')"></i>
                <span>{{ model.display_name }}</span>
              </li>
            </ul>
          `,
        }, this.config.sidebar);

        this.setHookLoading({loading: false});

        this.setReady(true);
      });
    }

    async showPanel(model) {
      new Panel({
        id: 'qprocessing-panel',
        title: 'plugins.qprocessing.title',
        internalPanel: new (Vue.extend((await import(BASE_URL + '/components/ModelPanel.js')).default))({
          propsData: { model },
        }),
        show: true,
      });
    }

    registersSelectedFeatureLayersEvent() {
      GUI.getService('map').defaultsLayers.selectionLayer.getSource().on('addfeature', this.emitChangeSelectedFeatures);
      GUI.getService('map').defaultsLayers.selectionLayer.getSource().on('removefeature', this.emitChangeSelectedFeatures);
    }

    unregistersSelectedFeatureLayersEvent() {
      GUI.getService('map').defaultsLayers.selectionLayer.getSource().un('addfeature', this.emitChangeSelectedFeatures);
      GUI.getService('map').defaultsLayers.selectionLayer.getSource().un('removefeature', this.emitChangeSelectedFeatures);
    }

    createGeoJSONFile({features=[], name, crs}={}) {
      return new File(
        [JSON.stringify(Object.assign(
          (new ol.format.GeoJSON()).writeFeaturesObject(features), {
            crs: {
              type: "name",
              properties: {
                "name": crs || GUI.getService('map').getCrs() //add crs to geojsonObject
              }
            }
          }))],
        `${name}.geojson`,
        {
          type: "application/geo+json",
        }
      );
    }

    async uploadFile({modelId, inputName, file}) {
      const data = new FormData();
      data.append('file', file);
      const response = await fetch(`${this.config.urls.upload}${modelId}/${ProjectsRegistry.getCurrentProject().getId()}/${inputName}/`, {
        method: 'POST',
        body: data,
      });
      const json = await response.json();
      if (json.result) {
        return {
          key: file.name,
          value: `file:${json.data.file}`
        }
      }
    }

  }

} catch (e) { console.error(e); } })();