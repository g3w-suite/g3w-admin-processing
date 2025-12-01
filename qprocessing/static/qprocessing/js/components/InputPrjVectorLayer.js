import DrawInputVectorFeatures from './DrawInputVectorFeatures.js';

const { GUI } = g3wsdk.gui;

export default ({

  // language=html
  template: /* html */ `
  <div
    v-if  = "state.visible"
    class = "form-group prj-vector-layer"
  >

    <label :for = "state.name" v-disabled = "!state.editable">
      {{ state.label }}
      <span v-if = "state.validate && state.validate.required">*</span>
    </label>

    <section v-if = "showUploadFile" class = "vector-tools-context" v-disabled = "upload">
      <section class = "vector-tools">
        <div
          class = "qprocessing-upload-vector-file"
          style = "flex-grow: 2"
        >
          <section class = "upload-file-content">
            <form
              class                  = "addlayer skin-border-color"
              v-t-tooltip:top.create = "'qprocessing.add_layer_drag'"
            >
              <input
                ref     = "file"
                type    = "file"
                title   = " "
                @change = "addLayer({ file: $refs.file.files[0], type: 'upload' })"
                accept  = ".zip,.geojson,.GEOJSON,.kml,.kmz,.KMZ,.KML,.json,.gpx,.gml,.csv"
              />
              <div class = "drag_and_drop">
                <i class = "fa-2x fas fa-cloud-upload-alt" aria-hidden = "true"></i>
              </div>
            </form>
          </section>
        </div>
        
        <draw-input-vector-features 
          :upload       = "upload" 
          @toggled-tool = "toggleTempLayer" 
          :datatypes    = "state.input.options.datatypes" 
          @add-layer    = "addLayer"
        />
      </section>
  
    </section>

    <select
      v-select2 = "'value'"
      :id       = "state.name"
      ref       = "select_layer"
      style     = "width:100%;"
      class     = "form-control"
    >
      <option
        v-for  = "value in state.input.options.values"
        :key   = "value.value"
        :value = "value.value">{{ value.key }}
      </option>
    </select>
    <div
      v-if       = "isSelectedFeatures"
      v-disabled = "selected_features_disabled"
      class      = "prjvectorlayerfeature-only-selected-features"
    >
      <input
        v-model = "selected_features_checked"
        type    = "checkbox"
        :id     = "state.name + '_checkbox'"
      />
      <label
        style      = "margin-top: 10px;"
        :for       = "state.name + '_checkbox'"
        v-t-plugin = "'qprocessing.inputs.prjvectorlayerfeature.selected_features'">
      </label>
    </div>

    <p
      v-if   = "notvalid"
      class  = "g3w-long-text error-input-message"
      style  = "margin: 0"
      v-html = "state.validate.message"
    ></p>
    <p
      v-else-if = "state.info"
      style     = "margin: 0 "
      v-html    = "state.info"
    ></p>

    <div
      v-if   = "state.help && this.state.help.visible"
      v-html = "state.help.message"
      class  = "g3w_input_help skin-background-color extralighten">
    </div>

  </div>
  `,

  name: "InputPrjVectorLayer",

  components: {
    DrawInputVectorFeatures,
  },

  props: {
    modelId: { type: Number, required: true },
    state:   { type: Object, required: true }
  },

  data() {
    return {
      upload:                     false,
      errorUpload:                false,
      value:                      null,
      selected_features_checked:  false,
      selected_features_disabled: true
    }
  },

  computed: {

    /**
     * @returns { boolean } whether datatypes contain geometries values
     */
    showUploadFile() {
      return !!this.state.input.options.datatypes.find(datatype => (datatype === 'anygeometry') || (['point', 'line', 'polygon'].indexOf(datatype) !== -1));
    },

    //check if it can take in account of selected features
    isSelectedFeatures() {
      return 'prjvectorlayerfeature' === this.state.input.type;
    },

    //check if is no valid
    notvalid() {
      return false === this.state.validate.valid;
    },

  },

  methods: {

    /**
     * Show/hide temp tool
     */
    toggleTempLayer(bool) {
      this.addTempLayer.setVisible(bool);
    },

    /**
     * @param {*} param0 
     */
    async addLayer({ file, features = [] } = {}) {
     //set initial reactive properties
     this.upload      = true;
     this.errorUpload = false;
     try {
        const qprocessing    = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');
        const { key, value } = await qprocessing.uploadFile({
          file,
          inputName: this.state.name,
          modelId:   this.modelId,
        });
        //need to add only one external file
        this.state.input.options.values = this.state.input.options.values.filter(({ key, value }) => !value.startsWith('file:'));

        //handle temp layer

        this.addTempLayer.getSource().clear(); //clear all eventually previous features
        this.addTempLayer.getSource().addFeatures(features); //add eventually features
        this.addTempLayer.setVisible(true); //visible true

        this.state.input.options.values.push({ key, value });

        await this.$nextTick();
        this.value = value;
        //set current select item
        $(this.$refs.select_layer)
          .select2()
          .val(value)
          .trigger('change');
     } catch(e) {
       console.warn(e);
       this.errorUpload = true;
     }
     this.upload = false;
   },

    /**
     * Check if a layer has selected features
     * 
     * @param layerId
     * @returns {*}
     */
    getLayerSelectedFeaturesIds(layerId) {
      return GUI.getService('map').defaultsLayers.selectionLayer.getSource().getFeatures().filter(f => layerId === f.__layerId).map(f => f.getId());
    },

    /**
     * @TODO
     * @param layerId
     */
    setDisabledSelectFeaturesCheckbox(layerId){
      this.selected_features_disabled = 0 === this.getLayerSelectedFeaturesIds(layerId).length === 0;
      //in case go disabled, uncheck checkbox
      if (true === this.selected_features_disabled) {
        this.selected_features_checked = false;
      }
    },

    /**
     *Set input layer value based on selected feature id or not
     * @param checked
     */
    setInputValueFromSelectedFeatures(checked) {
      const currentLayerFeatureSelectedIds = this.getLayerSelectedFeaturesIds(this.value);
      if (true === checked && currentLayerFeatureSelectedIds.length > 0) {
        this.state.value = `${this.value}:${currentLayerFeatureSelectedIds.join(',')}`
      } else {
        this.state.value = this.value;
      }

      this.$emit('changeinput', this.state);
    },

    /**
     *
     * @param layer external layer Object
     * @param datatypes Array
     * @returns {boolean}
     */
    isExternalLayerValidForInputDatatypes({ layer, datatypes = [] } = {}) {
      return (
        undefined !== datatypes.find(type => 'anygeometry' === type) ||
        undefined !== datatypes.map(type  => ({ 'point': 'Point', 'line': 'LineString', 'polygon': 'Polygon' })[type]).filter(Boolean).find(type => type.replace('Multi','') === layer.geometryType.replace('Multi',''))
      )
    },

    /**
     * Get all Project Vector Layers that has geometry types
     * @param datatypes <Array> of String
     *   'nogeometry',
     *   'point',
     *   'line',
     *   'polygon',
     *   'anygeometry'
     * return <Array>
     */
    getInputPrjVectorLayerData(datatypes = []) {
      const layers = [];
      //check if any geometry layer type is request
      const anygeometry    = undefined !== datatypes.find(data_type => data_type === 'anygeometry');
      //check if no geometry layer type is request
      const nogeometry     = undefined !== datatypes.find(data_type => data_type === 'nogeometry');
      //get geometry_types only from data_types array
      const geometry_types = datatypes.map(type => ({ 'point': 'Point', 'line': 'LineString', 'polygon': 'Polygon' })[type]).filter(Boolean);
  
      g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing').getProject().getLayers()
        //exclude base layer
        .filter(l => !l.baselayer)
        .forEach(l => {
          const key   = l.name;
          const value = l.id;
          //get layer if it has no geometry
          if (true === nogeometry && (undefined === l.geometrytype || "NoGeometry" === l.geometrytype)) {
            layers.push({ key, value })
            return;
          }
  
          if (null !== l.geometrytype && undefined !== l.geometrytype && "NoGeometry" !== l.geometrytype) {
            // in the case of any geometry type
            if (true === anygeometry) {
              layers.push({ key, value })
            } else {
              if (geometry_types.length > 0) {
                if (undefined !== geometry_types.find(geometry_type => geometry_type.replace('Multi','') === l.geometrytype.replace('Multi',''))) {
                  layers.push({key, value})
                }
              }
            }
          }
      })
  
      //check for external
      if (anygeometry || geometry_types.length > 0) {
        //get external layers from catalog
        GUI.getService('catalog').getExternalLayers({ type: 'vector' }).forEach(l => {
          if (this.isExternalLayerValidForInputDatatypes({ layer: l, datatypes })) {
            layers.push({
              key:   l.name,
              value: `__g3w__external__:${l.id}`
            })
          }
        })
      }
  
      return layers;
    },

  },

  watch: {

    // listen change of value (input select)
    value(value) {
      if (true === this.isSelectedFeatures) {
        this.setDisabledSelectFeaturesCheckbox(value);
      }
      this.state.value          = value;
      this.state.validate.valid = ![undefined, null].includes(value);
      this.$emit('changeinput', this.state);
    },

    // Listen selected feature checkbox event change
    selected_features_checked(checked) {
      this.setInputValueFromSelectedFeatures(checked);
    },

    async notvalid(value) {
      await this.$nextTick();
      if (this.select2) {
       this.select2.data('select2').$container[value ? "addClass" : "removeClass"]("input-error-validation")
      }
    },

  },

  created() {
    const qprocessing = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');

    //set initial values
    this.state.input.options.values = this.getInputPrjVectorLayerData(this.state.input.options.datatypes);

    if (this.state.input.options.values.length > 0) {
      this.value                = this.state.input.options.values[0].value;
      this.state.validate.valid = true;
    }

    // In case of selected features
    if (null !== this.value && this.isSelectedFeatures) {
      this.selected_features_id = []; // create array of selected id features
      //register
      qprocessing.registersSelectedFeatureLayersEvent();
      qprocessing.on('change-selected-features', () => {
        this.setDisabledSelectFeaturesCheckbox(this.value);
        this.setInputValueFromSelectedFeatures(this.selected_features_checked);
      });
    }

    // temporary layer filled by upload or draw tools
    this.addTempLayer = new ol.layer.Vector({ source: new ol.source.Vector() });

    // add to map
    GUI.getService('map').getMap().addLayer(this.addTempLayer);

    // set initial visibility to false
    this.addTempLayer.setVisible(false);

    // listen add external Layer
    this.keyAddExternal =  GUI.getService('catalog')
      .onafter('addExternalLayer', ({ type, layer }) => {
        if ('vector' !== type) { return }
        if (this.isExternalLayerValidForInputDatatypes({ layer, datatypes: this.state.input.options.datatypes })) {
          this.state.input.options.values.push({
            key:   layer.name,
            value: `__g3w__external__:${layer.id}`
          });
        }
      })

  },

  async mounted() {
    await this.$nextTick();
    this.select2 = $(this.$refs.select_layer);
    // emit add input to validate
    this.$emit('addinput', this.state);
    this.$emit('changeinput', this.state);
  },

  beforeDestroy() {
    const qprocessing = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');

    if (this.isSelectedFeatures) {
      qprocessing.unregistersSelectedFeatureLayersEvent();
      qprocessing.removeAllListeners('change-selected-features');
    }

    // remove temp layer
    this.addTempLayer.getSource().clear();
    GUI.getService('map').getMap().removeLayer(this.addTempLayer);
    this.addTempLayer = null;

    // remove external layer
    GUI.getService('catalog').un('addExternalLayer', this.keyAddExternal);
  },

});

document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
  <style>
    /* Replicate same scoped style in InputBase.vue */
    .prj-vector-layer label             { text-align: left !important; padding-top: 0 !important; margin-bottom: 3px; }
    .vector-tools-context               { margin-bottom: 5px; }
    .vector-tools                       { display: flex; justify-content: space-between; }
    .vector-tools-message               { margin: 3px; }
    .vector-tools-message .error-upload { font-weight: bold; color: red; }
    .qprocessing-upload-vector-file form.addlayer   { position: relative; border: 2px dashed; text-align: center; border-radius: 3px; }
    .qprocessing-upload-vector-file .addlayer input { position: absolute; margin: 0; padding: 0; width: 100%; height: 100%; outline: 0; opacity: 0; cursor: pointer; display: block; }
    .qprocessing-upload-vector-file .drag_and_drop  { line-height: 20px; padding: 5px; color: #fff; }
  </style>`,
);