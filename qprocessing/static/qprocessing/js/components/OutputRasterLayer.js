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
   
    <select
      :id       = "state.name"
      v-select2 = "'type'"
      ref       = "select2"
      class     = "form-control qprocessing-output-vectorlayer-select"
    >
      <option
        v-for  = "({key, value}) in state.input.options.values"
        :key   = "key"
        :value = "value"
      >{{key}}</option>
    </select>
    
  </div>`,

  name: "OutputRasterLayer",

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
    },

    async task( response = {}) {
     const { task_result = {} } = response;
     const fileUrl = task_result[this.state.name];
     this.$emit('add-result-to-model-results', {
       url:    fileUrl,
       output: this.state,
       result: task_result
     })
    },

  },

});