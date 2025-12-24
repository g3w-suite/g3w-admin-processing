import prjvectorlayer_input from '../components/InputPrjVectorLayer.js';
import prjrasterlayer_input from '../components/InputPrjRasterLayer.js';
import fieldchooser_input   from '../components/InputFieldChooser.js';
import outputvectorlayer    from '../components/OutputVectorLayer.js';
import outputrasterlayer    from '../components/OutputRasterLayer.js';
import outputfile           from '../components/OutputFile.js';

const { Panel }            = g3wsdk.gui;
const { GUI }              = g3wsdk.gui;
const { t }                = g3wsdk.core.i18n;

export default ({

  // language=html
  template: /* html */ `
  <div class = "qprocessing-model" v-disabled = "state.loading">

    <!-- MODEL NAME -->
    <section class = "qprocessing-model-header">
      <div class = "skin-color">{{ model.display_name.toUpperCase() }}</div>
    </section>

    <!-- NOTES   -->
    <section v-if = "model.note" class = "qprocessing-model-note">
      <div class = "title" >NOTE</div>
      <div v-html = "model.note" ></div>
    </section>

    <!-- INPUTS   -->
    <section class = "qprocessing-model-inputs">
      <div class = "title">INPUTS</div>
      <form class = "form-horizontal g3w-form">
        <component
          v-for                  = "input in model.inputs"
          :key                   = "input.name"
          :modelId               = "model.id"
          @register-change-input = "registerChangeInputEvent"
          @addinput              = "addToValidate"
          @changeinput           = "validate(input)"
          :state                 = "input"
          :is                    = "input.input.type + '_input'"
        />
      </form>
    </section>

    <!-- OUTPUTS   -->
    <section class = "qprocessing-model-outputs">
      <div class = "title">OUTPUTS</div>
      <form class = "form-horizontal g3w-form">
        <component
          v-for                        = "output in model.outputs"
          :key                         = "output.name"
          @add-result-to-model-results = "addResultToModel"
          @changeoutput                = "clearState"
          :state                       = "output"
          :task                        = "task"
          :is                          = "output.input.type"
        />
      </form>
    </section>

    <!-- FOOTER -->
    <section class = "qprocess-model-footer">
      <div>
        <!-- PROGRESS BAR -->
        <section v-if = "null !== state.progress" style = "margin-bottom: 5px;">
          <progress  max = "100" :value = "state.progress" style = "width:100%; accent-color: var(--skin-color);">{{ state.progress }}%</progress>
          <span style = "font-weight: bold; color: var(--skin-color);"> {{ state.progress }}% </span>
        </section>
      
        <!-- LOADING BAR -->
        <div v-else-if = "state.loading" class  = "bar-loader"></div>

        <button
          class       = "btn skin-background-color run"
          @click.stop = "run"
          :disabled   = "!valid || state.loading">
          <i class = "fas fa-play"></i>
        </button>

        <div v-if = "state.message.show">
         <span
          class       ="message"
          :style      = "{color: ({ success: 'green', error: 'red' })[this.state.message.type] }"
           v-t-plugin = "'qprocessing.run.messages.'+ state.message.type"
          ></span>
        </div>

      </div>
    </section>

    <!-- MODEL RESULTS   -->
    <section class = "qprocessing-model-results">
      <section style = "display: flex; justify-content: space-between; align-items: center">
        <div class = "title" v-t-plugin = "'qprocessing.results'"></div>
        <section> 
          <span                 
            v-disabled          = "!state.processing_html_log"
            class               = "icon skin-color skin-border-color fas fa-file-code"
            :class              = "[{ 'pulse': newLog }]"
            style               = "margin-right: 5px;"
            @click.stop.prevent = "showProcessingLog"
          ></span>
          <span
            v-disabled          = "model.results.length === 0"
            class               = "icon skin-color skin-border-color fas fa-list-alt"
            :class              = "[{ 'pulse': newResults }]"
            @click.stop.prevent = "showModelResults"
          ></span>
        </section>
        
        
      </section>
      
    </section>

  </div>
`,

  name: "modelPanel",

  components: {
    // inputs
    ...g3wsdk.gui.vue.Inputs.InputsComponents,
    prjvectorlayer_input,
    prjrasterlayer_input,
    prjvectorlayerfeature_input: prjvectorlayer_input,
    fieldchooser_input,
    // outputs
    outputvectorlayer,
    outputrasterlayer,
    outputfile,
    outputhtml: outputfile,
  },

  props: {
    model: { required: true }
  },

  data() {
    return {
      state: {
        loading:  false,
        progress: null,
        message: {
          type: 'success', // error info
          show: false
        },
        processing_html_log: null,
      },
      tovalidate: [],
      task:       null,
      newResults: false, // set true if new results are add to models
      newLog:     false, //set new process log
      valid:      false, //valid format
    }
  },

  methods: {

    //add model result to results
    addResultToModel(data = {}) {
      if (undefined === data?.result) {
        return;
      }
      const key = (new Date()).toLocaleString();

      //check if output contain already result
      const out = this.model.results.find(result => data.output.name === result.id);

      if (out) {
        out.urls.push({ key, value: data.result[data.output.name] });
      } else {
        this.model.results.push({
          id:    data.output.name,
          label: data.output.label,
          urls:  [{ key, value: data.result[data.output.name] }]
        })
      }

      this.newResults = true; // set new result to true
    },

    /**
     * Register by every inputs change of other input with dependence
     */
    registerChangeInputEvent({ inputName, handler } = {}) {
      if (!this.subscribers[inputName]) {
        this.subscribers[inputName] = [];
      }
      this.subscribers[inputName].push(handler);
    },
    /***
     * Clear run state from already run model
     */
    clearState() {
      //clear state
      this.state.message.show = false;
      this.state.progress     = null;
    },

    /**
     * Method to handle change input
     */
    async validate(input) {
      this.clearState();
      // wait DOM changes 
      await this.$nextTick();

      this.subscribers?.[input.name]?.forEach?.(h => h(input.value));

      const MUTUALLY          = input && input.validate.mutually;
      const MIN_MAX           = !MUTUALLY && input && (!input.validate.empty && (input.validate.min_field || input.validate.max_field));
      const MUTUALLY_OPTIONAL = MUTUALLY && !input.validate.required;
      const NOT_EMPTY         = [];

      // check mutually
      if (MUTUALLY_OPTIONAL && !input.validate.empty) {
        input.validate._valid         = input.validate.valid;
        input.validate.mutually_valid = input.validate.mutually.every(inputname => previous && this.tovalidate[inputname].validate.empty);
        input.validate.valid          = input.validate.mutually_valid && input.validate.valid;
      }
      
      if (MUTUALLY_OPTIONAL && input.validate.empty) {
        input.value                   = null;
        input.validate._valid         = true;
        input.validate.mutually_valid = true;
        input.validate.valid          = true;
      }

      if (MUTUALLY_OPTIONAL && input.validate.empty) {
        for (let i = input.validate.mutually.length; i--;) {
          const name = input.validate.mutually[i];
          if (!this.tovalidate[name].validate.empty) {
            NOT_EMPTY.push(name);
          }
        }
      }

      if (MUTUALLY_OPTIONAL && input.validate.empty && NOT_EMPTY.length < 2) {
        NOT_EMPTY.forEach(name => {
          this.tovalidate[name].validate.mutually_valid = true;
          this.tovalidate[name].validate.valid          = true;
          setTimeout(() => {
            this.tovalidate[name].validate.valid = this.tovalidate[name].validate._valid;
            this.state.valid = this.state.valid && this.tovalidate[name].validate.valid;
          })
        })
      }

      // check if min_field or max_field is set
      if (MIN_MAX) {
        input.validate.valid = input.validate.min_field
          ? this.tovalidate[input.validate.min_field].validate.empty || 1*input.value > 1*this.tovalidate[input.validate.min_field].value
          : this.tovalidate[input.validate.max_field].validate.empty || 1*input.value < 1*this.tovalidate[input.validate.max_field].value;
      }

      if (MIN_MAX && input.validate.valid) {
        const input_name = input.validate.min_field || input.validate.max_field;
        this.tovalidate[input_name].validate.valid = true
      }

      this.valid = Object.values(this.tovalidate).every(input => input.validate.valid);
    },

    /**
     * Run model method
     */
    async run() {
      this.state.loading             = true;
      this.state.message.show        = false;
      this.state.progress            = null; 
      this.state.processing_html_log = null;
      await this.$nextTick();
      try {
        const qprocessing = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');

        //Run task
        this.task = await (new Promise(async (resolve, reject) => {
          //create inputs parmeters
          const inputs = {};

          //Loop through input model
          for (const input of this.model.inputs) {
            if (input.value) {
              if (
                (['prjvectorlayer', 'prjvectorlayerfeature'].includes(input.input.type)) &&
                input.value.startsWith(`__g3w__external__:`)
              ) {
                //extract layer id form input.value
                const [, layerExternalId] = input.value.split(`__g3w__external__:`);
                //get external layer from catalog service
                const { crs, name }       = GUI.getService('catalog').getExternalLayers({ type: 'vector' }).find(l => layerExternalId === l.id);
                //create a geojson file from freatures
                const file    = qprocessing.createGeoJSONFile({
                  name,
                  crs,
                  features: GUI.getService('map').getLayerById(layerExternalId).getSource().getFeatures(),
                });
                //upload file to server
                try {
                  //change input value value from new value
                  input.value = (await qprocessing.uploadFile({ modelId: this.model.id, inputName: input.name, file, showUserMessage: false }))?.value;
                } catch(e) {
                  console.warn(e);
                  reject(r);
                }
              }
              inputs[input.name] = input.value;
            }
          }

          const data = {
            inputs,
            outputs: this.model.outputs.reduce((a, output) => {
              if (output.value) {
                a[output.name] = output.value;
              }
              return a;
            }, {})
          }

          const url = `${qprocessing.config.urls.run}${this.model.id}/${qprocessing.getProject().getId()}/` // url model

          //Check if configured in async mode
          if (qprocessing.config.async) {
            let time;
            // start to run Task
            qprocessing.runTask({
              url,
              params: { data: JSON.stringify(data) },    // request params
              listener: ({ task_id, response }) => {     // handle task request

                // complete → stop current task
                if ('complete' === response.status) {
                  qprocessing.stopTask(task_id);
                  this.state.progress = response.progress;
                  time = null;
                  this.state.processing_html_log = response?.processing_html_log;
                  this.newLog = !!this.state.processing_html_log;
                  _handleCompleteModelResponse(response, { resolve, reject })
                }

                if ('executing' === response.status) {
                  if ([null, undefined].includes(this.state.progress) || response.progress > this.state.progress) {
                    time = Date.now();
                  } else if ((Date.now() - time) > 600000) {
                    qprocessing.stopTask(task_id);
                    GUI.showUserMessage({
                      type:     'warning',
                      message:  'Timeout',
                      autoclose: true
                    });
                    this.state.progress = null;
                    time           = null;
                    reject({ timeout: true });
                  }
                  this.state.progress = response.progress;
                }

                if (!['complete', 'executing'].includes(response.status) && _handleErrorModelResponse(response, { reject })) {
                  this.state.progress = null;
                  time           = null;
                  qprocessing.stopTask(task_id);
                }
              },
            })
          } else { //get result directly
            fetch(url, {
              method: 'POST',
              body:   JSON.stringify(data),
              headers: {
                "Content-Type": 'application/json'
              }
            })
              .then(async res => {
                if (200 != res.status) {
                  throw res;
                }
                res = await res.json(); //get json value format
                this.state.processing_html_log = res?.processing_html_log;
                this.newLog = !!this.state.processing_html_log;
                _handleCompleteModelResponse(res, { resolve, reject });
                
              })
              .catch(res => _handleErrorModelResponse(res, { reject }) )
          }
        }));
        this.state.message.type = 'success';
      } catch(e) {
        console.warn(e);
        this.state.message.type = 'error';
      }
      this.state.loading      = false;
      this.state.message.show = true;
    },

    showProcessingLog() {
      this.newLog = false;
      const dialog = Object.assign(document.createElement('template'), {
      innerHTML: /* html */ `
        <dialog  style = "width: 50vw;">
          <section style = "overflow: auto;">
            ${ this.state.processing_html_log }
          </section>
          
          <footer style = "border-top: 1px solid #eee; margin-top: 10px; display: flex; justify-content: flex-end; width: 100%">
            <button
              type   = "button"
              class  = "btn btn-secondary"
              style  = "margin-top: 5px;"
            >${t('close')}</button>
          </footer>
        </dialog>
      `.trim()
      }).content.firstChild;
      document.querySelector('.content-wrapper').insertAdjacentElement('afterbegin', dialog);
      dialog.showModal();

      // close dialog on x icon
      dialog.querySelector('button').addEventListener('click', () => {
        dialog.close();
        dialog.remove();
      });
    },


    /**
     * Show Model results Panel
     */
    async showModelResults() {
      const ModelResults = (await import('./ModelResults.js')).default;

      new Panel({
        id: `qprocessing-panel-results`,
        title: `${this.model.display_name.toUpperCase()}`,
        internalPanel: new (Vue.extend(ModelResults))({
          propsData: {
            model: this.model,
          }
        }),
        show: true,
      });
      this.newResults         = false;
      this.state.message.show = false;
    },

    addToValidate(input) {
      this.tovalidate.push(input);
    },

  },

  created() {
    this.tovalidate = [];
    // object contains subscribers of change parent input
    this.subscribers = {};
  },

  async mounted() {
    await this.$nextTick();
    //@TODO
    $('.qprocessing-model-inputs input')
      .keypress((event) => {
        if (event.which === 13) {
          event.preventDefault();
        }
    });
  },

  destroyed() {
    this.tovalidate = null;
  },

});

