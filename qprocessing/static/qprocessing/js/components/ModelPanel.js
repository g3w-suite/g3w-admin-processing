import prjvectorlayer_input from '../components/InputPrjVectorLayer.js';
import prjrasterlayer_input from '../components/InputPrjRasterLayer.js';
import fieldchooser_input   from '../components/InputFieldChooser.js';
import outputvectorlayer from '../components/OutputVectorLayer.js';
import outputrasterlayer from '../components/OutputRasterLayer.js';
import outputfile        from '../components/OutputFile.js';

const { Panel }            = g3wsdk.gui;
const { formInputsMixins } = g3wsdk.gui.vue.Mixins;
const { XHR }              = g3wsdk.core.utils;
const { ProjectsRegistry } = g3wsdk.core.project;
const { TaskService }      = g3wsdk.core.task;
const { GUI }              = g3wsdk.gui;

export default ({

  // language=html
  template: /* html */ `
  <div class="qprocessing-model">

    <section class="qprocessing-model-header">
      <div class="skin-color">{{model.display_name.toUpperCase()}}</div>
    </section>

    <!-- INPUTS   -->
    <section class="qprocessing-model-inputs">
      <div class="title" >INPUTS</div>
      <divider/>
      <form class="form-horizontal g3w-form">
        <div class="box-primary">
          <div class="box-body">
            <component
              v-for                  = "input in model.inputs"
              :key                   = "input.name"
              :modelId               = "model.id"
              @register-change-input = "registerChangeInputEvent"
              @addinput              = "addToValidate"
              @changeinput           = "_changeInput(input)"
              :state                 = "input"
              :is                    = "input.input.type + '_input'"
            />
          </div>
        </div>
      </form>

    </section>

    <!-- OUTPUTS   -->
    <section class="qprocessing-model-outputs">
      <div class="title">OUTPUTS</div>
      <divider/>
      <form class="form-horizontal g3w-form">
          <div class="box-primary">
            <div class="box-body">
              <component
                v-for                        = "output in model.outputs"
                :key                         = "output.name"
                @add-result-to-model-results = "addResultToModel"
                :state                       = "output"
                :task                        = "task"
                :is                          = "output.input.type + ''"
              />
            </div>
          </div>
        </form>
    </section>

    <!-- MODEL RESULTS   -->
    <section class="qprocessing-model-results">
      <section style="display: flex; justify-content: space-between; align-items: center">
        <div class="title">RESULTS</div>
        <span
          v-disabled          = "model.results.length === 0"
          class               = "icon skin-color skin-border-color"
          :class              = "[ g3wtemplate.getFontClass('list'), {'pulse': newResults}]"
          @click.stop.prevent = "showModelResults">
        </span>
      </section>
      <divider/>
    </section>

    <!-- FOOTER -->
    <section class="qprocess-model-footer">
      <div>
        <progressbar v-if="state.progress" :progress="state.progress" />
        <bar-loader v-else :loading="state.loading" />
        <button
          class       = "btn skin-background-color run"
          @click.stop = "run"
          :disabled   = "!valid || state.loading">
          <i :class="g3wtemplate.font['run']"></i>
        </button>
        <div v-if="state.message.show">
         <span
          class       ="message"
          :style      = "{color: getMessageColor()}"
           v-t-plugin = "'qprocessing.run.messages.'+ state.message.type"
          ></span>
        </div>
      </div>
    </section>

  </div>
`,

  name: "modelPanel",
  mixins: [formInputsMixins],
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
    model: {
      required: true
    }
  },
  data(){
    return {
      state: {
        loading: false,
        progress: null,
        message: {
          type: 'success', // error info
          show: false
        }
      },
      tovalidate: [],
      task: null,
      newResults: false, // set true if new results are add to models
    }
  },
  methods: {
    //add model result to results
    addResultToModel(data={}) {
      const {output, result} = data;
      if (undefined !== result) {
        const id = output.name;
         //check if output contain already result
        const findResultOutput = this.model.results.find(result => result.id === id);
        if (findResultOutput) {
          findResultOutput.urls.push(result[output.name])
        } else {
          this.model.results.push({
            id: output.name,
            label: output.label,
            urls: [result[output.name]]
          })
        }
        this.newResults = true; // set new result to true
      }
    },
    //return message color
    getMessageColor() {
      switch(this.state.message.type){
        case 'success':
          return 'green';
        case 'error':
          return 'red';
      }
    },

    /**
     * Method to register by every inputs change of other input with dependence
      * @param inputName
     * @param handler
     */
    registerChangeInputEvent({inputName, handler}={}) {

      if (undefined === this.subscribe_change_input[inputName]) {
        this.subscribe_change_input[inputName] = []
      }

      this.subscribe_change_input[inputName].push(handler)
    },
    /**
     * Method to handle change input
     * @param input
     */
    async _changeInput(input) {
      //need to wait change value dom
      await this.$nextTick();
      if (Array.isArray(this.subscribe_change_input[input.name])) {
        this.subscribe_change_input[input.name].forEach(handler => handler(input.value))
      }
      //call base changeInput method
      this.changeInput(input);
    },
    /**
     * Run model method
     * @returns {Promise<void>}
     */
    async run() {
      this.state.loading = true;
      this.state.message.show = false;
      await this.$nextTick();
      try {
        //Run task
        this.task = await this.runModel({
          model: this.model,
          state: this.state
        });
        this.state.message.type = 'success';
      } catch(err) {
        this.state.message.type = 'error';
      }

      this.state.loading = false;
      this.state.message.show = true;
    },

  /**
   * Method to run model
   * @param model
   * @param state
   * @returns {Promise<unknown>}
   */
    runModel({ model, state } = {}) {
      const qprocessing = g3wsdk.core.plugin.PluginsRegistry.getPlugin('qprocessing');

      return new Promise(async (resolve, reject) => {
        let timeoutprogressintervall;
        /**
         * listener method to handle task request
         * @param task_id
         * @param timeout
         * @param response
         */
        const listener = ({task_id, timeout, response}) => {
          const {progress, status} = response;
          // in case of complete
          if (status === 'complete') {
            //stop current task
            TaskService.stopTask({task_id});
            timeoutprogressintervall = null;
            _handleCompleteModelResponse(response, { resolve, reject })
          } else if (status === 'executing') {
            if (state.progress === null || state.progress === undefined) {
              timeoutprogressintervall = Date.now();
            } else {
              if (progress > state.progress) {
                timeoutprogressintervall = Date.now();
              } else {
                if ((Date.now() - timeoutprogressintervall) > 600000){
                  TaskService.stopTask({task_id});
                  GUI.showUserMessage({
                    type: 'warning',
                    message: 'Timeout',
                    autoclose: true
                  });
                  state.progress = null;
                  timeoutprogressintervall = null;
                  reject({
                    timeout: true
                  })
                }
              }
            }
            state.progress = progress;
          }
          else {
            const statusError = _handleErrorModelResponse(response, {
              reject,
            });

            if (statusError) {
              state.progress = null;
              timeoutprogressintervall = null;

              //stop task
              TaskService.stopTask({task_id});
            }
          }
        };

        //create inputs parmeters
        const inputs = {};

        //Loop through input model
        for (const input of model.inputs) {
          if (input.value) {
            if (
              (input.input.type === 'prjvectorlayer') &&
              input.value.startsWith(`__g3w__external__:`)
            ) {
              //extract layer id form input.value
              const [,layerExternalId] = input.value.split(`__g3w__external__:`);
              //get external layer from catalog service
              const {crs, name} = GUI.getService('catalog').getExternalLayers({type: 'vector'}).find(layer => layer.id === layerExternalId);
              //get map ol layer from map
              const OLlayer = GUI.getService('map').getLayerById(layerExternalId);
              //create a geojson file from freatures
              const file = qprocessing.createGeoJSONFile({
                name,
                features: OLlayer.getSource().getFeatures(),
                crs
              });
              //upload file to server
              try {
                const {value} = await qprocessing.uploadFile({
                  modelId: model.id,
                  inputName: input.name,
                  file
                });
                //change input value value from new value
                input.value = value;
              } catch(err) {
                //reject
                reject(err);
              }
            }
            inputs[input.name] = input.value;
          }
        }

        //create outputs paramter
        const outputs = model.outputs.reduce((accumulator, output) => {
          if (output.value) {
            accumulator[output.name] = output.value;
          }
          return accumulator;
        }, {});

        const data = {
          inputs,
          outputs,
        }

        const url = `${qprocessing.config.urls.run}${model.id}/${ProjectsRegistry.getCurrentProject().getId()}/` // url model

        //Check if configured in async mode
        if (qprocessing.config.async) {
          // start to run Task
          TaskService.runTask({
            url,
            taskUrl: qprocessing.config.urls.taskinfo, // url to ask task is end
            params: {
              data: JSON.stringify(data)
            }, // request params
            method: 'POST',
            listener
          })
        } else { //get result directly
          XHR.post({
            url,
            data: JSON.stringify(data),
            contentType: 'application/json'
          })
            .then((response)  => { _handleCompleteModelResponse(response, { resolve, reject }) })
            .catch((response) => {
              response.status = 500;
              _handleErrorModelResponse(response, { reject });
            })
        }
      })
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
      this.newResults = false;
    }
  },
  created() {
    //Object contains subscribers of change parent input
    this.subscribe_change_input = {};
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
});

