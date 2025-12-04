export default ({

  // language=html
  template: /* html */ `
  <div
    v-if  = "state.visible"
    class = "form-group prj-raster-layer"
  >

    <label
      :for       = "state.name"
      v-disabled = "!state.editable">
      {{ state.label }}
      <span v-if = "state.validate && state.validate.required">*</span>
    </label>

    <section v-disabled = "upload" style = "margin-bottom: 5px">
      <section>
        <div v-if = "upload" class = "bar-loader" style = "margin-bottom: 5px;"></div>
        <div
          class = "qprocessing-upload-raster-file"
          style = "flex-grow: 2"
        >
          <section class = "upload-file-content">
            <form
              class                  = "addlayer skin-border-color"
            >
              <input
                type    = "file"
                ref     = "file"
                title   = " "
                @change = "addLayer"
                accept  = ".tif,.geotif"
              />
              <div class = "drag_and_drop">
                <i class = "fa-2x fas fa-file-upload"  aria-hidden = "true"></i>
              </div>
            </form>
          </section>
          <!-- FILE UPLOAD MAX SIZE -->
          <section v-if = "max_upload_file_size" style = "font-weight: bold;">
            <span v-t-plugin = "'qprocessing.inputs.file_max_size_upload'"></span> 
            <span >{{ max_upload_file_size/ 1024 }} KB</span>
          </section>

        </div>
      
      </section>
    </section>

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

    <div
      v-if   = "state.help && this.state.help.visible"
      v-html = "state.help.message"
      class  = "g3w_input_help skin-background-color extralighten"
    ></div>


  </div>
  `,

  name: "InputPrjRasterLayer",

  props: {
    modelId: { type: Number, required: true },
    state:   { type: Object, required: true }
  },

  data() {
    return {
      upload:               false,
      value:                null,
      max_upload_file_size: g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing').config?.max_upload_file_size,
    }
  },

  methods: {

    /**
     * Add Raster Layer
     */
    async addLayer(evt) {
      const file = evt?.target.files?.[0];
      if (!file) { return }
      //check if file has size more than max_upload_file_size
      if (this.max_upload_file_size && file.size > this.max_upload_file_size) {
        g3wsdk.gui.GUI.showUserMessage({
          type:     'warning',
          message:  'plugins.qprocessing.warning.file_max_size_upload',
          closable:  false,
          autoclose: true,
        })
        return;
      }

      //set initial reactive properties
      this.upload               = true;
      try {
        const qprocessing    = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');
        const { key, value } = await qprocessing.uploadFile({
          file,
          inputName: this.state.name,
          modelId:   this.modelId,
        });
        //need to add only one external file
        this.state.input.options.values = this.state.input.options.values.filter(({ key, value }) => !value.startsWith('file:'));

        this.state.input.options.values.push({ key, value });

        await this.$nextTick();
        this.value = value;
        //set current select item
        $(this.$refs.select)
          .select2()
          .val(value)
          .trigger('change');
      } catch(e) {
        console.warn(e);
        //reset input value to null
        this.$refs.file.value = null;
      }
      this.upload = false;
    },

  },

  computed: {

    //recreate same computed property of input editing
    notvalid() {
      return false === this.state.validate.valid;
    },

  },

  watch: {

    //listen change of value (input select)
    value(value) {
      this.state.value          = value;
      this.state.validate.valid = !this.state.required || !!value;
      this.$emit('changeinput', this.state);
    },

    async notvalid(value) {
      await this.$nextTick();
      if (this.select2) {
       this.select2.data('select2').$container[value ? "addClass" : "removeClass"]("input-error-validation")
      }
    },

  },

  created() {
    const qprocessing               = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing')
    const exclude_layers            = qprocessing.config?.exclude_layers || [];
    this.state.input.options.values = qprocessing.getProject().getLayers()
      //exclude base layer
      .filter(l => !exclude_layers.includes(l.id) && !l.baselayer && 'gdal' === l?.source?.type)
      .map(l => ({
        key:   l.name,
        value: l.id
      }));

    if (this.state.input.options.values.length > 0) {
      this.value                = this.state.input.options.values[0].value; // set initial value
      this.state.validate.valid = true;
    }
  },

  async mounted(){
    await this.$nextTick();
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
    .qprocessing-upload-raster-file form.addlayer   { position: relative; border: 2px dashed; text-align: center; border-radius: 3px; }
    .qprocessing-upload-raster-file .addlayer input { position: absolute; margin: 0; padding: 0; width: 100%; height: 100%; outline: 0; opacity: 0; cursor: pointer; display: block; }
    .qprocessing-upload-raster-file .drag_and_drop  { line-height: 20px; padding: 5px; color: #fff; }
  </style>`,
);