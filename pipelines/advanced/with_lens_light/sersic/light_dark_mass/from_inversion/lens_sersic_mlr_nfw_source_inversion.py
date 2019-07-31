import autofit as af
from autolens.model.galaxy import galaxy_model as gm
from autolens.pipeline.phase import phase_imaging
from autolens.pipeline import pipeline
from autolens.pipeline import pipeline_tagging
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.profiles import light_and_mass_profiles as lmp
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg

import os


# In this pipeline, we'll perform an analysis which fits an image with the lens light included, and a source galaxy
# using an inversion, using a decomposed light and dark matter profile. The pipeline follows on from the
# inversion pipeline 'pipelines/with_lens_light/inversion/from_initialize/lens_sie_source_inversion.py'.

# The pipeline is two phases, as follows:

# Phase 1:

# Description: Fits the lens light and mass model as a decomposed profile, using an inversion for the Source.
# Lens Light & Mass: EllipticalSersic
# Lens Mass: SphericalNFW + ExternalShear
# Source Light: VoronoiMagnification + Constant
# Previous Pipelines: with_lens_light/inversion/from_initialize/lens_sie_source_inversion.py
# Prior Passing: Lens Light (variable -> previous pipeline), Lens Mass (default),
#                Source Inversion (variable / constant -> previous pipeline)
# Notes: Uses an interpolation pixel scale for fast power-law deflection angle calculations by default.

# Phase 2:

# Description: Refines the inversion parameters, using a fixed mass model from phase 1.
# Lens Light & Mass: EllipticalSersic
# Lens Mass: SphericalNFW + ExternalShear
# Source Light: VoronoiMagnification + Constant
# Previous Pipelines: None
# Prior Passing: Lens Light & Mass (constant -> phase 1), source inversion (variable -> phase 1)
# Notes: Uses an interpolation pixel scale for fast power-law deflection angle calculations by default.


def make_pipeline(
    pipeline_settings,
    phase_folders=None,
    tag_phases=True,
    redshift_lens=0.5,
    redshift_source=1.0,
    sub_grid_size=2,
    signal_to_noise_limit=None,
    bin_up_factor=None,
    positions_threshold=None,
    inner_mask_radii=None,
    interp_pixel_scale=0.05,
    use_inversion_border=True,
    inversion_pixel_limit=None,
    cluster_pixel_scale=0.1,
):

    ### SETUP PIPELINE AND PHASE NAMES, TAGS AND PATHS ###

    # We setup the pipeline name using the tagging module. In this case, the pipeline name is not given a tag and
    # will be the string specified below However, its good practise to use the 'tag.' function below, incase
    # a pipeline does use customized tag names.

    pipeline_name = "pipeline_ldm__lens_sersic_mlr_nfw_source_inversion"
    pipeline_name = pipeline_tagging.pipeline_name_from_name_and_settings(
        pipeline_name=pipeline_name,
        include_shear=pipeline_settings.include_shear,
        align_light_dark_centre=pipeline_settings.align_light_dark_centre,
        pixelization=pipeline_settings.pixelization,
        regularization=pipeline_settings.regularization,
    )

    phase_folders.append(pipeline_name)

    ### PHASE 1 ###

    # In phase 1, we will fit the lens galaxy's light and mass and one source galaxy, where we:

    # 1) Pass priors on the lens galaxy's light using the EllipticalSersic of the previous pipeline.
    # 2) Pass priors on the lens galaxy's SphericalNFW mass profile's centre using the EllipticalIsothermal fit of the
    #    previous pipeline, if the NFW centre is a free parameter.
    # 3) Pass priors on the lens galaxy's shear using the ExternalShear fit of the previous pipeline.
    # 4) Pass priors on the source galaxy's inversion using the Pixelization and Regularization of the previous pipeline.

    class LensSourcePhase(phase_imaging.PhaseImaging):
        def pass_priors(self, results):

            ### Lens Light to Light + Mass, Sersic -> Sersic ###

            self.galaxies.lens.light_mass.centre = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.centre

            self.galaxies.lens.light_mass.axis_ratio = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.axis_ratio

            self.galaxies.lens.light_mass.phi = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.phi

            self.galaxies.lens.light_mass.intensity = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.intensity

            self.galaxies.lens.light_mass.effective_radius = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.effective_radius

            self.galaxies.lens.light_mass.sersic_index = results.from_phase(
                "phase_3_lens_sersic_sie_source_sersic"
            ).variable.galaxies.lens.light.sersic_index

            ### Lens Mass, SIE ->  NFW ###

            if pipeline_settings.align_light_dark_centre:

                self.galaxies.lens.dark.centre = self.galaxies.lens.light_mass.centre

            elif not pipeline_settings.align_light_dark_centre:

                self.galaxies.lens.dark.centre = (
                    results.from_phase("phase_3_lens_sersic_sie_source_sersic")
                    .variable_absolute(a=0.05)
                    .galaxies.lens.light_mass.centre
                )

            ### Lens Shear, Shear -> Shear ###

            self.galaxies.lens.shear = results.from_phase(
                "phase_2_lens_sie_source_inversion"
            ).variable.galaxies.lens.shear

            ### Source Inversion, Inv -> Inv ###

            self.galaxies.source = results.from_phase(
                "phase_2_lens_sie_source_inversion"
            ).inversion.constant.galaxies.source

    phase1 = LensSourcePhase(
        phase_name="phase_1_lens_sersic_mlr_nfw_source_inversion",
        phase_folders=phase_folders,
        tag_phases=tag_phases,
        galaxies=dict(
            lens=gm.GalaxyModel(
                redshift=redshift_lens,
                light_mass=lmp.EllipticalSersic,
                dark=mp.SphericalNFW,
                shear=mp.ExternalShear,
            ),
            source=gm.GalaxyModel(
                redshift=redshift_source,
                pixelization=pipeline_settings.pixelization,
                regularization=pipeline_settings.regularization,
            ),
        ),
        sub_grid_size=sub_grid_size,
        signal_to_noise_limit=signal_to_noise_limit,
        bin_up_factor=bin_up_factor,
        positions_threshold=positions_threshold,
        inner_mask_radii=inner_mask_radii,
        interp_pixel_scale=interp_pixel_scale,
        use_inversion_border=use_inversion_border,
        inversion_pixel_limit=inversion_pixel_limit,
        cluster_pixel_scale=cluster_pixel_scale,
        optimizer_class=af.MultiNest,
    )

    phase1.optimizer.const_efficiency_mode = True
    phase1.optimizer.n_live_points = 75
    phase1.optimizer.sampling_efficiency = 0.2

    phase1 = phase1.extend_with_inversion_phase()

    return pipeline.PipelineImaging(pipeline_name, phase1)