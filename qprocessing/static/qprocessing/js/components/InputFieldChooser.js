const GUI     = g3w.app;
const { XHR } = g3w.utils;

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

      <x-select
        :id         = "state.name"
        ref         = "select"
        :value      = "state.input.options.multiple ? null : value"
        :multiple   = "state.input.options.multiple"
        searchable
        @change     = "onSelectChange"
        style       = "width:100%;"
      >
        <x-option
          v-if   = "state.validate.required && !state.input.options.multiple"
          value  = ""
        >---</x-option>
        <x-option
          v-for     = "value in state.input.options.values"
          :selected = "state.input.options.default_to_all_fields"
          :key      = "value.value"
          :value    = "value.value"
        >{{ value.key }}</x-option>
      </x-select>

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

  // Initialize the selected value from the input configuration.
  data() {
    return {
      loading: false,
      value:   this.state.input.options?.multiple
        ? (this.state.input.options.default_to_all_fields ? (this.state.input.options.values || []).map(({ value }) => value) : [])
        : null,
    }
  },

  computed: {

    // Expose the current validation state to the template.
    notvalid() {
      return false === this.state.validate.valid;
    },

  },

  methods: {

    // Copy the selected option values into component state.
    onSelectChange({ target }) {
      this.value = this.state.input.options.multiple
        ? target.selected_options.map(option => option.value)
        : (target.value || null);
    },

    // Synchronize the select UI without emitting another change event.
    syncSelect(value = this.value) {
      const select = this.$refs.select;
      if (!select?.container) {
        return;
      }
      const multiple = this.state.input.options.multiple;
      const values = (multiple ? value : [value])
        .filter(value => null !== value && undefined !== value)
        .map(String);
      const options = Array.from(select.container.querySelectorAll('x-option'));
      select.selected_options = [];
      options.forEach(option => option.removeAttribute('selected'));
      values.forEach(value => {
        const option = options.find(option => option.value === value);
        if (option) {
          select.select(option, { autoclose: false, emit: false });
        }
      });
      if (!values.length) {
        const emptyOption = !multiple && options.find(option => !option.value);
        select.select(emptyOption || null, { autoclose: false, emit: false });
      }
      select.setAttribute('value', values.join(','));
    },

  },

  watch: {

    // Update shared input state and validate required selections.
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

    // Reflect validation errors on the select after rendering.
    async notvalid(value) {
      await this.$nextTick();
      this.$refs.select?.classList.toggle('input-error-validation', value);
    },

  },

  // Start the component with a valid initial state.
  created() {
    //set it true at beginning to reactivity
    this.state.validate.valid = true;
  },

  // Initialize validation and register the parent-field change handler.
  async mounted() {
    //if required we set message of not valid input
    if (this.state.validate.required) {
      this.state.validate.message = `qprocessing.inputs.fieldchooser.validate.message.${this.state.input.options.multiple ? 'multiple' : 'single'}`
    }

    await this.$nextTick();
    if (this.state.input.options.multiple) {
      this.syncSelect();
    }

    //emit register change input to listen parent input layer value and get related fields
    this.$emit('register-change-input', {
      inputName: this.state.input.options.parent_field,
      // Load available fields whenever the parent layer changes.
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

        const qprocessing = GUI.getPlugin('qprocessing');

        // Check if it already fills by layerId
        if (undefined === qprocessing.layerFields[layerId]) {
          qprocessing.layerFields[layerId] = {};
        }

        // check if it was fill based on params
        const GIVE_ME_A_NAME = qprocessing.layerFields[layerId][JSON.stringify(params)];

        //check if layerId belong to project layer or is id of temporary upload layer
        if (undefined === GIVE_ME_A_NAME && undefined === g3w.state.project.getLayers().find(l => layerId === l.state.id)) {
          qprocessing.layerFields[layerId][JSON.stringify(params)] = [];
        } else if (undefined === GIVE_ME_A_NAME) {
          try {
            //do request to api
            const response = await XHR.get({
              url: `${qprocessing.config.urls.fields}${g3w.state.project.getId()}/${layerId}/`,
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
          this.syncSelect();
        }
      }
    })

    this.state.value = this.state.input.options.multiple ? this.value.join(',') : this.value;
    this.state.validate.valid = !this.state.validate.required || (this.state.input.options.multiple ? this.value.length > 0 : true);
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
  .input-error-validation .x-select-trigger { border-color: #dc3545; }
  </style>`,
);