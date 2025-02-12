export default ({

  // language=html
  template: /* html */ `
  <div
    class = "qprocessing-upload-vector-file"
    style = "flex-grow: 2"
  >
    <section class="upload-file-content">
      <form
        class                  = "addlayer skin-border-color"
        v-t-tooltip:top.create = "'mapcontrols.add_layer_control.drag_layer'"
      >
        <input
          ref     = "file"
          type    = "file"
          title   = " "
          @change = "$emit('add-layer', { file: $refs.file.files[0], type: 'upload' })"
          accept = ".zip,.geojson,.GEOJSON,.kml,.kmz,.KMZ,.KML,.json,.gpx,.gml,.csv"
        />
        <div class="drag_and_drop">
          <i :class="g3wtemplate.getFontClass('cloud-upload')" class="fa-2x" aria-hidden="true"></i>
        </div>
      </form>
    </section>
  </div>`,

  name: "UploadVectorFile",
  props: {
    upload: {
      type: Boolean,
    }
  },
  data() {
    return {
      layer: {
        name: null,
        id: null
      }
    }
  },
})


document.head.insertAdjacentHTML(
  'beforeend',
  /* css */`
<style>
  .qprocessing-upload-vector-file form.addlayer   { position: relative; border: 2px dashed; text-align: center; border-radius: 3px; }
  .qprocessing-upload-vector-file .addlayer input { position: absolute; margin: 0; padding: 0; width: 100%; height: 100%; outline: 0; opacity: 0; cursor: pointer; display: block; }
  .qprocessing-upload-vector-file .drag_and_drop  { line-height: 20px; padding: 5px; color: #fff; }
</style>`,
);