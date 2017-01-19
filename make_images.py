'''
Convert set of 3 fits files into a single band images and an rgb false color image
call as:
    python make_images {path to files} {common name of files}
example:
    python make_images './M110' 'M110_dE'
'''
import sys
import numpy as np
from astropy.visualization import stretch, interval
from astropy.io import fits
from reproject import reproject_interp
from matplotlib import pyplot as plt

# file path vars
path = sys.argv[1]
name = sys.argv[2]
base = '{0}/{1}'.format(path, name)


def logScaleImage(image, return_full=False):
    reagon = interval.AsymmetricPercentileInterval(10., 99.95)
    vmin, vmax = reagon.get_limits(image)
    a = vmax/vmin - 1
    scale = stretch.LogStretch(a=a)
    image_scaled = (scale + reagon)(image)
    return image_scaled


def removeNaN(data):
    bdx = ~np.isfinite(data)
    data[bdx] = 0

hdu_b = fits.open('{0}_b.fits'.format(base))
image_b_scaled = logScaleImage(hdu_b[0].data)
plt.imsave('{0}_b.png'.format(base), image_b_scaled, cmap='Greys_r', origin='lower')

hdu_r = fits.open('{0}_r.fits'.format(base))
image_r, footprint_r = reproject_interp(hdu_r[0], hdu_b[0].header)
image_r_scaled = logScaleImage(image_r)
removeNaN(image_r_scaled)
plt.imsave('{0}_r.png'.format(base), image_r_scaled, cmap='Greys_r', origin='lower')

hdu_ir = fits.open('{0}_ir.fits'.format(base))
image_ir, footprint_ir = reproject_interp(hdu_ir[0], hdu_b[0].header)
image_ir_scaled = logScaleImage(image_ir)
removeNaN(image_ir_scaled)
plt.imsave('{0}_ir.png'.format(base), image_ir_scaled, cmap='Greys_r', origin='lower')

RGB_image = np.zeros([image_b_scaled.shape[0], image_b_scaled.shape[1], 3])
RGB_image[:, :, 0] = image_ir_scaled
RGB_image[:, :, 1] = image_r_scaled
RGB_image[:, :, 2] = image_b_scaled
plt.imsave('{0}_rgb.png'.format(base), RGB_image, origin='lower')
