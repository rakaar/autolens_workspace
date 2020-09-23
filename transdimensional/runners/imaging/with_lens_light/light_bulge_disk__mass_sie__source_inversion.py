# %%
"""
__WELCOME__ 

This transdimensional pipeline runner loads a strong lens dataset and analyses it using a transdimensional lens
modeling pipeline.

Using a pipeline composed of five phases this runner fits `Imaging` of a strong lens system, where in the final phase
of the pipeline:

 - The lens galaxy`s `LightProfile` is modeled as an `EllipticalSersic` and _EllipticalExponential_.
 - The lens galaxy`s `MassProfile` is modeled as an _EllipticalIsothermal_.
 - The source galaxy is modeled using an _Inversion_.

This uses the pipeline (Check it out full description of the pipeline):

 `autolens_workspace/pipelines/imaging/with_lens_light/light_bulge_disk__mass_sie__source_inversion.py`.
"""

# %%
"""Use the WORKSPACE environment variable to determine the path to the `autolens_workspace`."""

# %%
import os

workspace_path = os.environ["WORKSPACE"]
print("Workspace Path: ", workspace_path)

# %%
""" AUTOLENS + DATA SETUP """

# %%
import autolens as al
import autolens.plot as aplt

dataset_type = "imaging"
dataset_label = "with_lens_light"
dataset_name = "light_bulge_disk__mass_sie__source_sersic"
pixel_scales = 0.1

# %%
"""
Create the path where the dataset will be loaded from, which in this case is
`/autolens_workspace/dataset/imaging/light_bulge_disk__mass_sie__source_sersic`
"""

# %%
dataset_path = f"{workspace_path}/dataset/{dataset_type}/{dataset_label}/{dataset_name}"

# %%
"""Using the dataset path, load the data (image, noise-map, PSF) as an `Imaging` object from .fits files."""

# %%
imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    pixel_scales=pixel_scales,
)

# %%
"""Next, we create the mask we'll fit this data-set with."""

# %%
mask = al.Mask2D.circular(
    shape_2d=imaging.shape_2d, pixel_scales=imaging.pixel_scales, radius=3.0
)

# %%
"""Make a quick subplot to make sure the data looks as we expect."""

# %%
aplt.Imaging.subplot_imaging(imaging=imaging, mask=mask)

# %%
"""
__Settings__

The `SettingsPhaseImaging` describe how the model is fitted to the data in the log likelihood function.

These settings are used and described throughout the `autolens_workspace/examples/model` example scripts, with a 
complete description of all settings given in `autolens_workspace/examples/model/customize/settings.py`.

The settings chosen here are applied to all phases in the pipeline.
"""

# %%
settings_masked_imaging = al.SettingsMaskedImaging(grid_class=al.Grid, sub_size=2)

# %%
"""
_Inversion_`s may infer unphysical solution where the source reconstruction is a demagnified reconstruction of the 
lensed source (see **HowToLens** chapter 4). 

To prevent this, auto-positioning is used, which uses the lens mass model of earlier phases to automatically set 
positions and a threshold that resample inaccurate mass models (see `examples/model/positions.py`).

The *auto_positions_factor* is a factor that the threshold of the inferred positions using the previous mass model are 
multiplied by to set the threshold in the next phase. The *auto_positions_minimum_threshold* is the minimum value this
threshold can go to, even after multiplication.
"""

settings_lens = al.SettingsLens(
    auto_positions_factor=3.0, auto_positions_minimum_threshold=0.8
)

settings = al.SettingsPhaseImaging(
    settings_masked_imaging=settings_masked_imaging, settings_lens=settings_lens
)

# %%
"""
__Pipeline_Setup__:

Pipelines can contain `Setup` objects, which customize how different aspects of the model are fitted. 

First, we create a `SetupLightBulgeDisk` which customizes:

 - If the centre of the lens light profile is manually input and fixed for modeling.
 - The alignment of the centre and elliptical components of the bulge and disk.
 - If the disk is modeled as an `EllipticalExponential` or _EllipticalSersic_.

In this example we align the centres of the bulge and disk and model the disk and an _EllipticalSersic_.
"""

# %%
setup_light = al.SetupLightBulgeDisk(
    light_centre=None,
    align_bulge_disk_elliptical_comps=False,
    align_bulge_disk_centre=True,
    disk_as_sersic=True,
)

# %%
"""
This pipeline also uses a `SetupMass`, which customizes:

 - If there is an `ExternalShear` in the mass model or not.
"""

# %%
setup_mass = al.SetupMassTotal(no_shear=False)

# %%
"""
Next, we create a `SetupSourceInversion` which customizes:

 - The `Pixelization` used by the `Inversion` in phase 3 of the pipeline.
 - The `Regularization` scheme used by the `Inversion` in phase 3 of the pipeline.
"""

# %%
setup_source = al.SetupSourceInversion(
    pixelization=al.pix.VoronoiMagnification, regularization=al.reg.Constant
)

# %%
"""
_Pipeline Tagging_

The `Setup` objects are input into a `SetupPipeline` object, which is passed into the pipeline and used to customize
the analysis depending on the setup. This includes tagging the output path of a pipeline. For example, if `no_shear` 
is True, the pipeline`s output paths are `tagged` with the string `no_shear`.

This means you can run the same pipeline on the same data twice (with and without shear) and the results will go
to different output folders and thus not clash with one another!


The `folders` below specify the path the pipeline results are written to, which is:

 `autolens_workspace/output/pipelines/dataset_type/dataset_name` 
 `autolens_workspace/output/pipelines/imaging/light_bulge_disk__mass_sie__source_inversion/`


The redshift of the lens and source galaxies are also input (see `examples/model/customimze/redshift.py`) for a 
description of what inputting redshifts into **PyAutoLens** does.
"""

# %%
setup = al.SetupPipeline(
    folders=["transdimensional", f"{dataset_type}_{dataset_label}", dataset_name],
    redshift_lens=0.5,
    redshift_source=1.0,
    setup_light=setup_light,
    setup_mass=setup_mass,
    setup_source=setup_source,
)

# %%
"""
__Pipeline Creation__

To create a pipeline we import it from the pipelines folder and run its `make_pipeline` function, inputting the 
*Setup* and *SettingsPhase* above.
"""

# %%
from autolens_workspace.transdimensional.pipelines.imaging.with_lens_light import (
    light_bulge_disk__mass_sie__source_inversion,
)

pipeline = light_bulge_disk__mass_sie__source_inversion.make_pipeline(
    setup=setup, settings=settings
)

# %%
"""
__Pipeline Run__

Running a pipeline is the same as running a phase, we simply pass it our lens dataset and mask to its run function.
"""

# %%
pipeline.run(dataset=imaging, mask=mask)
