import autofit as af
import autolens as al

"""
In this pipeline, we fit `Imaging` of a strong lens system where:

 - The lens galaxy`s `LightProfile` is omitted (and is not present in the simulated data).
 - The lens galaxy`s `MassProfile` is modeled as an _EllipticalIsothermal_.
 - A subhalo is included in the lens galaxy whose `MassProfile` is modeled as a _SphericalNFW_.
 - The source galaxy`s `LightProfile` is modeled as an _EllipticalSersic_. 

The pipeline is three phases:

Phase 1:

    Fit the lens mass model and source _LightProfile_.
    
    Lens Mass: EllipticalIsothermal + ExternalShear
    Source Light: EllipticalSersic
    Prior Passing: None.
    Notes: None.

Phase 2:

    Perform the subhalo detection analysis using a *GridSearch* of non-linear searches.
    
    Lens Mass: EllipticalIsothermal + ExternalShear
    Subhalo: SphericalTruncatedNFWMCRLudlow
    Source Light: EllipticalSersic
    Prior Passing: Lens mass (instance or model -> phase_1), source light (model -> phase_1).
    Notes: Priors on subhalo are tuned to give realistic masses (10^6 - 10^11).

Phase 3:

    Refine the best-fit detected subhalo from the previous phase.
    
    Lens Mass: EllipticalIsothermal + ExternalShear
    Subhalo: SphericalTruncatedNFWMCRLudlow
    Source Light: EllipticalSersic
    Prior Passing: Lens mass & source light (model -> phase_1), subhalo mass (model -> phase_2).
    Notes: None
"""


def make_pipeline(setup, settings, grid_size=2, parallel=False):

    """SETUP PIPELINE & PHASE NAMES, TAGS AND PATHS"""

    pipeline_name = "pipeline__mass_sie__subhalo_nfw__source_sersic"

    """
    This pipeline is tagged according to whether:
    
        1) The lens galaxy mass model includes an  _ExternalShear_.
        2) The `Pixelization` and `Regularization` scheme of the pipeline (fitted in phases 3 & 4).
    """

    setup.folders.append(pipeline_name)
    setup.folders.append(setup.tag)

    """Setup: Include an `ExternalShear` in the mass model if turned on in _SetupMass_. """

    if not setup.setup_mass.no_shear:
        shear = al.mp.ExternalShear
    else:
        shear = None

    """
    Phase 1: Fit the lens`s `MassProfile``s and source `LightProfile`, where we:

        1) Set priors on the lens galaxy (y,x) centre such that we assume the image is centred around the lens galaxy.
    """

    mass = af.PriorModel(al.mp.EllipticalIsothermal)
    mass.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
    mass.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

    phase1 = al.PhaseImaging(
        phase_name="phase_1__source_sersic",
        folders=setup.folders,
        galaxies=dict(
            lens=al.GalaxyModel(
                redshift=setup.redshift_lens,
                mass=mass,
                shear=shear,
                subhalo=setup.subhalo_instance,
            ),
            source=al.GalaxyModel(
                redshift=setup.redshift_source, sersic=al.lp.EllipticalSersic
            ),
        ),
        settings=settings,
        search=af.DynestyStatic(n_live_points=50),
    )

    """
    Phase 2: Attempt to detect subhalos, by performing a NxN grid search of MultiNest searches, where:

        1) The lens model and source parameters are held fixed to the best-fit values of the previous pipeline.
        2) Each grid search varies the subhalo (y,x) coordinates and mass as free parameters.
        3) The priors on these (y,x) coordinates are UniformPriors, with limits corresponding to the grid-cells.
    """

    class GridPhase(af.as_grid_search(phase_class=al.PhaseImaging, parallel=parallel)):
        @property
        def grid_priors(self):
            return [
                self.model.galaxies.subhalo.mass.centre_0,
                self.model.galaxies.subhalo.mass.centre_1,
            ]

    subhalo = al.GalaxyModel(
        redshift=setup.redshift_lens, mass=al.mp.SphericalNFWMCRLudlow
    )

    subhalo.mass.mass_at_200 = af.LogUniformPrior(lower_limit=1.0e6, upper_limit=1.0e11)
    subhalo.mass.centre_0 = af.UniformPrior(lower_limit=-2.5, upper_limit=2.5)
    subhalo.mass.centre_1 = af.UniformPrior(lower_limit=-2.5, upper_limit=2.5)
    subhalo.mass.redshift_object = setup.redshift_lens
    subhalo.mass.setup.redshift_source = setup.redshift_source

    phase2 = GridPhase(
        phase_name="phase_2__subhalo_search",
        folders=setup.folders,
        galaxies=dict(
            lens=af.last.instance.galaxies.lens,
            subhalo=subhalo,
            source=af.last.instance.galaxies.source,
        ),
        settings=settings,
        search=af.DynestyStatic(n_live_points=40),
        number_of_steps=grid_size,
    )

    """
    Phase 3: Refine the lens + subhalo + source model, using the best subhalo model detected in the *GridSearch* above
             to initialize the subhalo priors.
    """

    subhalo = al.GalaxyModel(
        redshift=setup.redshift_lens, mass=al.mp.SphericalNFWMCRLudlow
    )
    subhalo.mass.mass_at_200 = phase2.result.model.galaxies.subhalo.mass.mass_at_200
    subhalo.mass.centre = phase2.result.model_absolute(
        a=0.5
    ).galaxies.subhalo.mass.centre
    subhalo.mass.redshift_object = setup.redshift_lens
    subhalo.mass.setup.redshift_source = setup.redshift_source

    phase3 = al.PhaseImaging(
        phase_name="phase_3__subhalo_refine",
        folders=setup.folders,
        galaxies=dict(
            lens=phase1.result.model.galaxies.lens,
            source=phase1.result.model.galaxies.source,
            subhalo=subhalo,
        ),
        settings=settings,
        search=af.DynestyStatic(n_live_points=80),
    )

    return al.PipelineDataset(pipeline_name, phase1, phase2, phase3)
