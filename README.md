[![DOI](https://zenodo.org/badge/79459697.svg)](https://zenodo.org/badge/latestdoi/79459697)

# 3D-Printed-Galaxy-Software
The software created and used for the Tactile Universe


## Make images
`make_images.py`: A python script that converts set of 3 `.fits` files into a single band images and an rgb false color image.  The single band images can be used as height maps to create the 3D models.  This script makes use of [Astropy](http://www.astropy.org/), [reproject](https://reproject.readthedocs.io/en/stable/), [NumPy](http://www.numpy.org/), and [Matplotlib](http://matplotlib.org/).

## Tactile Universe plugin
`tactile_universe_plugin.zip`: A [Blender](https://www.blender.org/) plugin containing all the functions needed to create tactile universe models in blender.

## Command line install script
`install_all_addons.py`: A script for installing and activating all of the plugins needed to make Tactile Universe models (useful if the Blender UI is too difficult to use).

```bash
blender -b --python install_all_addons.py
```

## M51 image
`M51_i.png`: The SDSS i-band image of the galaxy M51. This image can be used for testing out the plugin and command line tools.

## Make model
`make_model.py`: A blender script for automating the model making process via the command line.  To learn how to run blender via the command line see the [Blender documentation](https://docs.blender.org/manual/en/dev/render/workflows/command_line.html).  Once set up this script can be used as follows

```bash
blender TU_startup.blend --python-exit-code 1 --python make_model.py -- example_model_config.json
```

### Base file
`TU_startup.blend`: The base blender file used for scripting (make sure units are set to mm and no other objects are in the scene).

### Configuration
`example_model_config.json`: A file containing the configuration parameters to run `make_model.py`.  This example file contains the maximum number of parameters that can be configured.

 - `input_file_path`: Full path to the image file (if no path is specified it assumes the image is the the same directory the script is called from)
 - `plane_height`: Height in `mm` of the resulting model
 - `emboss_plane_keywords`: The keywords to be passed into the `emboss_plane` plugin, any that are not specified will use their default values (the example file lists all keywords with their default values)
 - `stl_keywords`: The keywords passed into the `stl` export function, any that are not specified will use default values.
 - `output_path`: Full path to the folder the output files will be saved to (if not specified it will use the directory the script is called from).
 - `output_name`: The name to used for the `.blend` and `.stl` files created by the script.

## Make holder
`make_holder.py`: A blender script for automating the holder making process via the command line.  Once set up this script can be used as follows

```bash
blender TU_startup.blend --python-exit-code 1 --python make_holder.py -- example_holder_config.json
```

### Configuration
`example_holder_config.json`: A file containing the configuration parameters to run `make_holder.py`.  This example file contains the maximum number of parameters that can be configured.

 - `holder_keywords`: The keywords to be passed into the `holder` plugin, any that are not specified will use their default values
 - `output_path`: Full path to the folder the output files will be saved to (if not specified it will use the directory the script is called from).
 - `output_name`: The name to used for the `.blend` and `.stl` files created by the script.


