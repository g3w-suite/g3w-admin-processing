const { ApplicationState } = g3wsdk.core;
const { GUI } =              g3wsdk.gui;

export default ({

  // language=html
  template: /* html */ `
  <div class = "qprocessing-model-results">
    <div
      v-for   = "result in model.results"
      v-if    = "result.urls.length"
      :key    = "result.id"
    >
      <h4 style = "font-weight: bold">{{ result.label }}</h4>
      <span class = "divider"></span>
        <ul
          class = "treeview-menu menu-items"
          style = "background-color: #2c3b41"
        >
          <li
            v-for  = "( url, index) in result.urls" :key = "url.value"
            class  = "menu-item"
            style  = "display: flex; justify-content: space-between; padding: 5px;"
          >
            <span>{{ url.key }}</span>
            <section style = "padding: 3px; cursor: pointer; font-weight: bold;">
              <i
                style               = "margin: 0 5px;"
                :class              = "g3wtemplate.font['download']"
                @click.stop.prevent = "downloadFile(url.value)"
              ></i>
              <i
                :class              = "g3wtemplate.font['trash']"
                style               = "color: red"
                @click.stop.prevent = "removeResult(result, index)"
              ></i>
            </section>
          </li>
        </ul>
    </div>
  </div>`,

  name: "ModelResults",
  props: {
    model: {
      type: Object,
    }
  },
  methods: {
    //@since v3.7.0
    removeResult(result, index) {
      result.urls.splice(index, 1);
      //In case of no urls in result, remove from model result
      if (0 === result.urls.length) {
        this.model.results = this.model.results.filter(r => result.id !== r.id);
      }
      //Close results panel in case of no results
      if (0 === this.model.results.length) {
        GUI.closePanel();
      }
    },
    /**
     * 
     * @param {*} url 
     */
    async downloadFile(url) {
      try {
        ApplicationState.download = true;
        const response = url && await fetch(url, {
          headers: { 'Access-Control-Expose-Headers': 'Content-Disposition' }, // get filename from server
          signal:  AbortSignal.timeout(60000),
        });
        if (!response?.ok) {
          throw (await response.json()).message;
        }
        const blob = await response.blob();
        Object.assign(document.createElement('a'), {
          href:     URL.createObjectURL(blob),
          download: (response.headers.get('content-disposition') || 'filename=g3w_download_file').split('filename=').at(-1).split('filename=').at(-1)
        }).click();
        URL.revokeObjectURL(blob);
      } finally {
        ApplicationState.download = false;
      }
    }
  }
});