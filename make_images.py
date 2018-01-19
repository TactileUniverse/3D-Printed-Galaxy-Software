import numpy as np
from astropy.visualization import stretch, interval
from astropy.io import fits
from astropy import wcs
from reproject import reproject_interp
from matplotlib import pyplot as plt


def scaleImage(image, a=1, stretch_type='asinh'):
    reagon = interval.AsymmetricPercentileInterval(10., 99.95)
    vmin, vmax = reagon.get_limits(image)
    if stretch_type == 'log':
        scale = stretch.LogStretch(a=a)
    elif stretch_type == 'asinh':
        scale = stretch.AsinhStretch(a=a)
    image_scaled = (scale + reagon)(image)
    return image_scaled


def removeNaN(data):
    bdx = ~np.isfinite(data)
    data[bdx] = 0


def make_images(base, index_cut=1300, filters='gri', **kwargs):
    hdus = []
    images_scaled = []
    for fdx, filt in enumerate(filters):
        hdu = fits.open('{0}-{1}.fits.gz'.format(base, filt))
        w = wcs.WCS(hdu[0].header)
        newf = fits.PrimaryHDU()
        newf.data = hdu[0].data[index_cut:-index_cut, index_cut:-index_cut]
        newf.header = hdu[0].header
        newf.header.update(w[index_cut:-index_cut, index_cut:-index_cut].to_header())
        hdus.append(newf)
        if fdx > 0:
            scidata, footprint = reproject_interp(newf, hdus[0].header)
        scidata = newf.data
        scidata[scidata < 0] = 0
        image = scaleImage(scidata, **kwargs)
        removeNaN(image)
        images_scaled.append(image)
        plt.imsave('{0}_{1}_{2}.png'.format(base, filt, kwargs.get('stretch_type', 'asinh')), image, cmap='Greys_r', origin='lower')

    RGB_image = np.zeros([images_scaled[0].shape[0], images_scaled[0].shape[1], 3])
    RGB_image[:, :, 0] = images_scaled[2]
    RGB_image[:, :, 1] = images_scaled[1]
    RGB_image[:, :, 2] = images_scaled[0]
    RGB_image[RGB_image > 1] = 1
    RGB_image[RGB_image < 0] = 0
    plt.imsave('{0}_rgb_{1}.png'.format(base, kwargs.get('stretch_type', 'asinh')), RGB_image, origin='lower')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create single band and false color images from fits files')
    parser.add_argument('base_name', type=str, help='the base name of the fits files (note: all files must be named `{base_name}_{filter_letter}`)')
    parser.add_argument('-c', '--crop', type=int, help='an intiger used to corp the fits images (by index of array)')
    parser.add_argument('-f', '--filters', type=str, default='gri', choices=['gri', 'rbi'], help='a three letter stirng representing the filters contained in each fits file')
    parser.add_argument('-a', type=float, default=1, help='the `a` parameter used in the streact function')
    parser.add_argument('-s', '--stretch', type=str, default='asinh', choices=['asinh', 'log'], help='the type of stretch to use for the fits image')

    args = parser.parse_args()
    make_images(args.base_name, index_cut=args.crop, filters=args.filters, a=args.a, stretch_type=args.stretch)
