import os

"""
This pipeline runner demonstrates how to use the binning up in pipelines. Checkout the pipeline
'autolens_workspace/pipelines/beginner/features/binning_up.py' for a description binning up.

I'll assume that you are familiar with how the beginner runners work, so if any code doesn't make sense familiarize
yourself with those first!
"""

""" AUTOFIT + CONFIG SETUP """

import autofit as af

workspace_path = "{}/../..".format(os.path.dirname(os.path.realpath(__file__)))

conf.instance = conf.Config(
    config_path=f"{workspace_path}/config", output_path=f"{workspace_path}/output"
)

dataset_label = "imaging"
dataset_name = "lens_sie__source_sersic"
pixel_scales = 0.1

""" AUTOLENS + DATA SETUP """

import autolens as al
import autolens.plot as aplt

dataset_path = af.util.create_path(
    path=workspace_path, folders=["dataset", dataset_label, dataset_name]
)

imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    pixel_scales=pixel_scales,
)

mask = al.Mask.circular(
    shape_2d=imaging.shape_2d, pixel_scales=imaging.pixel_scales, radius=3.0
)

aplt.Imaging.subplot_imaging(imaging=imaging, mask=mask)

"""
We simply import the binning up pipeline and pass the level of binning up we want as an input parameter (which
for the pipeline below, is only used in phase 1).
"""

from pipelines.settings import binning_up

pipeline = binning_up.make_pipeline(phase_folders=["features"], bin_up_factor=2)

pipeline.run(dataset=imaging, mask=mask)