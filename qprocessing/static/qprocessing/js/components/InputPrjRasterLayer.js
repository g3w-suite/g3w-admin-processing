import UploadRasterFile from "./UploadRasterFile.js";
const { selectMixin }      = g3wsdk.gui.vue.Mixins;
const { ProjectsRegistry } = g3wsdk.core.project;

export default ({

  // language=html
  template: /* html */ `
  <div
    v-if  = "state.visible"
    class = "form-group prj-raster-layer"
  >

    <slot name = "label">
      <label
        :for       = "state.name"
        v-disabled = "!state.editable"
        class      = "col-sm-12">
        {{ state.label }}
        <span v-if = "state.validate && state.validate.required">*</span>
      </label>
    </slot>

    <div class = "col-sm-12">

      <section v-disabled = "upload" style = "margin-bottom: 5px">
        <section class = "vector-tools">
          <upload-raster-file         
            :upload    = "upload" 
            @add-layer = "addLayer" />
          </section>
          <section class = "raster-tools-message">
            <div v-if = "errorUpload" class = "error-upload"> Errore </div>
          </section>
      </section>

      <slot name = "body">
        <select
          v-select2 = "'value'"
          :id       = "state.name"
          ref       = "select"
          style     = "width:100%;"
          class     = "form-control"
        >
          <option
           v-for  = "value in state.input.options.values"
           :key   = "value.value"
           :value = "value.value"
          >{{ value.key }}</option>
        </select>
      </slot>

      <slot name = "message">
        <p
          v-if   = "notvalid"
          v-html = "state.validate.message"
          class  = "g3w-long-text error-input-message"
          style  = "margin: 0"
        ></p>
        <p
          v-else-if = "state.info"
          v-html    = "state.info"
          style     = "margin: 0"
        ></p>
      </slot>

      <div
        v-if   = "state.help && this.state.help.visible"
        v-html = "state.help.message"
        class  = "g3w_input_help skin-background-color extralighten"
      ></div>

    </div>

  </div>
  `,

  name: "InputPrjRasterLayer",
  mixins: [selectMixin],
  components: { UploadRasterFile },
  props: {
    modelId: {
      type:     Number,
      required: true,
    },
    state: {
      type:     Object,
      required: true
    }
  },
  data(){
    return {
      upload:      false,
      errorUpload: false,
      value:       null,
    }
  },
  methods: {
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
        this.state.input.options.values = this.state.input.options.values.filter(({key, value}) => !value.startsWith('file:'));

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

  },
  computed: {
    //recreate same computed property of input editing
    notvalid() {
      return this.state.validate.valid === false;
    }
  },
  watch: {
    //listen change of value (input select)
    'value'(value) {
      this.state.value = value;
      this.$emit('changeinput', this.state);
    }
  },
  created() {

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
    this.state.input.options.values = ProjectsRegistry.getCurrentProject().getLayers()
      //exclude base layer
      .filter(layer => !layer.baselayer && (undefined !== layer.source && layer.source.type === 'gdal'))
      .map(layer => ({
        key:   layer.name,
        value: layer.id
      }));

    if (this.state.input.options.values.length > 0) {
      //set initial value
      this.value                = this.state.input.options.values[0].value;
      this.state.validate.valid = true;
    }

    /**
     * temporary layer filled by upload or draw tools
     */

    this.addTempLayer = new ol.layer.Vector({ source: new ol.source.Vector() });

    //add to map
    GUI.getService('map').getMap().addLayer(this.addTempLayer);

    //set initial visibility to false
    this.addTempLayer.setVisible(false);

  },
  async mounted(){
    await this.$nextTick();
    //set select2 needed to selectMixin
    this.select2 = $(this.$refs.select);
    this.$emit('addinput', this.state);
  },
});

document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
  <style>
    /* Replicate same scoped style in InputBase.vue */
    .prj-raster-layer label { text-align: left !important; padding-top: 0 !important; margin-bottom: 3px; }
  </style>`,
);