/**
 * Handle Async or Sync response error
 */
function _handleErrorModelResponse(response, { reject }) {
  const { status, exception } = response;
  let statusError             = false;
  let textMessage             = false;
  let message;

  switch(status) {
    case '500':
    case 500:
      message = (
        response.responseJSON ?
        (response.responseJSON.exception || response.responseJSON.error.message) :
        'server_error'
      );
      textMessage = undefined !== exception;
      statusError = true;
      break;
    case 408:
      message     = "TIMEOUT";
      statusError = true;   
    case 502:
      message = (
        response.responseJSON ?
        (response.responseJSON.exception || response.responseJSON.error.message) :
        'server_error'
      );
      textMessage = undefined !== exception;
      statusError = true;
      break;  
    case 'error':
      message = exception;
      textMessage = true;
      statusError = true;
      break;
    default:
      message = 'server_error';
      statusError = true;

  }

  // in case of status error
  if (statusError) {
    //show a user message with error
    GUI.showUserMessage({
      type: 'alert',
      message,
      textMessage,
    });

    reject({
      statusError: true,
      timeout:     false
    })
  }

  return statusError;
}

/**
 * TO handle complete task ot sync request model
 * @since v3.7.0
 * @param response server response
 * @param resolve resolve method of a Promise
 * @param reject reject method of a Promise
 */
