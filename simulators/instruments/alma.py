from os import path
import autolens as al
import autolens.plot as aplt

"""
This tool allows one to make simulated datasets of strong lenses, which can be used to test example pipelines and
investigate strong lens modeling on simulated datasets where the `true` answer is known.

The `dataset label` is the name of the dataset folder and `dataset_name` the folder the dataset is stored in, e.g:

The image will be output as `/autolens_workspace/dataset/dataset_type/dataset_name/image.fits`.
The noise-map will be output as `/autolens_workspace/dataset/dataset_type/dataset_name/lens_name/noise_map.fits`.
The psf will be output as `/autolens_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""

"""To perform the Fourier transform we need the wavelengths of the baselines."""

uv_wavelengths_path = path.join("simulators", "interferometer", "uv_wavelengths")
# uv_wavelengths_file = "alma_uv_wavelengths_x10k"
# uv_wavelengths_file = "alma_uv_wavelengths_x100k"
uv_wavelengths_file = "alma_uv_wavelengths_x500k"
# uv_wavelengths_file = "alma_uv_wavelengths_x1m"
# uv_wavelengths_file = "alma_uv_wavelengths_x5m"
# uv_wavelengths_file = "alma_uv_wavelengths_x10m"

uv_wavelengths = al.util.array.numpy_array_1d_from_fits(
    file_path=path.join(uv_wavelengths_path, f"{uv_wavelengths_file}.fits"), hdu=0
)

"""
The `dataset_type` describes the type of data being simulated (in this case, `Imaging` data) and `dataset_name` 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

 - The image will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/image.fits`.
 - The noise-map will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/lens_name/noise_map.fits`.
 - The psf will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""

dataset_type = "instruments"
dataset_instrument = "alma"

"""
The path where the dataset will be output, which in this case is
`/autolens_workspace/dataset/interferometer/instruments/sma/mass_sie__source_sersic`
"""

dataset_path = path.join(
    "dataset", dataset_type, dataset_instrument, uv_wavelengths_file
)

"""
For simulating an image of a strong lens, we recommend using a GridIterate object. This represents a grid of (y,x) 
coordinates like an ordinary Grid, but when the light-profile`s image is evaluated below (using the Tracer) the 
sub-size of the grid is iteratively increased (in steps of 2, 4, 8, 16, 24) until the input fractional accuracy of 
99.99% is met.

This ensures that the divergent and bright central regions of the source galaxy are fully resolved when determining the
total flux emitted within a pixel.
"""

grid = al.GridIterate.uniform(
    shape_2d=(256, 256), pixel_scales=0.05, fractional_accuracy=0.9999
)

"""
To simulate the interferometer dataset we first create a simulator, which defines the shape, resolution and pixel-scale 
of the visibilities that are simulated, as well as its exposure time, noise levels and uv-wavelengths.
"""

simulator = al.SimulatorInterferometer(
    uv_wavelengths=uv_wavelengths,
    exposure_time=100.0,
    background_sky_level=0.1,
    noise_sigma=100.0,
    transformer_class=al.TransformerNUFFT,
)

"""Setup the lens `Galaxy`'s mass (SIE+Shear) and source galaxy light (elliptical Sersic) for this simulated lens."""

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0),
        einstein_radius=1.6,
        elliptical_comps=al.convert.elliptical_comps_from(axis_ratio=0.8, phi=45.0),
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    bulge=al.lp.EllipticalSersic(
        centre=(-0.5, -0.5),
        elliptical_comps=al.convert.elliptical_comps_from(axis_ratio=0.8, phi=60.0),
        intensity=0.3,
        effective_radius=1.0,
        sersic_index=3.0,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated `Imaging` dataset."""

tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

"""Lets look at the tracer`s image - this is the image we'll be simulating."""

aplt.Tracer.image(tracer=tracer, grid=grid)
aplt.Plane.image(plane=tracer.source_plane, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
interferometer dataset.
"""

interferometer = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Lets plot the simulated interferometer dataset before we output it to fits."""

aplt.Interferometer.subplot_interferometer(interferometer=interferometer)

transformer = simulator.transformer_class(
    uv_wavelengths=simulator.uv_wavelengths,
    real_space_mask=tracer.image_from_grid(grid=grid).in_1d_binned.mask,
)

image = transformer.image_from_visibilities(visibilities=interferometer.visibilities)

import matplotlib.pyplot as plt

plt.imshow(image)
plt.show()

"""Output our simulated dataset to the dataset path as .fits files"""

interferometer.output_to_fits(
    visibilities_path=path.join(dataset_path, "visibilities.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    uv_wavelengths_path=path.join(dataset_path, "uv_wavelengths.fits"),
    overwrite=True,
)
