(async function() { try {

  const BASE_URL = `${initConfig.group.plugins.qprocessing.baseUrl}qprocessing/js`;

  const { Plugin, Panel }   = g3w;
  const GUI                 = g3w.app;
  const { XHR }             = g3w.utils;

  new class extends Plugin {

    /**
     * ORIGINAL SOURCE: g3wsdk.core.task.TaskService@v4.0.0
     */
    #tasks = [];

    /**
     * layer fields based on layerId and datatype
     */
    layerFields = {};

    /** Initialize the plugin, register its sidebar, and mark it ready. */
    constructor() {
      super({ 
        name: 'qprocessing',
        //Add to avoid initial show plugin.qrocessing.title
        i18n: `${BASE_URL}/i18n/`,
      });

      
      // Show loading plugin icon
      this.setHookLoading({ loading: true });

      GUI.isReady().then(async() => {

         if (!this.registerPlugin(this.config.gid)) {
          return;
        }
         
        // Notify components when selected map features change.
        this.emitChangeSelectedFeatures            = () => this.emit('change-selected-features');
        this.registersSelectedFeatureLayersEvent   = this.registersSelectedFeatureLayersEvent.bind(this);
        this.unregistersSelectedFeatureLayersEvent = this.unregistersSelectedFeatureLayersEvent.bind(this);

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
                <i class="fas fa-cog"></i>
                <span>{{ model.display_name }}</span>
              </li>
            </ul>
          `,
        }, this.config.sidebar);

        this.setHookLoading({loading: false});

        this.setReady(true);
      });
    }

    /** Open the processing panel for the selected model. */
    async showPanel(model) {
      new Panel({
        id:           'qprocessing-panel',
        title:        'plugins.qprocessing.title',
        internalPanel: new (Vue.extend((await import(`${BASE_URL}/components/ModelPanel.js`)).default))({
          propsData: { model },
        }),
        show: true,
      });
    }

    /** Subscribe to feature selection changes on the map. */
    registersSelectedFeatureLayersEvent() {
      GUI.defaultsLayers.selectionLayer.getSource().on('addfeature',    this.emitChangeSelectedFeatures);
      GUI.defaultsLayers.selectionLayer.getSource().on('removefeature', this.emitChangeSelectedFeatures);
    }

    /** Remove the map feature selection subscriptions. */
    unregistersSelectedFeatureLayersEvent() {
      GUI.defaultsLayers.selectionLayer.getSource().un('addfeature',    this.emitChangeSelectedFeatures);
      GUI.defaultsLayers.selectionLayer.getSource().un('removefeature', this.emitChangeSelectedFeatures);
    }

    /** Serialize features into a GeoJSON file using the requested CRS. */
    createGeoJSONFile({ features = [], name, crs } = {}) {
      return new File(
        [JSON.stringify(Object.assign(
          (new ol.format.GeoJSON()).writeFeaturesObject(features), {
            crs: {
              type:       "name",
              properties: { "name": crs || GUI.getService('map').getCrs() } //add crs to geojsonObject
            
            }
          }))],
        `${name}.geojson`,
        {
          type: "application/geo+json",
        }
      );
    }

    /** Upload an input file and return its server-side reference. */
    async uploadFile({ modelId, inputName, file, showUserMessage = true }) {
      const data = new FormData();
      data.append('file', file);
      try {
        const response = await (await fetch(`${this.config.urls.upload}${modelId}/${g3w.state.project.getId()}/${inputName}/`, {
          method: 'POST',
          body:    data,
        })).json();
        if (response.result) {
          showUserMessage && GUI.showUserMessage({
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
          showUserMessage && GUI.showUserMessage({
            type: 'alert',
            message: response?.error || 'server_error',
          });
          return Promise.reject(response);
        }
      } catch(e) {
        showUserMessage && GUI.showUserMessage({
          type:    'alert',
          message: e,
        })
        console.warn(e);
        return Promise.reject({ error: e });
      }
      
    }

    /**
     * ORIGINAL SOURCE: g3wsdk.core.task.TaskService@v4.0.0
     */
    /** Start a processing task and periodically report its status. */
    async runTask({
      params = {},
      url,
      listener = () => {}
    } = {}) {
      try {
        const r = await XHR.post({ url, data: params.data || {}, contentType: params.contentType || "application/json" });
        if (!r.result) {
          return Promise.reject(r);
        }
        const id = setInterval(async () => {
          let task;
          try {
            task = await XHR.get({url: `${this.config.urls.taskinfo}${r.task_id}`});
          } catch(e) {
            task = e;
            console.warn(e);
          }
          listener({ task_id: r.task_id, timeout: false, response: task });
        }, (this.config?.task_info_interval * 1000 || 1000));
        this.#tasks.push({ task_id: r.task_id, intervalId: id }); // add current task to list of task
      } catch(e) {
        console.warn(e);
        return Promise.reject(e);
      }
    }

    /**
     * ORIGINAL SOURCE: g3wsdk.core.task.TaskService@v4.0.0
     */
    /** Stop polling the specified task. */
    stopTask(task_id) {
      const task = this.#tasks.find(t => task_id === t.task_id);
      if (task) {
        clearInterval(task.intervalId);
      }
    }

  }

} catch(e) { console.error(e); } })();