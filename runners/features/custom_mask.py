import os

# This pipeline runner demonstrates how to load a custom mask for a lens from the hard-disk, and use this as the
# default mask in a pipeline.

# I'll assume that you are familiar with how the beginner runners work, so if any code doesn't make sense familiarize
# yourself with those first!

### AUTOFIT + CONFIG SETUP ###

import autofit as af

workspace_path = "{}/../..".format(os.path.dirname(os.path.realpath(__file__)))

af.conf.instance = af.conf.Config(
    config_path=f"{workspace_path}/config", output_path=f"{workspace_path}/output"
)

dataset_label = "imaging"
dataset_name = "lens_sie__source_sersic"
pixel_scales = 0.1

### AUTOLENS + DATA SETUP ###

import autolens as al
import autolens.plot as aplt

dataset_path = af.path_util.make_and_return_path_from_path_and_folder_names(
    path=workspace_path, folder_names=["dataset", dataset_label, dataset_name]
)

imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    pixel_scales=pixel_scales,
)

# Okay, we need to load the mask from a .fits file, in the same fashion as the imaging above. To draw a mask for an
# image, checkout the tutorial
# 'autolens_workspace/preprocess/imaging/p4_mask.ipynb'

# The example autolens_workspace dataset comes with a mask already, if you look in
# autolens_workspace/dataset/imaging/lens_sie__source_sersic/ you'll see a mask.fits file!
mask = al.Mask.from_fits(
    file_path=dataset_path + "mask.fits", hdu=0, pixel_scales=pixel_scales
)

# When we plot the imaging dataset, we can:

# - Pass the mask to show it on the image.
# - Extract only the regions of the image in the mask, to remove contaminating bright sources away from the lens.
# - zoom in around the mask to emphasize the lens.

aplt.Imaging.subplot_imaging(imaging=imaging, mask=mask)

source_setup = al.setup.Source()
mass_setup = al.setup.Mass()
setup = al.setup.Setup(source=source_setup, mass=mass_setup)

# Finally, we import and make the pipeline as described in the runner.py file, but pass the mask into the
# 'pipeline.run() function.

from pipelines.beginner.with_lens_light import lens_sersic_sie__source_sersic

pipeline = lens_sersic_sie__source_sersic.make_pipeline(
    setup=setup, phase_folders=["features"]
)

pipeline.run(dataset=imaging, mask=mask)
