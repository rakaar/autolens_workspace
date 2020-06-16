import autofit as af
import autolens as al
import autolens.plot as aplt
import os

# This script creates a sample of three strong lenses, which are used to illustrate the aggregator.

# It follows the scripts described in the '/autolens_workspace/simulators/', so if anything doesn't make sense check
# those scripts out for details!

"""Setup the path to the autolens_workspace, using a relative directory name."""
aggregator_path = "{}/../".format(os.path.dirname(os.path.realpath(__file__)))

######## EXAMPLE LENS SYSTEM 1 ###########

"""
The 'dataset_label' describes the type of data being simulated (in this case, imaging data) and 'dataset_name' 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

    - The image will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/image.fits'.
    - The noise map will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/lens_name/noise_map.fits'.
    - The psf will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/psf.fits'.
"""

dataset_name = "lens_sie__source_sersic__0"

# Create the path where the dataset will be output.
dataset_path = af.util.create_path(
    path=aggregator_path, folders=["dataset", dataset_name]
)

"""The pixel scale of dataset to be simulated."""
pixel_scales = 0.1

# The grid use to create the image.
grid = al.Grid.uniform(shape_2d=(100, 100), pixel_scales=0.1, sub_size=4)

"""Simulate a simple Gaussian PSF for the image."""
psf = al.Kernel.from_gaussian(shape_2d=(11, 11), sigma=0.1, pixel_scales=pixel_scales)

"""
To simulate the imaging dataset we first create a simulator, which defines the expoosure time, background sky,
noise levels and psf of the dataset that is simulated.
"""
simulator = al.SimulatorImaging(
    exposure_time_map=al.Array.full(fill_value=300.0, shape_2d=grid.shape_2d),
    psf=psf,
    background_sky_map=al.Array.full(fill_value=0.1, shape_2d=grid.shape_2d),
    add_noise=True,
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=0.8, elliptical_comps=(0.0, 0.111111)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    light=al.lp.EllipticalSersic(
        centre=(0.1, 0.1),
        elliptical_comps=(0.0, 0.111111),
        intensity=0.3,
        effective_radius=1.0,
        sersic_index=2.0,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated imaging dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Finally, lets output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    overwrite=True,
)


######## EXAMPLE LENS SYSTEM 2 ###########

"""
The 'dataset_label' describes the type of data being simulated (in this case, imaging data) and 'dataset_name' 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

    - The image will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/image.fits'.
    - The noise map will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/lens_name/noise_map.fits'.
    - The psf will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/psf.fits'.
"""

dataset_name = "lens_sie__source_sersic__1"

# Create the path where the dataset will be output.
dataset_path = af.util.create_path(
    path=aggregator_path, folders=["dataset", dataset_name]
)

# Create a simulator, which defines the shape, resolution and pixel-scale of the image that is simulated, as well as
# its expoosure time, noise levels and psf.
simulator = al.SimulatorImaging(
    exposure_time_map=al.Array.full(fill_value=300.0, shape_2d=grid.shape_2d),
    psf=psf,
    background_sky_map=al.Array.full(fill_value=0.1, shape_2d=grid.shape_2d),
    add_noise=True,
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.0, elliptical_comps=(0.17647, 0.0)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    light=al.lp.EllipticalSersic(
        centre=(0.2, 0.2),
        elliptical_comps=(0.0, 0.15),
        intensity=0.3,
        effective_radius=1.5,
        sersic_index=2.5,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated imaging dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Finally, lets output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    overwrite=True,
)


######## EXAMPLE LENS SYSTEM 3 ###########

"""
The 'dataset_label' describes the type of data being simulated (in this case, imaging data) and 'dataset_name' 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

    - The image will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/image.fits'.
    - The noise map will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/lens_name/noise_map.fits'.
    - The psf will be output to '/autolens_workspace/dataset/dataset_label/dataset_name/psf.fits'.
"""

dataset_name = "lens_sie__source_sersic__2"

# Create the path where the dataset will be output.
dataset_path = af.util.create_path(
    path=aggregator_path, folders=["dataset", dataset_name]
)

# Create a simulator, which defines the shape, resolution and pixel-scale of the image that is simulated, as well as
# its expoosure time, noise levels and psf.
simulator = al.SimulatorImaging(
    exposure_time_map=al.Array.full(fill_value=300.0, shape_2d=grid.shape_2d),
    psf=psf,
    background_sky_map=al.Array.full(fill_value=0.1, shape_2d=grid.shape_2d),
    add_noise=True,
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.2, elliptical_comps=(0.1, 0.0)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    light=al.lp.EllipticalSersic(
        centre=(0.3, 0.3),
        elliptical_comps=(0.0, 0.222222),
        intensity=0.3,
        effective_radius=2.0,
        sersic_index=3.0,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated imaging dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Finally, lets output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    overwrite=True,
)