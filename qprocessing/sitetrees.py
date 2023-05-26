from sitetree.utils import item
from core.utils.tree import G3Wtree

# Be sure you defined `sitetrees` in your module.
sitetrees = (
  # Define a tree with `tree` function.
    G3Wtree('qprocessing', title='QProcessing', module='qprocessing', items=[
      # Then define items and their children with `item` function.
      item('PROCESSING', '#', type_header=True),
      item('Modelli', 'qprocessing-project-list', icon_css_class='fa fa-list', children=[
        item('Aggiungi modello', 'qprocessing-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qprocessing.add_qprocessingproject']),
        item('Lista Modelli', 'qprocessing-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
        item('Agg. Modello {{ object.pk }}', 'qprocessing-project-update object.pk', url_as_pattern=True,
               icon_css_class='fa fa-edit', in_menu=False),
      ])
    ]),

    G3Wtree('qprocessing_en', title='QProcessing', module='qprocessing', items=[
      # Then define items and their children with `item` function.
      item('PROCESSING', '#', type_header=True),
      item('Models', 'qprocessing-project-list', icon_css_class='fa fa-list', children=[
          item('Add model', 'qprocessing-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qprocessing.add_qprocessingproject']),
          item('Models list', 'qprocessing-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
      ])
    ]),


)

