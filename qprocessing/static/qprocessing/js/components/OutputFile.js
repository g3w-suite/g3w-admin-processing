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
      class = "col-sm-12"
    >{{state.label}}</label>
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
          :value = "value"
        >{{key}}</option>
      </select>
    </div>
  </div>`,

  name: "OutputFile",
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
    async task(response={}) {
     const {task_result={}} = response;
      this.$emit('add-result-to-model-results', {
       output: this.state,
       result: task_result
     })
    }
  },
});