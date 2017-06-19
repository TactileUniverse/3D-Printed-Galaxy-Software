[![DOI](https://zenodo.org/badge/79459697.svg)](https://zenodo.org/badge/latestdoi/79459697)

# 3D-Printed-Galaxy-Software
The software created and used for the Tactile Universe

`make_images.py`: A python script that converts set of 3 `.fits` files into a single band images and an rgb false color image.  The single band images can be used as height maps to create the 3D models.  This script makes use of [Astropy](http://www.astropy.org/), [reproject](https://reproject.readthedocs.io/en/stable/), [NumPy](http://www.numpy.org/), and [Matplotlib](http://matplotlib.org/).

`emboss_plane.py`: A [Blender](https://www.blender.org/) plugin to turn a single-band black and white image into a 3D printable model.
