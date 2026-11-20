Feature: Processing models
  Scenario: Run a buffer model directly with QGIS
    Given the buffer model and its QGIS project
    When the buffer model runs
    Then QGIS returns the expected buffer result

  Scenario: Describe a processing model
    Given the buffer model
    When its inputs and outputs are described
    Then the description contains the expected inputs and output formats

  Scenario: Raster and vector outputs offer their respective formats
    Given distinct raster and vector output formats
    When raster and vector model outputs are described
    Then each output offers its configured formats

  Scenario: Use a project raster as processing input
    Given a valid raster layer in a QGIS project
    When the raster layer is selected for processing
    Then QGIS resolves the selected raster layer

  Scenario Outline: Reject an invalid project raster input
    Given a valid raster layer in a QGIS project
    When a <layer> layer is selected for raster processing
    Then the raster input is rejected

    Examples:
      | layer   |
      | missing |
      | vector  |
