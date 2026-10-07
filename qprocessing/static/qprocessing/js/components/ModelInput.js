export default {
  name: 'qprocessing-model-input',

  template: /* html */ `
    <div v-if = "state.visible" class = "form-group">
      <label :for = "state.name" class = "control-label">
        {{ state.label }}<span v-if = "state.validate.required"> *</span>
      </label>

      <select
        v-if             = "hasOptions"
        :id              = "state.name"
        :value           = "state.value"
        :multiple        = "options.multiple"
        :disabled        = "!state.editable"
        class            = "form-control"
        :aria-invalid    = "!state.validate.valid"
        :aria-describedby = "!state.validate.valid ? errorId : null"
        @change          = "updateSelect"
      >
        <option v-if = "!options.multiple && !state.validate.required" value = "">---</option>
        <option
          v-for  = "option in options.values"
          :key   = "optionValue(option)"
          :value = "optionValue(option)"
        >{{ optionLabel(option) }}</option>
      </select>

      <textarea
        v-else-if        = "['textarea_input', 'texthtml_input'].includes(type)"
        :id              = "state.name"
        :value           = "state.value"
        :placeholder     = "state.default"
        :disabled        = "!state.editable"
        rows             = "3"
        class            = "form-control"
        :aria-invalid    = "!state.validate.valid"
        :aria-describedby = "!state.validate.valid ? errorId : null"
        @input           = "updateValue"
      ></textarea>

      <input
        v-else
        :id              = "state.name"
        :type            = "controlType"
        :value           = "state.value"
        :checked         = "'checkbox' === controlType && !!state.value"
        :placeholder     = "state.default"
        :step             = "options.step || options.values?.[0]?.Step || 1"
        :min              = "options.min ?? options.values?.[0]?.min"
        :max              = "options.max ?? options.values?.[0]?.max"
        :disabled         = "!state.editable"
        class             = "form-control"
        :aria-invalid     = "!state.validate.valid"
        :aria-describedby = "!state.validate.valid ? errorId : null"
        @input            = "updateValue"
      >

      <p v-if = "!state.validate.valid" :id = "errorId" class = "error-input-message" role = "status">
        {{ state.validate.message }}
      </p>
      <p v-else-if = "state.info">{{ state.info }}</p>
    </div>
  `,

  props: {
    state: { type: Object, required: true },
  },

  computed: {
    // Normalize the configured type for template checks.
    type() {
      return this.state.input.type.endsWith('_input') ? this.state.input.type : `${this.state.input.type}_input`;
    },
    // Return the configured options or an empty object.
    options() {
      return this.state.input.options || {};
    },
    // Check whether this input should render as a select control.
    hasOptions() {
      return Array.isArray(this.options.values) && [
        'select_input',
        'select_autocomplete_input',
        'unique_input',
        'radio_input',
      ].includes(this.type);
    },
    // Map processing input types to native input types.
    controlType() {
      if ('color_input' === this.type) { return 'color'; }
      if (['integer_input', 'bigint_input', 'float_input', 'range_input', 'slider_input'].includes(this.type)) { return 'number'; }
      if ('check_input' === this.type) { return 'checkbox'; }
      return 'text';
    },
    // Provide a stable ID for the validation message.
    errorId() {
      return `${this.state.name}-error`;
    },
  },

  // Register the input and report its initial validation state.
  mounted() {
    this.$emit('addinput', this.state);
    this.updateValidation();
  },

  methods: {
    // Extract a value from either an option object or a primitive.
    optionValue(option) {
      return option && 'object' === typeof option ? option.value : option;
    },
    // Extract a label from either an option object or a primitive.
    optionLabel(option) {
      return option && 'object' === typeof option ? (option.key ?? option.value) : option;
    },
    // Store selected values and revalidate the input.
    updateSelect(event) {
      const { target } = event;
      this.state.value = target.multiple
        ? Array.from(target.selectedOptions, option => option.value)
        : ('' === target.value ? null : target.value);
      this.updateValidation();
    },
    // Normalize a native input value before updating component state.
    updateValue(event) {
      const { target } = event;
      this.state.value = 'checkbox' === target.type
        ? target.checked
        : ('number' === target.type && '' !== target.value ? Number(target.value) : ('' === target.value ? null : target.value));
      this.updateValidation();
    },
    // Update required-field validity and notify the parent component.
    updateValidation() {
      const value = this.state.value;
      const empty = null === value || undefined === value || '' === value || (Array.isArray(value) && 0 === value.length);
      this.state.validate.empty = empty;
      this.state.validate.valid = !empty || !this.state.validate.required;
      this.$emit('changeinput', this.state);
    },
  },
};