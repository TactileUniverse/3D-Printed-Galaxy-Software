[![DOI](https://zenodo.org/badge/79459697.svg)](https://zenodo.org/badge/latestdoi/79459697)

# 3D-Printed-Galaxy-Software
The software created and used for the Tactile Universe


## Make images
`make_images.py`: A python script that converts set of 3 `.fits` files into a single band images and an rgb false color image.  The single band images can be used as height maps to create the 3D models.  This script makes use of [Astropy](http://www.astropy.org/), [reproject](https://reproject.readthedocs.io/en/stable/), [NumPy](http://www.numpy.org/), and [Matplotlib](http://matplotlib.org/).

## Emboss Plane
`emboss_plane.py`: A [Blender](https://www.blender.org/) plugin to turn a single-band black and white image into a 3D printable model.


## Make model
`make_model.py`: A blender script for automating the model making process via the command line.  To learn how to run blender via the command line see the [their documentation](https://docs.blender.org/manual/en/dev/render/workflows/command_line.html).  Once set up this script can be used as follows

```bash
blender TU_startup.blend --python-exit-code 1 --python make_model.py -- example_model_config.json
```

### Base file
`TU_startup.blend`: The base blender file used for scripting (make sure units are set to mm and no other objects are in the scene).

### Configuration
`example_model_config.json`: A file containing the configuration parameters to run `make_model.py`.  This example file contains the maximum number of parameters that can be configured.

`input_file_path`: Full path to the image file (if no path is specified it assumes the image is the the same directory the script is called from)

`plane_height`: Height in `mm` of the resulting model

`emboss_plane_keywords`: The keywords to be passed into the `emboss_plane` plugin, any that are not specified will use their default values

`filter_size`: The size of the filter (in pixels) applied to the input image, this is useful for noisy images.

`stl_keywords`: The keywords passed into the `stl` export function, any that are not specified will use default values.

`output_path`: Full path to the folder the output files will be saved to (if not specified it will use the directory the script is called from).

`output_name`: The name to used for the `.blend` and `.stl` files created by the script.


## Name Plate
`name_plate.py`: A [Blender](https://www.blender.org/) plugin to crate name plates for the models created with the Emboss Plane plugin.

## Make name plate
`make_name_plate.py`: A blender script for automating the name plate making process via the command line.  To learn how to run blender via the command line see the [their documentation](https://docs.blender.org/manual/en/dev/render/workflows/command_line.html).  Once set up this script can be used as follows

```bash
blender TU_startup.blend --python-exit-code 1 --python make_name_plate.py -- example_name_config.json
```

### Configuration
`example_name_config.json`: A file containing the configuration parameters to run `make_name_plate.py`.  This example file contains the maximum number of parameters that can be configured.

`name_plate_keywords`: The keywords to be passed into the `name_plate` plugin, any that are not specified will use their default values

`stl_keywords`: The keywords passed into the `stl` export function, any that are not specified will use default values.

`output_path`: Full path to the folder the output files will be saved to (if not specified it will use the directory the script is called from).

`output_name`: The name to used for the `.blend` and `.stl` files created by the script.
