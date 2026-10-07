const GUI                 = g3w.app;
const _                   = g3w.gettext;
export default ({

  // language=html
  template: /* html */ `
  <div
    class                   = "qprocessing-draw-vector-features"
    style                   = "font-size: 1.3em;"
    
  >
    <button
      class               = "btn skin-background-color"
      style               = "height: 100%; margin-right: 0 !important;"
      @click.stop.prevent = "toggled = !toggled"
      v-t-tooltip:top.create  = "'plugins.qprocessing.inputs.drawfeatures'"
    >
      <i class = "fas fa-pencil-alt"></i>
    </button>
  </div>
  `,

  name: "DrawInputVectorFeatures",

  props: {
    datatypes: { type: Array, default: [] }, // array of datatypes from input
    upload:    { type: Boolean }             // Boolean when file is upload ot not
  },

  data() {
    return {
      toggled: false, //draw button toggled
      drawTool: {
        loading:  this.upload,
        disabled: true
      }
    }
  },

  methods: {

    /**
     * handle draw interaction flow
     */
    setDrawInteraction(type = this.drawGeometryTypes[0]){
      GUI.disableClickMapControls(true);                                          // avoid click conflicts
      this.drawLayer.getSource().clear();                                                           // clear previous features
      GUI.removeInteraction(this.drawInteraction);                       // remove previous draw interaction
      this.drawInteraction = new ol.interaction.Draw({ type, source: this.drawLayer.getSource() }); // create draw interaction
      this.drawInteraction.on('drawend', () => this.drawTool.disabled = false);                     // enable upload button on drawend 
      GUI.addInteraction(this.drawInteraction);                          // add interaction to Map
    },

    clear() {
      this.drawLayer.getSource().clear();
      GUI.disableClickMapControls(false);
      GUI.removeInteraction(this.drawInteraction);
      GUI.closeUserMessage();
    },

  },

  watch: {

    //listen toggled button
    toggled(bool) {
      if (!bool) {
        this.clear();
        this.$emit('toggled-tool', !bool);
        return;
      }
      //set start interaction
      this.setDrawInteraction();
      //whow tool component
      GUI.showUserMessage({
        title:    'plugins.qprocessing.inputs.drawfeatures', //@TODO add translation title
        type:     'tool',
        size:     'small',
        closable: false,
        hooks: {
          body: {
            template: /* html */`
              <div style = "width: 100%; padding: 5px;" v-disabled = "state.loading">
                <x-select
                  :value  = "type"
                  ref     = "select"
                  @change = "type = $event.target.value"
                  style   = "width: 100%">
                  <x-option
                    v-for      = "type in types"
                    :key       = "type"
                    :value     = "type"
                    v-t-plugin = "'qprocessing.draw_types.'+type"
                  ></x-option>
                </x-select>

                <div v-if = "state.loading" class = "bar-loader"></div>

                <button
                  v-disabled          = "state.disabled"
                  class               = "btn skin-background-color"
                  @click.stop.prevent = "uploadLayer(type)"
                  style               = "margin: 3px; width: 100%"
                >
                  <i class = "fas fa-cloud-upload-alt"></i>
                </button>

              </div>`,
            data: () => {
              return {
                state: this.drawTool,
                types: this.drawGeometryTypes,
                type:  this.drawGeometryTypes[0]
              };
            },
            watch: {

              /**
               * @listens type change of drawed geometry
               * @fires   change-draw-type
               */
              'type': type => this.setDrawInteraction(type),

            },
            methods: {
              uploadLayer: async (type) => {
                const qprocessing = GUI.getPlugin('qprocessing');
                const features    = this.drawLayer.getSource().getFeatures();
                await this.$nextTick();
                //emit event
                this.$emit('add-layer', {
                  file: qprocessing.createGeoJSONFile({
                    features,
                    name: `${_('plugins.qprocessing.draw_filename')}(${_('plugins.qprocessing.draw_types.' + type)})`
                  }),
                  features,
                  type: 'draw'
                });
              }
            },
          }
        }
      });
      this.$emit('toggled-tool', !bool);
    },

    upload(bool) {
      //listen upload status. Boolean
      this.drawTool.loading  = bool;
      this.drawTool.disabled = !bool;
      if (!bool) {
        this.clear();
        this.toggled = bool;
      }
    },

  },

  created() {
    //set geometries type
    this.drawGeometryTypes = Object.entries({
      point:   'Point',
      line:    'LineString',
      polygon: 'Polygon'
    }).reduce((a, [ type, olGeometry ]) => {
      if (this.datatypes.find(dt => 'anygeometry' === dt)){
        a.push(olGeometry);
      } else {
        this.datatypes.find(dt => type === dt) && a.push(olGeometry)
      }
      return a;
    }, []);

    this.drawInteraction = null;
    this.drawLayer       = new ol.layer.Vector({ source: new ol.source.Vector() });
    GUI.getMap().addLayer(this.drawLayer);
  },

  beforeDestroy() {
    this.clear();
    GUI.getMap().removeLayer(this.drawLayer);
    this.drawLayer       = null;
    this.drawInteraction = null;
  },

});