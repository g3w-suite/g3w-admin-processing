export default ({

  // language=html
  template: /* html */ `
  <div
    class                  = "form-group"
    v-t-tooltip:top.create = "state.description"
  >
    <label
      style = "color:#fff !important;"
      :for  = "state.name"
    >{{ state.label }}</label>
    <x-select
      :id       = "state.name"
      :value    = "type"
      searchable
      @change   = "type = $event.target.value"
      class     = "qprocessing-output-vectorlayer-select"
    >
      <x-option
        v-for  = "({key, value}) in state.input.options.values"
        :key   = "key"
        :value = "value"
      >{{ key }}</x-option>
    </x-select>
  </div>`,

  name: "OutputFile",

  props: {
    state: { type: Object, required: true },
    task:  { required: true }
  },

  data() {
    this.state.value = this.state.input.options.values[0].value;
    return {
      type: this.state.value,
    }
  },

  watch: {

    type(value) {
      this.state.value = value; // change select value
      this.$emit('changeoutput', this.state);
    },

    async task(response = {}) {
     const { task_result = {} } = response;
      this.$emit('add-result-to-model-results', {
       output: this.state,
       result: task_result
     })
    },

  },

});