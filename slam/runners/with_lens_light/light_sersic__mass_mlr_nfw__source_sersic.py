# %%
"""
__SLaM (Source, Light and Mass)__

This SLaM pipeline runner loads a strong lens dataset and analyses it using a SLaM lens modeling pipeline.

__THIS RUNNER__

Using a source pipeline, a light pipeline and a mass pipeline this runner fits _Imaging_ of a strong lens system
where in the final phase of the pipeline:

 - The lens galaxy's _LightProfile_'s are modeled as an _EllipticalSersic_ + _EllipticalExponential_, representing
   a bulge + disk model.
 - The lens galaxy's stellar _MassProfile_ is fitted using the _EllipticalSersic_ + EllipticalExponential of the
    _LightProfile_, where it is converted to a stellar mass distribution via constant mass-to-light ratios.
 - The source galaxy's _LightProfile_ is modeled using an _EllipticalSersic_.

This runner uses the SLaM pipelines:

 'slam/with_lens_light/source__sersic.py'.
 'slam/with_lens_light/light__sersic.py'.
 'slam/with_lens_light/mass__light_dark__sersic.py'.

Check them out for a detailed description of the analysis!
"""

# %%
"""Use the WORKSPACE environment variable to determine the path to the autolens workspace."""

# %%
import os

workspace_path = os.environ["WORKSPACE"]
print("Workspace Path: ", workspace_path)

# %%
""" AUTOLENS + DATA SETUP """
import autolens as al
import autolens.plot as aplt

# %%
"""Specify the dataset type, label and name, which we use to determine the path we load the data from."""
dataset_type = "imaging"
dataset_label = "light_dark"
dataset_name = "light_sersic__mass_mlr_nfw__source_sersic"
pixel_scales = 0.1

# %%
"""
Create the path where the dataset will be loaded from, which in this case is
'/autolens_workspace/dataset/imaging/light_bulge_disk__mass_mlr_nfw__source_parametric'
"""

# %%
dataset_path = f"{workspace_path}/dataset/{dataset_type}/{dataset_label}/{dataset_name}"

# %%
"""Using the dataset path, load the data (image, noise-map, PSF) as an _Imaging_ object from .fits files."""

# %%
imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    pixel_scales=pixel_scales,
)

mask = al.Mask.circular(
    shape_2d=imaging.shape_2d, pixel_scales=pixel_scales, radius=3.0
)

aplt.Imaging.subplot_imaging(imaging=imaging, mask=mask)

# %%
"""
__Settings__

The _SettingsPhaseImaging_ describe how the model is fitted to the data in the log likelihood function.

These settings are used and described throughout the 'autolens_workspace/examples/model' example scripts, with a 
complete description of all settings given in 'autolens_workspace/examples/model/customize/settings.py'.

The settings chosen here are applied to all phases in the pipeline.
"""

# %%
"""
Due to the slow deflection angle calculation of the _EllipticalSersic_ and _EllipticalExponential_ _MassProfile_'s
we use _GridInterpolate_ objects to speed up the analysis. This is specified separately for the _Grid_ used to fit
the source _LightProfile_ and perform the _Inversion_.
"""

# %%
settings_masked_imaging = al.SettingsMaskedImaging(
    grid_class=al.GridInterpolate,
    grid_inversion_class=al.GridInterpolate,
    pixel_scales_interp=0.1,
)

settings = al.SettingsPhaseImaging(settings_masked_imaging=settings_masked_imaging)

# %%
"""
__PIPELINE SETUP__

Transdimensional pipelines used the _SetupPipeline_ object to customize the analysis performed by the pipeline,
for example if a shear was included in the mass model and the model used for the source galaxy.

SLaM pipelines break the analysis down into multiple pipelines which focus on modeling a specific aspect of the strong 
lens, first the Source, then the (lens) Light and finally the Mass. Each of these pipelines has it own setup object 
which is equivalent to the _SetupPipeline_ object, customizing the analysis in that pipeline. Each pipeline therefore
has its own _SetupMass_, _SetupLight_ and _SetupSource_ object.

The _Setup_ used in earlier pipelines determine the model used in later pipelines. For example, if the _Source_ 
pipeline is given a _Pixelization_ and _Regularization_, than this _Inversion_ will be used in the subsequent 
_SLaMPipelineLight_ and Mass pipelines. The assumptions regarding the lens light chosen by the _Light_ object are 
carried forward to the _Mass_  pipeline.

The _Setup_ again tags the path structure of every pipeline in a unique way, such than combinations of different
SLaM pipelines can be used to fit lenses with different models. If the earlier pipelines are identical (e.g. they use
the same _SLaMPipelineSource_) they will reuse those results before branching off to fit different models in the 
_SLaMPipelineLight_ and / or _SLaMPipelineMass_ pipelines. 
"""

