const { XHR } = g3wsdk.core.utils;

export default ({

  // language=html
  template: /* html */ `
    <div
      v-if  = "state.visible"
      class = "form-group field-chooser"
    >

      <label :for = "state.name" v-disabled = "!state.editable">
        {{ state.label }}
        <span v-if = "state.validate && state.validate.required">*</span>
      </label>
      
      <div v-if = "loading" class  = "bar-loader"></div>

      <select
        v-select2   = "'value'"
        :multiple   = "state.input.options.multiple"
        :id         = "state.name"
        ref         = "select"
        style       = "width:100%;"
        class       = "form-control"
      >
        <option
          v-if   = "state.validate.required && !state.input.options.multiple"
          :value = "null"
        >---</option>
        <option
          v-for     = "value in state.input.options.values"
          :selected = "state.input.options.default_to_all_fields"
          :key      = "value.value"
          :value    = "value.value"
        >{{ value.key }}</option>
      </select>

      <p
        v-if       = "notvalid"
        class      = "g3w-long-text error-input-message"
        style      = "margin: 0"
        v-t-plugin = "state.validate.message"
      ></p>
      <p
        v-else-if = "state.info"
        style     = "margin: 0 "
        v-html    = "state.info"
      ></p>

      <div
        v-if   = "state.help && this.state.help.visible"
        v-html = "state.help.message"
        class  = "g3w_input_help skin-background-color extralighten"
      ></div>
    </div>
  `,

  name: "InputFieldChooser",

  props: {
    state: { type: Object, required: true },
  },

  data() {
    return {
      loading: false,
      value:   this.state.input.options.multiple ? [] : null,
    }
  },

  computed: {

    notvalid() {
      return false === this.state.validate.valid;
    },

    autocomplete() {
      return 'select_autocomplete' === this.state.input.type && this.state.input.options.usecompleter;
    },

  },

  watch: {

    //listen change of value (input select)
    value(value) {
      const is_multiple = this.state.input.options.multiple;

      // handle multiple/single selection
      this.state.value  = is_multiple ? value.join(',') : value;

      // validate in case of required
      if (true === this.state.validate.required) {
        this.state.validate.valid = is_multiple ? value.length > 0 : ("" !== value && null !== value);
      }

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
    //set it true at beginning to reactivity
    this.state.validate.valid = true;
  },

  async mounted() {
    //if required we set message of not valid input
    if (this.state.validate.required) {
      this.state.validate.message = `qprocessing.inputs.fieldchooser.validate.message.${this.state.input.options.multiple ? 'multiple' : 'single'}`
    }

    await this.$nextTick();
    //set this.select2 element
    this.select2 = $(this.$refs.select);

    //emit register change input to listen parent input layer value and get related fields
    this.$emit('register-change-input', {
      inputName: this.state.input.options.parent_field,
      handler:   async (layerId) => {

        //in case of change parent value change, in case of selectefeature need to get only layerId without featuresid
        layerId = layerId.split(':')[0];

        //set values from Input layer fields
        const params = {
          datatype: this.state.input.options.datatype,
        };

        // Extract fields from project layerId

        this.loading = true;
        let error;

        const qprocessing = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');

        // Check if it already fills by layerId
        if (undefined === qprocessing.layerFields[layerId]) {
          qprocessing.layerFields[layerId] = {};
        }

        // check if it was fill based on params
        const GIVE_ME_A_NAME = qprocessing.layerFields[layerId][JSON.stringify(params)];

        //check if layerId belong to project layer or is id of temporary upload layer
        if (undefined === GIVE_ME_A_NAME && undefined === qprocessing.getProject().getLayers().find(layer => layer.id === layerId)) {
          qprocessing.layerFields[layerId][JSON.stringify(params)] = [];
        } else if (undefined === GIVE_ME_A_NAME) {
          try {
            //do request to api
            const response = await XHR.get({
              url: `${qprocessing.config.urls.fields}${qprocessing.getProject().getId()}/${layerId}/`,
              params
            });
            if (true === response.result) {
              qprocessing.layerFields[layerId][JSON.stringify(params)] = response.fields;
            }
          } catch(e) {
            error = e;
          }
        }

        if (error) {
          console.warn(error);
          this.state.input.options.values = [];
        } else {
          this.state.input.options.values = qprocessing.layerFields[layerId][JSON.stringify(params)]
        }

        this.loading = false;

        //check if multiple
        if (this.state.input.options.multiple) {
          //value is set checking if default_all_fields is true, set all options values by defaults, otherwise empty array
          this.value = this.state.input.options.default_to_all_fields ? this.state.input.options.values.map(({value}) => value) : [];
        } else {
          this.value = null;
        }

        // in case of no value or values set value to null
        if (this.value === null || (Array.isArray(this.value) && this.value.length === 0)) {
          this.select2.val(null).trigger('change');
        }
      }
    })

    this.state.validate.valid = !this.state.validate.required;
    //emit add input
    this.$emit('addinput', this.state);
  },
});

document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
  <style>
  /* Replicate same scoped style in InputBase.vue */
  .field-chooser label { text-align: left !important; padding-top: 0 !important; margin-bottom: 3px; }
  </style>`,
);