import autofit as af
from os import path
import autolens as al

"""
So, how does hyper-mode work in pipelines? There are a lot more things we have to do now; pass hyper-galaxy-images
between phases, use different `Pixelization`'s and `Regularization`.chemes, and decide what parts of the noise-map we do
and don't want to scale.

##HYPER IMAGE PASSING ###

So, lets start with hyper-image passing. That is, how do we pass the model images of the lens and source galaxies to
later phases to use them as hyper-galaxy-images? Well, I've got some good news, *we no nothing*. **PyAutoLens** automatically
passes hyper-images between phases!

However, **PyAutoLens** does need to know which hyper-images to pass to which galaxies. To do this, **PyAutoLens** uses
galaxy-names. When you create a `GalaxyModel`, you name the `Galaxy`'s for example below we've called the lens galaxy
`lens` and the source galaxy `source`:

phase1 = al.PhaseImaging(
    name="phase[1]",
    
    galaxies=af.CollectionPriorModel(
NAME --> lens=al.GalaxyModel(
            redshift=0.5,
            bulge=al.lp.EllipticalSersic,
            mass=al.mp.EllipticalIsothermal,
        )
    ),
      galaxies=af.CollectionPriorModel(
NAME --> source=al.GalaxyModel(redshift=1.0, bulge=al.lp.EllipticalSersic)
    ),
)

To pass the resulting model images of these galaxies to galaxies in the next phase, galaxies are paired by their names.
So, in the next phase (phase2), the lens galaxy must be called `lens` (again) and the source galaxy `source` (again).
Hopefully, you`ve followed this naming convention with **PyAutoLens** up to now anyway, so this should come naturually.

Why do we pass images based on galaxy names? It is because for more complex lens systems (e.g. with multiple lens and
source galaixes) we must explicitly define how their images are linked between phases.

##HYPER PHASES ###

There is one more major change to hyper-pipelines. That is, how do we fit for the hyper-parameters using our
non-linear search (e.g. Dynesty)? We don't fit for them simultaneously with the lens and source models, as this
creates an unnecessarily large parameter space which we`d fail to fit accurately and efficiently.

Instead, we `extend` phases with extra phases that specifically fit certain components of hyper-galaxy-model. You`ve
hopefully already seen the following code, which optimizes the parameters of an `Inversion` (e.g. the `Pixelization` and
regularization):

phase1 = phase1.extend_with_inversion_phase()

Extending a phase with hyper phases is just as easy:

phase1 = phase1.extend_with_multiple_hyper_phases(
    hyper-galaxy=True,
    include_background_sky=True,
    include_background_noise=True,
    inversion=True
)

This extends the phase with 3 additional phases:

1) Fit the `Inversion` parameters using the `Pixelization` and `Regularization` scheme that were used in the main phase.
   (e.g. a brightness-based `Pixelization` and adaptive `Regularization` scheme. The best-fit lens and source
   models are used. This is called the `inversion` phase.

2) Simultaneously fit the hyper-galaxies, background sky and background noise hyper parameters using the best-fit
   lens and source models from the main phase. Thus, this phase only scales the noise and the image. This is called
   the `hyper-galaxy` phase.

3) Fit all of the components above using Gaussian priors centred on the resulting values in steps 1) and 2). This is
   important as there is trade-off between increasing the noise in the lens / source and changing the `Pixelization`.
   `Regularization`.yper-galaxy-parameters. This is called the `hyper_combined` phase.

In the pipeline below we use the results of the `hyper_combined` phase to setup the hyper-galaxies, hyper-image,
_Pixelization_`s and regularizations in the next phase. Typically, we set these components up as `instances` whose
parameters are fixed during the main phases which fit the lens and source models.

##HYPER MASKING ###

In hyper-model, the mask *cannot* change between phases. This is because of hyper-galaxy-image passing. If the mask
changes and adds new pixels that were not modeled in the previous phase, these pixels wouldn't be in the
hyper-galaxy-image. This causes some very nasty problems. Thus, the same mask must be used throughout the analysis.
To ensure this happens, for hyper-galaxy-pipelines we require that the mask is passed to the `pipeline.run` function.

import autofit as af
from os import path
import autolens as al

For our example hyper-pipeline,we're going to run 7 (!) phases. There isn't much new here compared to normal
pipelines. But, the large number of phases are required to fully model the lens with hyper-mode features. An overview
of the pipeline is as follows:

Phase 1) Fit and subtract the lens `Galaxy`'s `LightProfile`.
Phase 1 Extension) Fit the lens `Galaxy`'s hyper-galaxy and background noise.

Phase 2) Fit the lens galaxy mass model and source `LightProfile`, using the lens subtracted image, using the lens
         hyper-galaxy noise-map and background noise from phase 1.
Phase 2 Extension) Fit the lens / source hyper-galaxy and background noise.

Phase 3) Fit the lens light, mass and source using priors from phases 1 & 2, using the lens hyper-galaxy
         from phase 2.
Phase 3 Extension) Fit the lens / source hyper-galaxy and background noise.

Phase 4) Initialize an `Inversion` of the source-galaxy, using a magnification based `Pixelization` and constant
         `Regularization` scheme.
Phase 4 Extension) Fit the lens / source hyper-galaxy and background noise.

Phase 5) Refine the lens light and mass models using the `Inversion` from phase 4.
Phase 5 Extension) Fit the lens / source hyper-galaxy and background noise.

Phase 6) Initialize an `Inversion` of the source-galaxy, using a brightness based `Pixelization` and adaptive
         `Regularization` scheme.
Phase 6 Extension) Fit the lens / source hyper-galaxy, background noise and reoptimize the `Inversion`.

Phase 7) Refine the lens light and mass models using the `Inversion` from phase 6 and lens / source hyper galaxy.
Phase 7 Extension) Fit the lens / source hyper-galaxy, background noise and reoptimize the `Inversion`.

Phew! Thats a lot of phases, so lets take a look.

For hyper-pipelines, we pass pipeline setup which detemine whether certain hyper-galaxy features are on or off. For
example, if pipeline_setup.general.hyper_galaxy is False, noise-scaling via hyper-galaxies is omitted  We also pass in the
_Pixelization_/ `Regularization`.chemes that will be used in phase 6 and 7 of the pipeline.
"""


