# %%

"""
__Example: Modeling__

To fit a lens model to a dataset, we must perform lens modeling, which uses a non-linear search algorithm to fit many
different tracers to the dataset.

Model-fitting is handled by our project **PyAutoFit**, a probablistic programming language for non-linear model
fitting. The setting up on configuration files is performed by our project **PyAutoConf**. We'll need to import
both to perform the model-fit.
"""

# %%
"""
In this example script, we will fit imaging of a strong lens system where:

    - The lens galaxy's *MassProfile* is fitted with an *EllipticalIsothermal*.
    - The source galaxy's *LightProfile* is fitted with an *EllipticalSersic*.
    
Thus, for this system the lens galaxy's light emission is omitted (it is not present in the simulated data).     
"""

# %%
from autoconf import conf
import autofit as af
import os

workspace_path = "{}/../../..".format(os.path.dirname(os.path.realpath(__file__)))

# %%
"""
We use this path to set:
    config_path:
        Where PyAutoLens configuration files are located. The default location is '/path/to/autolens_workspace/config'. 
        They control many aspects of PyAutoLens (visualization, model priors, etc.). Feel free to check them out!.
    
    output-path: 
        Where the output of the non-linear search and model-fit are stored on your hard-disk. The default location 
        is '/path/to/autolens_workspace/output.
"""

# %%
conf.instance = conf.Config(
    config_path=f"{workspace_path}/config", output_path=f"{workspace_path}/output"
)

# %%
"""
To begin lets load the strong lens dataset 'lens_sie__source_sersic' 'from .fits files, which is the dataset we will
use to perform lens modeling.

This is the same dataset we fitted in the 'fitting.py' example.
"""

# %%
import autolens as al
import autolens.plot as aplt

dataset_label = "imaging"
dataset_name = "lens_sie__source_sersic"
dataset_path = f"{workspace_path}/dataset/{dataset_label}/{dataset_name}"

imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    psf_path=f"{dataset_path}/psf.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    pixel_scales=0.1,
)

# %%
"""
The model-fit also requires a mask, which defines the regions of the image we use to fit the lens model to the data.
"""

# %%
mask = al.Mask.circular(
    shape_2d=imaging.shape_2d, pixel_scales=imaging.pixel_scales, sub_size=1, radius=3.0
)

# %%
"""
__Phase__

To perform lens modeling, we create a *PhaseImaging* object, which comprises:

   - The *GalaxyModel*'s used to fit the data.
   - The *PhaseSettings* which customize how the model is fitted to the data.
   - The *NonLinearSearch* used to sample parameter space.
   
Once we have create the phase, we 'run' it by passing it the data and mask.
"""

# %%
"""
__Model__

We compose our lens model using *GalaxyModel* objects, which represent the galaxies we fit to our data. In this 
example our lens mooel is:

    - An *EllipticalIsothermal* *MassProfile* for the lens galaxy's mass (5 parameters).
    - An *EllipticalSersic* *LightProfile* for the source galaxy's light (6 parameters).

The number of free parameters and therefore the dimensionality of non-linear parameter space is N=11.
"""

# %%
lens_galaxy_model = al.GalaxyModel(redshift=0.5, mass=al.mp.EllipticalIsothermal)
source_galaxy_model = al.GalaxyModel(redshift=1.0, light=al.lp.EllipticalSersic)

# %%
"""
__Settings__

Next, we specify the *PhaseSettingsImaging*, which describe how the model is fitted to the data in the log likelihood
function. Below, we specify:
 
    - That a regular *Grid* is used to fit create the model-image when fitting the data 
      (see 'autolens_workspace/examples/grids.py' for a description of grids).
    - The sub-grid size of this grid.

Different *PhaseSettings* are used in different example model scripts and a full description of all *PhaseSettings* 
can be found in the example script 'autolens/workspace/examples/model/customize/settingspy' and the following 
link -> <link>
"""

# %%
settings = al.PhaseSettingsImaging(grid_class=al.Grid, sub_size=2)

# %%
"""
__Search__

The lens model is fitted to the data using a *NonLinearSearch*, which we specify below. In this example, we use the
nested sampling algorithm Dynesty (https://dynesty.readthedocs.io/en/latest/), with:

    - 50 live points.
    - A sampling efficiency of 60%.

The script 'autolens_workspace/examples/model/customize/non_linear_searches.py' gives a description of the types of
non-linear searches that can be used with **PyAutoLens**. If you do not know what a non-linear search is or how it 
operates, I recommend you complete chapters 1 and 2 of the HowToLens lecture series.
"""

# %%
search = af.DynestyStatic(n_live_points=50, sampling_efficiency=0.6)

# %%
"""
__Phase__

We can now combine the model, settings and non-linear search above to create and run a phase, fitting our data with
the lens model.

The phase_name and phase_folders inputs below specify the path of the results in the output folder:  

    '/autolens_workspace/output/examples/phase__lens_sie__source_sersic'.
"""

# %%
phase = al.PhaseImaging(
    phase_name="phase__lens_sie__source_sersic",
    galaxies=dict(lens=lens_galaxy_model, source=source_galaxy_model),
    settings=settings,
    search=search,
    phase_folders=["examples"],
)

# %%
"""
We can now begin the fit by passing the dataset and mask to the phase, which will use the non-linear search to fit
the model to the data. 

The fit outputs visualization on-the-fly, so checkout the path 
'/path/to/autolens_workspace/output/examples/phase__lens_sie__source_sersic' to see how your fit is doing!
"""

# %%
result = phase.run(dataset=imaging, mask=mask)

# %%
"""
The phase above returned a result, which, for example, includes the lens model corresponding to the maximum
log likelihood solution in parameter space.
"""

# %%
print(result.max_log_likelihood_instance)

# %%
"""
It also contains instances of the maximum log likelihood Tracer and FitImaging, which can be used to visualize
the fit.
"""

# %%
aplt.Tracer.subplot_tracer(tracer=result.max_log_likelihood_tracer, grid=mask.geometry.masked_grid)
aplt.FitImaging.subplot_fit_imaging(fit=result.max_log_likelihood_fit)

# %%
"""
Checkout '/path/to/autolens_workspace/examples/modeling/results.py' for a full description of the result object.
"""