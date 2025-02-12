export default {
  title: 'Geoprocessing',
  inputs: {
    prjvectorlayerfeature: {
      selected_features: "Solo features selezionate",
    },
    fieldchooser: {
      validate: {
        message: {
          multiple: "Seleziona almeno un campo",
          single: "Seleziona un campo"
        }
      }
    }
  },
  outputs: {
    outputvector: {
      open_file_on_map: "Apri il file sulla mappa"
    }
  },
  run :{
    messages: {
      success: "Modello eseguito con successo",
      error: "Errore durante l'esecuzione del modello"
    }
  },
  draw_types: {
    'Polygon': "Poligono",
    'LineString': "Linea",
    'Point': "Punto",
  },
  draw_filename: 'Layer disegnato',
}