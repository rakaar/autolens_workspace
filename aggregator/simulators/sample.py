from os import path
import autolens as al
import autolens.plot as aplt

"""
This script simulates a sample of three strong lenses, which are used to illustrate the `Aggregator`.

It follows the scripts described in the `/autolens_workspace/simulators/`, so if anything doesn`t make sense 
check those scripts out for details!
"""

"""The pixel scale of the datasets that are simulated."""
pixel_scales = 0.1

"""EXAMPLE LENS SYSTEM 1"""

"""
The `dataset_type` describes the type of data being simulated (in this case, `Imaging` data) and `dataset_name` 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

 - The image will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/image.fits`.
 - The noise-map will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/lens_name/noise_map.fits`.
 - The psf will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""

dataset_type = "aggregator"
dataset_name = "mass_sie__source_sersic__0"

"""Create the path where the dataset is output."""
dataset_path = path.join("dataset", dataset_type, dataset_name)

"""The grid use to create the image."""
grid = al.GridIterate.uniform(
    shape_2d=(100, 100), pixel_scales=0.1, fractional_accuracy=0.9999
)

"""Simulate a simple Gaussian PSF for the image."""
psf = al.Kernel.from_gaussian(shape_2d=(11, 11), sigma=0.1, pixel_scales=pixel_scales)

"""
To simulate the `Imaging` dataset we first create a simulator, which defines the exposure time, background sky,
noise levels and psf of the dataset that is simulated.
"""
simulator = al.SimulatorImaging(
    exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=0.8, elliptical_comps=(0.0, 0.25)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    bulge=al.lp.EllipticalSersic(
        centre=(0.1, 0.1),
        elliptical_comps=(0.0, 0.25),
        intensity=0.3,
        effective_radius=1.0,
        sersic_index=2.0,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated `Imaging` dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=path.join(dataset_path, "image.fits"),
    psf_path=path.join(dataset_path, "psf.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    overwrite=True,
)

"""
Pickle the `Tracer` in the dataset folder, ensuring the true `Tracer` is safely stored and available if we need to 
check how the dataset was simulated in the future. 

This will also be accessible via the `Aggregator` if a model-fit is performed using the dataset.
"""
tracer.save(file_path=dataset_path, filename="true_tracer")


"""EXAMPLE LENS SYSTEM 2"""

"""
The `dataset_type` describes the type of data being simulated (in this case, `Imaging` data) and `dataset_name` 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

 - The image will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/image.fits`.
 - The noise-map will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/lens_name/noise_map.fits`.
 - The psf will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""
dataset_type = "aggregator"
dataset_name = "mass_sie__source_sersic__1"

"""Create the path where the dataset is output."""
dataset_path = path.join("dataset", dataset_type, dataset_name)

"""
        Returns a simulator, which defines the shape, resolution and pixel-scale of the image that is simulated, as well as
its exposure time, noise levels and psf.
"""
simulator = al.SimulatorImaging(
    exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.0, elliptical_comps=(0.25, 0.0)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    bulge=al.lp.EllipticalSersic(
        centre=(0.2, 0.2),
        elliptical_comps=(0.0, 0.15),
        intensity=0.3,
        effective_radius=1.5,
        sersic_index=2.5,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated `Imaging` dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=path.join(dataset_path, "image.fits"),
    psf_path=path.join(dataset_path, "psf.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    overwrite=True,
)

"""
Pickle the `Tracer` in the dataset folder, ensuring the true `Tracer` is safely stored and available if we need to 
check how the dataset was simulated in the future. 

This will also be accessible via the `Aggregator` if a model-fit is performed using the dataset.
"""
tracer.save(file_path=dataset_path, filename="true_tracer")


"""EXAMPLE LENS SYSTEM 3"""

"""
The `dataset_type` describes the type of data being simulated (in this case, `Imaging` data) and `dataset_name` 
gives it a descriptive name. They define the folder the dataset is output to on your hard-disk:

 - The image will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/image.fits`.
 - The noise-map will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/lens_name/noise_map.fits`.
 - The psf will be output to `/autolens_workspace/dataset/dataset_type/dataset_name/psf.fits`.
"""

dataset_type = "aggregator"
dataset_name = "mass_sie__source_sersic__2"

"""Create the path where the dataset is output."""
dataset_path = path.join("dataset", dataset_type, dataset_name)

"""
Returns a simulator, which defines the shape, resolution and pixel-scale of the image that is simulated, as well as
its exposure time, noise levels and psf.
"""
simulator = al.SimulatorImaging(
    exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
)

lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.2, elliptical_comps=(0.25, 0.0)
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    bulge=al.lp.EllipticalSersic(
        centre=(0.3, 0.3),
        elliptical_comps=(0.0, 0.222222),
        intensity=0.3,
        effective_radius=2.0,
        sersic_index=3.0,
    ),
)

"""Use these galaxies to setup a tracer, which will generate the image for the simulated `Imaging` dataset."""
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.image(tracer=tracer, grid=grid)

"""
We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
imaging dataset.
"""
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

"""Output our simulated dataset to the dataset path as .fits files"""
imaging.output_to_fits(
    image_path=path.join(dataset_path, "image.fits"),
    psf_path=path.join(dataset_path, "psf.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    overwrite=True,
)

"""
Pickle the `Tracer` in the dataset folder, ensuring the true `Tracer` is safely stored and available if we need to 
check how the dataset was simulated in the future. 

This will also be accessible via the `Aggregator` if a model-fit is performed using the dataset.
"""
tracer.save(file_path=dataset_path, filename="true_tracer")
