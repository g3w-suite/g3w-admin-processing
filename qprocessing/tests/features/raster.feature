Feature: Project raster selector
  Scenario: List raster layers without vector, base or excluded layers
    Given project layers from raster and vector providers
    When the raster selector is initialized
    Then only eligible raster layers are listed
    And the first raster layer is selected
