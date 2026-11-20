Feature: Processing API
  Background:
    Given a processing project and an authenticated administrator

  Scenario Outline: Filter project fields by datatype
    When fields are requested for datatype "<datatype>"
    Then the response contains the <fields> fields

    Examples:
      | datatype | fields   |
      | omitted  | all      |
      | any      | all      |
      | string   | string   |
      | numeric  | numeric  |
      | datetime | datetime |

  Scenario Outline: Reject invalid field requests
    When fields are requested for <request>
    Then the response has status <status> and the expected error

    Examples:
      | request          | status |
      | a missing layer  | 500    |
      | an empty datatype | 400   |
      | an unknown datatype | 400 |

  Scenario Outline: Run processing models and download results
    Given model execution is <mode>
    When the buffer, point-in-polygon and selected-feature models run
    Then their downloaded results have the expected geometries and attributes

    Examples:
      | mode         |
      | synchronous  |
      | asynchronous |

  Scenario: Running a model requires permissions
    When a viewer tries to run the buffer model
    Then the request is forbidden
    When the viewer receives project and model permissions
    Then the viewer can run the buffer model

  Scenario Outline: Report asynchronous task progress
    Given task progress is represented by <representation>
    When task progress is requested
    Then the reported progress is <progress>

    Examples:
      | representation | progress |
      | count          | 25       |
      | tuple          | 25       |
      | missing        | 0        |

  Scenario Outline: Upload supported vector inputs
    When a <geometry> input is uploaded
    Then the input is stored successfully

    Examples:
      | geometry |
      | point    |
      | polygon  |
      | shapefile |

  Scenario Outline: Reject invalid vector inputs
    When a <geometry> input is uploaded
    Then the upload is rejected with the expected error

    Examples:
      | geometry           |
      | line               |
      | incomplete shapefile |
