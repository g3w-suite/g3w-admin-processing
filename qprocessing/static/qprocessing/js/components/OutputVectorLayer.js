const { GUI }                       = g3wsdk.gui;
const { uniqueId }                  = g3wsdk.core.utils;
const { createVectorLayerFromFile } = g3wsdk.core.geoutils;

export default ({

  // language=html
  template: /* html */ `
  <div
    v-t-tooltip:top.create = "state.description"
    class                  = "form-group">
    <label
      style = "color:#fff !important;"
      :for  = "state.name"
      class = "col-sm-12">{{ state.label }}
    </label>
    <div class="col-sm-12">
      <select
        :id       = "state.name"
        v-select2 = "'type'"
        ref       = "select2"
        class     = "form-control qprocessing-output-vectorlayer-select"
      >
        <option
          v-for  = "({key, value}) in state.input.options.values"
          :key   = "key"
          :value = "value">{{key}}
        </option>
      </select>
      <input
        style   = "width:100%;"
        class   = "magic-checkbox"
        v-model = "checked"
        type    = "checkbox"
        :id     = "state.name + '_checkbox'"
      ><label
        style      = "margin-top: 10px;"
        :for       = "state.name + '_checkbox'"
        v-t-plugin = "'qprocessing.outputs.outputvector.open_file_on_map'"
      ></label>
    </div>
  </div>`,

  name: "OutputVectorLayer",
  props: {
    state: {
      type: Object,
      required: true
    },
    task: {
      required: true
    }
  },
  data() {
    this.state.value = this.state.input.options.values[0].value;
    return {
      checked: true,
      type: this.state.value,
    }
  },
  methods: {
    changeSelect(value) {
      this.state.value = value;
    }
  },
  watch: {
    type(value) {
      this.changeSelect(value)
    },
    async task(res={}) {
     const {task_result={}} = res;
     //get value from name of the output
     const downloadUrl = task_result[this.state.name];

     //add to map
     if (this.checked) {
      let name =  `${uniqueId()}_${this.type}`, crs = GUI.getService('map').getEpsg();
      // convert shp → zip
      const type = 'shp' !== this.type  ? this.type : 'zip';
      const response = await fetch(downloadUrl);
      try {
        name = response.headers.get("content-disposition").split('filename=')[1].replace(/"/g,'');
      } catch(e) {
        console.warn(e);
      }
      let data = await response.blob();

      // skip adding csv file to map
      if ('csv' === type) {
        return;
      }

      // ie. geojson, kml
      if (!['zip', 'kmz'].includes(type)) {
        data = await (new Promise(resolve => {
          const reader = new FileReader();
          reader.addEventListener("load", () => { resolve(reader.result) }, false);
          reader.readAsText(data);
        }));
      }

      GUI.getService('map').addExternalLayer(
        await createVectorLayerFromFile({ name, data, crs, mapCrs: crs, type }),
        { type, downloadUrl, color: `#${((1<<24)*Math.random() | 0).toString(16)}` });
     }

     //always add to results
     this.$emit('add-result-to-model-results', {
      output: this.state,
      result: task_result
     })

    }
  },
});