function _handleCompleteModelResponse(response, { resolve, reject }) {
  let { result, task_result, data } = response;
  //case sync request model return data instead of task_result
  if (data) { task_result = data; }
  //in case of task_result null
  if (null === task_result || false === result) { reject({}); } 
  else { resolve({ result, task_result }); }
}

document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
  <style>
    .qprocessing-model                                                   { padding-bottom: 10px; }
    .qprocessing-model-header                                            { font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }
    .qprocessing-model .title                                            { font-weight: bold; margin-bottom: 5px; }
    .qprocessing-model > section > .title                                { border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .qprocessing-model > section.qprocessing-model-results               { border-top: 2px solid #eee; padding-top: 5px; }
    .qprocessing-model-results                                           { margin-top: 10px; }
    .qprocessing-model-results .icon                                     { cursor: pointer; border: 2px solid transparent; margin-bottom: 8px; padding: 3px; border-radius: 5px; }
    .qprocessing-model-results .icon.pulse                               { transform: scale(1); animation: pulse 2s infinite; }
    .qprocess-model-footer button.run                                    { width: 100%; }
    .qprocessing-model-inputs, .qprocessing-model-note                   { margin-bottom: 5px; }
    :is(.qprocessing-model-inputs, .qprocessing-model-outputs) .g3w-form { background-color: transparent !important; padding: 10px; }
    .qprocess-model-footer .message                                      { font-weight: bold; }
    @keyframes pulse {
      0% { transform: scale(0.75); }
      70% { transform: scale(1); }
      100% { transform: scale(0.75); }
    }
  </style>`,
);