/**
 * Handel Async or Sync response error
 * @param response
 * @param reject
 * @private
 */
function _handleErrorModelResponse(response, {
  reject,
}) {
  const {status, exception} = response;
  let statusError = false;
  let textMessage = false;
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
    case 'error':
      message = exception;
      textMessage = true;
      statusError = true;
      break;
  }

  // in case of status error
  if (statusError) {
    //show a user message with error
    GUI.showUserMessage({
      type: 'alert',
      message,
      textMessage
    });

    reject({
      statusError:true,
      timeout: false
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
 * @private
 */
function _handleCompleteModelResponse(response, {
  resolve,
  reject,
}) {
  let {result, task_result, data} = response;
  //case sync request model return data instead of task_result
  if (data) {
    task_result = data;
  }
  //in case of task_result null
  if (null === task_result || false === result) {
    reject({});
  } else {
    resolve({result, task_result});
  }
}

document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
<style>
  .qprocessing-model                                                   { padding-bottom: 10px; }
  .qprocessing-model-header                                            { font-size: 1.3em; font-weight: bold; }
  .qprocessing-model .title                                            { font-weight: bold; margin-bottom: 5px; }
  .qprocessing-model-results .icon                                     { cursor: pointer; border: 2px solid transparent; margin-bottom: 8px; padding: 3px; border-radius: 5px; }
  .qprocessing-model-results .icon.pulse                               { transform: scale(1); animation: pulse 2s infinite; }
  .qprocess-model-footer button.run                                    { width: 100%; }
  .qprocessing-model-inputs                                            { margin-bottom: 5px; }
  :is(.qprocessing-model-inputs, .qprocessing-model-outputs) .g3w-form { background-color: transparent !important; }
  .qprocess-model-footer                                               { margin-top: 10px; }
  .qprocess-model-footer .message                                      { font-weight: bold; }
  @keyframes pulse {
    0% { transform: scale(0.75); }
    70% { transform: scale(1); }
    100% { transform: scale(0.75); }
  }
</style>`,
);