# %%
"""
__HYPER SETUP__

The _SetupHyper_ determines which hyper-mode features are used during the model-fit and is used identically to the
hyper pipeline examples.

The _SetupHyper_ object has a new input available, 'hyper_fixed_after_source', which fixes the hyper-parameters to
the values computed by the hyper-phase at the end of the Source pipeline. By fixing the hyper-parameter values in the
_SLaMPipelineLight_ and _SLaMPipelineMass_ pipelines, model comparison can be performed in a consistent fashion.
"""

# %%
hyper = al.SetupHyper(
    hyper_galaxies=False,
    hyper_image_sky=False,
    hyper_background_noise=False,
    hyper_fixed_after_source=True,
)

# %%
"""
__SLaMPipelineSourceParametric__

The parametric source pipeline aims to initialize a robust model for the source galaxy using _LightProfile_ objects. 

_SLaMPipelineSourceParametric_ determines the source model used by the parametric source pipeline. A full description of all 
options can be found ? and ?.

By default, this assumes an _EllipticalIsothermal_ profile for the lens galaxy's mass and an _EllipticalSersic_ + 
_EllipticalExponential_ model for the lens galaxy's light. Our experience with lens modeling has shown they are the 
simplest models that provide a good fit to the majority of strong lenses.

For this runner the _SLaMPipelineSourceParametric_ customizes:

 - The _MassProfile_ fitted by the pipeline (and the following _SLaMPipelineSourceInversion_).
 - If there is an _ExternalShear_ in the mass model or not.
"""

setup_light = al.SetupLightBulgeDisk(light_centre=(0.0, 0.0))
setup_mass = al.SetupMassTotal(
    mass_profile=al.mp.EllipticalIsothermal, no_shear=False, mass_centre=(0.0, 0.0)
)
setup_source = al.SetupSourceSersic()

pipeline_source_parametric = al.SLaMPipelineSourceParametric(
    setup_light=setup_light, setup_mass=setup_mass, setup_source=setup_source
)

# %%
"""
__SLaMPipelineLight__

The _SLaMPipelineLight_ pipeline fits the model for the lens galaxy's bulge + disk light model. 

A full description of all options can be found ? and ?.

The model used to represent the lens galaxy's light is input into _SLaMPipelineLight_ below and this runner uses an 
 _EllipticalSersic_.
 
For this runner the _SLaMPipelineLight_ customizes:

 - That the _LightProfile_ centre is fixed to (0.0, 0.0).

The _SLaMPipelineLight_ uses the mass model fitted in the previous _SLaMPipelineSource_'s.

The _SLaMPipelineLight_ and imported light pipelines determine the lens light model used in _Mass_ pipelines.
"""

# %%
setup_light = al.SetupLightSersic(light_centre=(0.0, 0.0))

pipeline_light = al.SLaMPipelineLight(setup_light=setup_light)

# %%
"""
__SLaMPipelineMass__

The _SLaMPipelineMass_ pipeline fits the model for the lens galaxy's decomposed stellar and dark matter mass distribution. 

A full description of all options can be found ? and ?.

The model used to represent the lens galaxy's mass is an _EllipticalSersic_ and _EllipticalExponential_ 
_LightMassProfile_ representing the bulge and disk fitted in the previous pipeline, alongside a _SphericalNFW_ for the
dark matter halo.

For this runner the _SLaMPipelineMass_ customizes:

 - If there is an _ExternalShear_ in the mass model or not.
"""

setup_mass = al.SetupMassLightDark(no_shear=False, mass_centre=(0.0, 0.0))

pipeline_mass = al.SLaMPipelineMass(setup_mass=setup_mass)

# %%
"""
__SLaM__

We combine all of the above _SLaM_ pipelines into a _SLaM_ object.

The _SLaM_ object contains a number of methods used in the make_pipeline functions which are used to compose the model 
based on the input values. It also handles pipeline tagging and path structure.
"""

slam = al.SLaM(
    folders=["slam", f"{dataset_type}_{dataset_label}", dataset_name],
    setup_hyper=hyper,
    pipeline_source_parametric=pipeline_source_parametric,
    pipeline_light=pipeline_light,
    pipeline_mass=pipeline_mass,
)

# %%
"""
__PIPELINE CREATION__

We import and make pipelines as per usual, albeit we'll now be doing this for multiple pipelines!

We then add the pipelines together and run this summed pipeline, which runs each individual pipeline back-to-back.
"""

# %%
from autolens_workspace.slam.pipelines.with_lens_light import source__sersic
from autolens_workspace.slam.pipelines.with_lens_light import light__sersic
from autolens_workspace.slam.pipelines.with_lens_light import mass__light_dark__sersic

source__sersic = source__sersic.make_pipeline(slam=slam, settings=settings)
light__sersic = light__sersic.make_pipeline(slam=slam, settings=settings)
mass__light_dark__sersic = mass__light_dark__sersic.make_pipeline(
    slam=slam, settings=settings
)

pipeline = source__sersic + light__sersic + mass__light_dark__sersic

pipeline.run(dataset=imaging, mask=mask)