def make_pipeline(setup, settings):

    ##SETUP PIPELINE AND PHASE NAMES, TAGS AND PATHS ###

    pipeline_name = "pipeline__hyper_example"

    """
    This pipeline is tagged according to whether:

        1) Hyper-fitting setup (galaxies, sky, background noise) are used.
        2) The `Pixelization` and `Regularization` scheme of the pipeline (fitted in phases 3 & 4).
    """

    path_prefix = path.join(setup.path_prefix, pipeline_name)

    """
    Phase 1:

    We set up and run phase 1 as per usual for pipelines, so nothing new here.
    """

    phase1 = al.PhaseImaging(
        search=af.DynestyStatic(name="phase[1]_light[bulge]", n_live_points=30),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(redshift=0.5, bulge=al.lp.EllipticalSersic)
        ),
    )

    """
    This extends phase 1 with hyper-phases that fit for the hyper-galaxies, as described above. The extension below
    adds two phases, a `hyper-galaxy` phase which fits for the lens hyper-galaxy + the background noise, and a
    `hyper_combined` phase which fits them again.
    
    Although this might sound like unnecessary repetition, the second phase uses Gaussian priors inferred from the
    first phase, meaning that it can search regions of parameter space that may of been unaccessible due to the
    first phase`s uniform piors.
    """

    phase1 = phase1.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 2:

    This phase fits for the lens`s mass model and source's `LightProfile` using the lens subtracted image from phase
    1. The lens galaxy hyper-galaxy is included, such that high chi-squared values in the central regions of the
    image due to a poor lens light subtraction are reduced by noise scaling and do not impact the fit.

    You can also setup individual model components and customize their priors using a `PriorModel` instead of setting
    up the entire GalaxyModel.
    """

    mass = af.PriorModel(al.mp.EllipticalIsothermal)
    mass.centre = phase1.result.model_absolute(a=0.1).galaxies.lens.bulge.centre

    """
    You will note three new inputs to the phase below, `hyper_galaxy`, `hyper_image_sky` and `hyper_background_noise`.

    These are new to a hyper-galaxy-pipeline and will appear in every pass priors function. Basically, these
    check whether a hyper-galaxy-feature is turned on. If it is, then it will have been fitted for in the previous
    phase`s `hyper_combined` phase, so its parameters are passed to this phase as instances.
    """

    phase2 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[2]_mass_[sie]_source[bulge]", n_live_points=50
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase1.result.instance.galaxies.lens.bulge,
                mass=mass,
                shear=al.mp.ExternalShear,
                hyper_galaxy=phase1.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(redshift=1.0, bulge=al.lp.EllipticalSersic),
        ),
        hyper_image_sky=phase1.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase1.result.hyper.instance.optional.hyper_background_noise,
    )

    """
    This extends phase 2 with hyper-phases that fit for the hyper-galaxies, as described above. This extension again
    adds two phases, a `hyper-galaxy` phase and `hyper_combined` phase. Unlike the extension to phase 1 which only
    include a lens hyper-galaxy, this extension includes both the lens and source hyper-galaxy `Galaxy`'s as well as the
    background noise.
    """

    phase2 = phase2.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 3:

    Usual stuff in this phase - we fit the lens and source using priors from the above 2 phases.

    Although the above hyper-galaxy phase includes fitting for the source galaxy, at this early stage in the
    pipeline we make a choice not to pass the hyper-galaxy of the source. Why? Because there is a good chance
    our simplistic single Sersic `Profile` won't yet provide a good fit to the source.
    #
    If this is the case, the hyper noise-map won't be very good. It isn't until we are fitting the
    source using an `Inversion` that we begin to pass its hyper-galaxy, e.g. when we can be confident our fit
    to the dataset is reliable!
    """

    phase3 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[3]_light[bulge]_mass[sie]_source[exp]", n_live_points=100
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase1.result.model.galaxies.lens.bulge,
                mass=phase2.result.model.galaxies.lens.mass,
                shear=phase2.result.model.galaxies.lens.shear,
                hyper_galaxy=phase2.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(
                redshift=1.0, bulge=phase2.result.model.galaxies.source.bulge
            ),
        ),
        hyper_image_sky=phase2.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase2.result.hyper.instance.optional.hyper_background_noise,
    )

    """The usual phase extension, which operates the same as the extension for phase 2."""

    phase3 = phase3.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 4:

    Next, we initialize a magnification based `Pixelization` and constant `Regularization` scheme. But, you're probably
    wondering, why do we bother with these at all? Why not jump straight to the brightness based `Pixelization` and
    adaptive regularization?

    Well, its to do with the hyper-galaxy-images of our source. At the end of phase 3, we've only fitted the source galaxy
    using a single `EllipticalSersic` profile. What if the source galaxy is more complex than a Sersic? Or has
    multiple components? Our fit, put simply, won't be very good! This makes for a bad hyper-galaxy-image.

    So, its beneficial for us to introduce an intermediate `Inversion` using a magnification based grid, that fits
    all components of the source accurately giving us a good quality hyper-galaxy image for the brightness based
    `Pixelization` and adaptive regularization. Its for this reason we've also omitted the hyper-galaxy source galaxy
    from the phases above; if the hyper-galaxy-image were poor, so is the hyper noise-map!
    """

    phase4 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[4]_source[inversion_initialize_magnification]", n_live_points=20
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase3.result.instance.galaxies.lens.bulge,
                mass=phase3.result.instance.galaxies.lens.mass,
                shear=phase3.result.instance.galaxies.lens.shear,
                hyper_galaxy=phase3.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(
                redshift=1.0,
                pixelization=al.pix.VoronoiMagnification,
                regularization=al.reg.Constant,
            ),
        ),
        hyper_image_sky=phase3.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase3.result.hyper.instance.optional.hyper_background_noise,
    )

    """
    This is the usual phase extensions. Given we're only using this `Inversion` to refine our hyper-galaxy-images, we
    won't bother reoptimizing its hyper-galaxy-parameters
    """

    phase4 = phase4.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 5: Refine the lens light and mass models using this magnification based `Pixelization` and constant
    `Regularization` scheme. If our source model was a bit dodgy because it was more complex than a single Sersic, it
    probably means our lens model was too, so a quick refinement in phase 5 is worth the effort!
    """

    phase5 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[5]_light[bulge]_mass[sie]_source[inversion_magnification]",
            n_live_points=100,
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase3.result.model.galaxies.lens.bulge,
                mass=phase3.result.model.galaxies.lens.mass,
                shear=phase3.result.model.galaxies.lens.shear,
                hyper_galaxy=phase4.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(
                redshift=1.0,
                pixelization=phase4.result.instance.galaxies.source.pixelization,
                regularization=phase4.result.instance.galaxies.source.regularization,
            ),
        ),
        hyper_image_sky=phase4.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase4.result.hyper.instance.optional.hyper_background_noise,
    )

    phase5 = phase5.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 6: use our hyper-galaxy-mode features to adapt the `Pixelization` to the source's morphology
    and the `Regularization` to its brightness! This phase works like a hyper initialization phase, whereby we fix
    the lens and source models to the best-fit of the previous phase and just optimize the hyper-galaxy-parameters.
    """

    phase6 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[6]_source[inversion_initialize]", n_live_points=20
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase5.result.instance.galaxies.lens.bulge,
                mass=phase5.result.instance.galaxies.lens.mass,
                shear=phase5.result.instance.galaxies.lens.shear,
                hyper_galaxy=phase5.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(
                redshift=1.0,
                pixelization=phase5.result.model.galaxies.source.pixelization,  # <- This is our brightness based `Pixelization`.rovided it was input into the pipeline.
                regularization=phase5.result.model.galaxies.source.regularization,  # <- And this our adaptive regularization.
            ),
        ),
        hyper_image_sky=phase5.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase5.result.hyper.instance.optional.hyper_background_noise,
    )

    """
    For this phase, we'll also extend it with an `Inversion` phase. This ensures our `Pixelization` and regularization
    are fully optimized in conjunction with the hyper-galaxies and background noise-map.
    """

    phase6 = phase6.extend_with_hyper_phase(setup_hyper=setup.setup_hyper)

    """
    Phase 7: fit the lens light and mass models one final time using all our hyper-galaxy-mode features.

    Finally, now we trust our source hyper-galaxy-image, we'll our source-hyper-galaxy in this phase.
    """

    phase7 = al.PhaseImaging(
        search=af.DynestyStatic(
            name="phase[7]_light[bulge]_mass[sie]_source[inversion]", n_live_points=100
        ),
        galaxies=af.CollectionPriorModel(
            lens=al.GalaxyModel(
                redshift=0.5,
                bulge=phase5.model.galaxies.lens.bulge,
                mass=phase5.model.galaxies.lens.mass,
                shear=phase5.model.galaxies.lens.shear,
                hyper_galaxy=phase6.result.hyper.instance.galaxies.lens.hyper_galaxy,
            ),
            source=al.GalaxyModel(
                redshift=1.0,
                pixelization=phase6.result.instance.galaxies.source.pixelization,
                regularization=phase6.result.instance.galaxies.source.regularization,
                hyper_galaxy=phase6.result.hyper.instance.galaxies.source.hyper_galaxy,
            ),
        ),
        hyper_image_sky=phase6.result.hyper.instance.optional.hyper_image_sky,
        hyper_background_noise=phase6.result.hyper.instance.optional.hyper_background_noise,
    )

    return al.PipelineDataset(
        pipeline_name,
        path_prefix,
        None,
        phase1,
        phase2,
        phase3,
        phase4,
        phase5,
        phase6,
        phase7,
    )
