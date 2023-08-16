# G3W-ADMIN-QPROCESSING v1.0.1-beta.0

A G3W-ADMIN module to use processing features fo QGIS application inside G3W-SUITE framework.
Is possible upload a QGIS processing model file `.model3` inside G3W-ADMIN to get the Processing form available 
on G3W-CLIENT.

![QGIS desktop](doc/images/qgis.png)
![G3W-SUITE](doc/images/g3w-suite.png)

## QGIS processing features

At the moment the follow inputs and outputs feature of QGIS processing are supported:

#### Inputs

- VectorLayer (*QgsProcessingParameterVectorLayer*)
- VectorFeatures (*QgsProcessingParameterFeatureSource*)
- VectorField (*QgsProcessingParameterField*)
- RasterLayer (*QgsProcessingParameterRasterLayer*)
- Distance (*QgsProcessingParameterDistance*) 
- DateTime (*QgsProcessingParameterDateTime*) 
- Boolean (*QgsProcessingParameterBoolean*)
- Range (*QgsProcessingParameterRange*) 
- Number (*QgsProcessingParameterNumber*) 
- Extent (*QgsProcessingParameterExtent*)

#### Outputs

- VectorLayer (*QgsProcessingOutputVectorLayer*)
- RasterLayer (*QgsProcessingOutputRasterLayer*)



## Installation

Install *qprocessing* module into [`g3w-admin`](https://github.com/g3w-suite/g3w-admin/tree/v.3.6.x/g3w-admin) applications folder:

```sh
# Install module from github (v1.0.0)
pip3 install git+https://github.com/g3w-suite/g3w-admin-processing.git@v1.0.0

# Install module from github (dev branch)
# pip3 install git+https://github.com/g3w-suite/g3w-admin-processing.git@master

# Install module from local folder (git development)
# pip3 install -e /g3w-admin/plugins/processing

# Install module from PyPi (not yet available)
# pip3 install g3w-admin-authjwt
```

Enable `'qprocessing'` module adding it to `G3W_LOCAL_MORE_APPS` list:

```py
# local_settings.py

G3WADMIN_LOCAL_MORE_APPS = [
    ...
    'qprocessing'
    ...
]
```

### Huey configuration
To make `QProcessing` work in asynchronous mode (in batch mode) you need to configure Huey and have a message broker such as `Redis`. Here is an example Huey configuration using Redis as a message broker:

```python
HUEY = {
    # Huey implementation to use.
    'huey_class': 'huey.RedisExpireHuey',
    'name': 'g3w-suite',
    'url': 'redis://localhost:6379/?db=0',
    'immediate': False,  # If True, run synchronously.
    'consumer': {
        'workers': 1,
        'worker_type': 'process',
    },
}
```

To run Huey:
```
python3 manage.py tun_huey -k process
```

### Docker

Refer to [g3w-suite-docker](https://github.com/g3w-suite/g3w-suite-docker) repository for more info about running this on a docker instance.

**NB** On Ubuntu Jammy you could get an `UNKNOWN` package install instead of `g3w-admin-processing`, you can retry installing it as follows to fix it:

```sh
# Fix: https://github.com/pypa/setuptools/issues/3269#issuecomment-1254507377
export DEB_PYTHON_INSTALL_LAYOUT=deb_system

# And then install again the module
pip3 install ...
```