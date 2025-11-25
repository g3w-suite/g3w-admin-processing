(async function() { try {

  const BASE_URL = `${initConfig.group.plugins.qprocessing.baseUrl}qprocessing/js`;

  const { ApplicationState } = g3wsdk.core;
  const { Plugin }           = g3wsdk.core.plugin;
  const { ProjectsRegistry } = g3wsdk.core.project;
  const { GUI, Panel }       = g3wsdk.gui;

  new class extends Plugin {
    constructor() {
      super({ 
        name: 'qprocessing',
        //Add to avoid initial show plugin.qrocessing.title
        i18n: {
          [ApplicationState.language] : {
            title: 'Geoprocessing',
          }
        } 
      });

      // i18n
      const VM = new Vue();
      const i18n = async lang => {
        import(`${BASE_URL}/i18n/${['it', 'en', 'fr'].includes(lang) ? lang : 'en'}.js`)
        .then(m => this.setLocale({ [lang]: m.default }))
        .catch(console.warn)
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
        id:           'qprocessing-panel',
        title:        'plugins.qprocessing.title',
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

    createGeoJSONFile({ features = [], name, crs } = {}) {
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

    /**
     * 
     * @param {*} param0 
     * @returns 
     */
    async uploadFile({ modelId, inputName, file }) {
      const data = new FormData();
      data.append('file', file);
      try {
        const response = await (await fetch(`${this.config.urls.upload}${modelId}/${this.getProject().getId()}/${inputName}/`, {
          method: 'POST',
          body:    data,
        })).json();
        if (response.result) {
          GUI.showUserMessage({
            type:    'success',
            message:  `UPLOAD FILE ${ file?.name }`,
            autoclose: true,
            closable:  false,
          })
          return {
            key:    file.name,
            value: `file:${response?.data?.file}`,
          }
        } else {
          GUI.showUserMessage({
            type: 'alert',
            message: response?.error || 'server_error',
          });
          return Promise.reject(response);
        }
      } catch(e) {
        GUI.showUserMessage({
          type:    'alert',
          message: e,
        })
        console.warn(e);
        return Promise.reject({ error: e });
      }
      
    }

    #tasks = [];

    /**
     * ORIGINAL SOURCE: g3wsdk.core.task.TaskService@v4.0.0
     */
    async runTask({
      method = 'GET',
      params = {},
      url,
      taskUrl,
      interval = 1000,
      timeout = Infinity,
      listener = () => {}
    } = {}) {
      try {
        const r = 'GET' === method
          ? await XHR.get({ url, params })
          : await XHR.post({ url, data: params.data || {}, contentType: params.contentType || "application/json" });
        if (r.result) {
          const id = setInterval(async () => {
            // check if timeout is defined
            timeout = timeout - interval;
            if (timeout > 0) {
              let r;
              try {
                r = await XHR.get({url: `${taskUrl}${r.task_id}`});
              } catch(e) {
                r = e;
                console.warn(e);
              }
              listener({ task_id: r.task_id, timeout: false, response: r });
            } else {
              listener({ timeout: true });
              this.stopTask(r.task_id);
            }
          }, interval);
          this.#tasks.push({ task_id: r.task_id, intervalId: id }); // add current task to list of task
          listener({ task_id: r.task_id, response: r });            // run first time listener function
        } else {
          return Promise.reject(r);
        }
      } catch(e) {
        console.warn(e);
        return Promise.reject(e);
      }
    }

    /**
     * ORIGINAL SOURCE: g3wsdk.core.task.TaskService@v4.0.0
     */
    stopTask(task_id) {
      const task = this.#tasks.find(t => task_id === t.task_id);
      if (task) { clearInterval(task.intervalId); }
    }

  }

} catch(e) { console.error(e); } })();