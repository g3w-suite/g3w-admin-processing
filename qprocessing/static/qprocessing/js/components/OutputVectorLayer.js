const { GUI }                      = g3wsdk.gui;
const { GEOMETRY_FIELDS }          = g3wsdk.constant;
const { uniqueId, getUniqueDomId } = g3wsdk.core.utils;

export default ({

  // language=html
  template: /* html */ `
  <div
    v-t-tooltip:top.create = "state.description"
    class                  = "form-group"
  >
    <label
      style = "color:#fff !important;"
      :for  = "state.name"
    >{{ state.label }}</label>
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
      class   = "magic-checkbox"
      v-model = "checked"
      type    = "checkbox"
      :id     = "state.name + '_checkbox'"
    ><label
      style      = "margin-top: 10px;"
      :for       = "state.name + '_checkbox'"
      v-t-plugin = "'qprocessing.outputs.outputvector.open_file_on_map'"
    ></label>
  </div>`,

  name: "OutputVectorLayer",

  props: {
    state: { type: Object, required: true },
    task:  { required: true }
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

    async task(res = {}) {
     const { task_result = {} } = res;
     const downloadUrl = task_result[this.state.name]; // get value from name of the output

     //add to map
     if (this.checked) {
      let name =  `${uniqueId()}_${this.type}`;
      let crs  = GUI.getService('map').getEpsg();

      // convert shp → zip
      const type     = 'shp' === this.type  ? 'zip' : this.type;
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

      if (!window.JSZip) {
        await import('../vendors/jszip.min.js');
      }

      if (!window.shp) {
        await import('../vendors/shp.min.js');
      }

      let olLayer;

      const epsg   = ['zip', 'kml', 'kmz'].includes(type) ? 'EPSG:4326' : crs;
    
      // SHAPE FILE
      if ('zip' === type) {
        data = JSON.stringify(await shp(await data.arrayBuffer(data))); // un-zip folder data 
      }
    
      // KMZ FILE
      if ('kmz' === type) {
        const zip = new JSZip();
        zip.load(await data.arrayBuffer(data));
        data = zip.file(/.kml$/i).at(-1).asText(); // get last kml file within folder
      }

      let features = ({
        'gpx'    : new ol.format.GPX(),
        'gml'    : new ol.format.WMSGetFeatureInfo(),
        'geojson': new ol.format.GeoJSON(),
        'zip'    : new ol.format.GeoJSON(),
        'kml'    : new ol.format.KML({ extractStyles: false }),
        'kmz'    : new ol.format.KML({ extractStyles: false }),
      })[type].readFeatures(data, { dataProjection: epsg, featureProjection: crs || epsg });
    
      // ignore kml property [`<styleUrl>`](https://developers.google.com/kml/documentation/kmlreference)
      if (['kml', 'kmz'].includes(type)) {
        features.forEach(f => f.unset('styleUrl'));
      }
    
      if (features.length) {
        olLayer = new ol.layer.Vector({
          source: new ol.source.Vector({ features }),
          name,
          _fields: 'csv' === type ? data.headers : Object.keys(features[0].getProperties()).filter(prop => GEOMETRY_FIELDS.indexOf(prop) < 0),
          id:      getUniqueDomId(),
          style:   undefined
        });
      } else {
        throw 'invalid layer';
      }

      GUI.getService('map').addExternalLayer(olLayer, {
        type,
        downloadUrl,
        color: `#${((1<<24)*Math.random() | 0).toString(16)}`
      });

     }

     //always add to results
     this.$emit('add-result-to-model-results', {
        output: this.state,
        result: task_result
     })

    },

  },
});