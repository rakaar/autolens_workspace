import autofit as af
import autolens as al
import autolens.plot as aplt
import os

# This dataset_label maker makes example simulated images using decomposed light and dark matter profiles.

# The 'dataset label' is the name of the dataset folder and 'dataset_name' the folder the dataset is stored in, e.g:

# The image will be output as '/autolens_workspace/dataset/dataset_label/dataset_name/image.fits'.
# The noise-map will be output as '/autolens_workspace/dataset/dataset_label/dataset_name/lens_name/noise_map.fits'.
# The psf will be output as '/autolens_workspace/dataset/dataset_label/dataset_name/psf.fits'.

# Setup the path to the autolens_workspace, using a relative directory name.
workspace_path = "{}/../../".format(os.path.dirname(os.path.realpath(__file__)))

# (these files are already in the autolens_workspace and are remade running this script)
dataset_label = "imaging"
dataset_name = "lens_sersic_mlr_nfw__source_sersic"

# Create the path where the dataset will be output, which in this case is
# '/autolens_workspace/dataset/imaging/lens_sie__source_sersic/'
dataset_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=["dataset", dataset_label, dataset_name]
)

# The grid use to create the image.
grid = al.Grid.uniform(shape_2d=(100, 100), pixel_scales=0.1, sub_size=4)

# Simulate a simple Gaussian PSF for the image.
psf = al.Kernel.from_gaussian(
    shape_2d=(11, 11), sigma=0.1, pixel_scales=grid.pixel_scales
)

# To simulate the imaging dataset we first create a simulator, which defines the shape, resolution and pixel-scale of the
# image that is simulated, as well as its expoosure time, noise levels and psf.
simulator = al.SimulatorImaging(
    exposure_time_map=al.Array.full(fill_value=300.0, shape_2d=grid.shape_2d),
    psf=psf,
    background_sky_map=al.Array.full(fill_value=0.1, shape_2d=grid.shape_2d),
    add_noise=True,
)

# Setup the lens galaxy's light (elliptical Sersic), mass (SIE+Shear) and source galaxy light (elliptical Sersic) for
# this simulated lens.
lens_galaxy = al.Galaxy(
    redshift=0.5,
    light=al.lmp.EllipticalSersic(
        centre=(0.0, 0.0),
        axis_ratio=0.9,
        phi=45.0,
        intensity=1.0,
        effective_radius=0.8,
        sersic_index=4.0,
        mass_to_light_ratio=0.3,
    ),
    mass=al.mp.SphericalNFW(centre=(0.0, 0.0), kappa_s=0.1, scale_radius=20.0),
    shear=al.mp.ExternalShear(magnitude=0.03, phi=45.0),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    light=al.lp.EllipticalSersic(
        centre=(0.1, 0.1),
        axis_ratio=0.8,
        phi=60.0,
        intensity=0.3,
        effective_radius=1.0,
        sersic_index=2.5,
    ),
)


# Use these galaxies to setup a tracer, which will generate the image for the simulated Imaging dataset.
tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

# To make this figure, we need to pass the plotter a grid which it uses to create the image. The simulator has its
# grid accessible as a property, which we can use to do this.
aplt.Tracer.profile_image(tracer=tracer, grid=grid)

# We can then pass this simulator a tracer, which uses the tracer to create a ray-traced image which is simulated as
# imaging dataset following the setup of the dataset.
imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

# Lets plot the simulated Imaging dataset before we output it to fits.
aplt.Imaging.subplot_imaging(imaging=imaging)

# Finally, lets output our simulated dataset to the dataset path as .fits files.
imaging.output_to_fits(
    image_path=dataset_path + "image.fits",
    psf_path=dataset_path + "psf.fits",
    noise_map_path=dataset_path + "noise_map.fits",
    overwrite=True,
)
