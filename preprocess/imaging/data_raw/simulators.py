import autofit as af
from astropy.io import fits
import autolens as al
import autolens.plot as aplt

import os


def simulate_all_imaging(dataset_path):

    simulate_imaging(dataset_path=dataset_path)
    simulate_imaging_in_counts(dataset_path=dataset_path)
    simulate_imaging_in_adus(dataset_path=dataset_path)
    simulate_imaging_with_large_stamp(dataset_path=dataset_path)
    simulate_imaging_with_small_stamp(dataset_path=dataset_path)
    simulate_imaging_noise_map_wht(dataset_path=dataset_path)
    simulate_imaging_with_offset_centre(dataset_path=dataset_path)
    simulate_imaging_with_even_psf(dataset_path=dataset_path)
    simulate_imaging_with_large_psf(dataset_path=dataset_path)
    simulate_imaging_with_unnormalized_psf(dataset_path=dataset_path)
    simulate_imaging_with_psf_with_offset_centre(dataset_path=dataset_path)


def simulate_imaging(dataset_path):

    imaging_path = f"{dataset_path}/imaging"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )

    new_hdul = fits.HDUList()
    new_hdul.append(fits.ImageHDU(imaging.image.in_2d))
    new_hdul.append(fits.ImageHDU(imaging.noise_map.in_2d))
    new_hdul.append(fits.ImageHDU(imaging.psf.in_2d))

    if os.path.exists(f"{imaging_path}/multiple_hdus.fits"):
        os.remove(f"{imaging_path}/multiple_hdus.fits")

    new_hdul.writeto(f"{imaging_path}/multiple_hdus.fits")


def simulate_imaging_in_counts(dataset_path):

    imaging_path = f"{dataset_path}/imaging_in_counts"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    exposure_time_map = al.Array.full(
        fill_value=1000.0, shape_2d=grid.shape_2d, pixel_scales=grid.pixel_scales
    )
    exposure_time_map.output_to_fits(
        file_path=f"{imaging_path}/exposure_time_map.fits", overwrite=True
    )

    imaging.data = al.preprocess.array_eps_to_counts(
        array_eps=imaging.image, exposure_time_map=exposure_time_map
    )
    imaging.noise_map = al.preprocess.array_eps_to_counts(
        array_eps=imaging.noise_map, exposure_time_map=exposure_time_map
    )

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_in_adus(dataset_path):

    imaging_path = f"{dataset_path}/imaging_in_adus"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    exposure_time_map = al.Array.full(
        fill_value=1000.0, shape_2d=grid.shape_2d, pixel_scales=grid.pixel_scales
    )
    exposure_time_map.output_to_fits(
        file_path=f"{imaging_path}/exposure_time_map.fits", overwrite=True
    )

    imaging.data = al.preprocess.array_eps_to_adus(
        array_eps=imaging.image, exposure_time_map=exposure_time_map, gain=4.0
    )
    imaging.noise_map = al.preprocess.array_eps_to_adus(
        array_eps=imaging.noise_map, exposure_time_map=exposure_time_map, gain=4.0
    )

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_large_stamp(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_large_stamp"

    grid = al.Grid.uniform(shape_2d=(800, 800), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_small_stamp(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_small_stamp"

    grid = al.Grid.uniform(shape_2d=(50, 50), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_offset_centre(dataset_path):

    imaging_path = f"{dataset_path}/imaging_offset_centre"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(1.0, 1.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(1.0, 1.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(1.0, 1.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_noise_map_wht(dataset_path):

    imaging_path = f"{dataset_path}/imaging_noise_map_wht"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.noise_map = 1.0 / imaging.noise_map ** 2.0

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_large_psf(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_large_psf"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(101, 101), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_even_psf(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_even_psf"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.psf = al.Kernel.from_gaussian(
        shape_2d=(22, 22), sigma=0.05, pixel_scales=0.1
    )

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_unnormalized_psf(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_unnormalized_psf"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1)

    psf = 10.0 * psf

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )


def simulate_imaging_with_psf_with_offset_centre(dataset_path):

    imaging_path = f"{dataset_path}/imaging_with_off_centre_psf"

    grid = al.Grid.uniform(shape_2d=(130, 130), pixel_scales=0.1, sub_size=1)

    psf = al.Kernel.from_gaussian(
        shape_2d=(21, 21), sigma=0.05, pixel_scales=0.1, centre=(0.1, 0.1)
    )

    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.3, effective_radius=1.0, sersic_index=2.0
        ),
        mass=al.mp.SphericalIsothermal(centre=(0.0, 0.0), einstein_radius=1.2),
    )

    source_galaxy = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.SphericalSersic(
            centre=(0.0, 0.0), intensity=0.2, effective_radius=1.0, sersic_index=1.5
        ),
    )

    tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

    simulator = al.SimulatorImaging(
        exposure_time=300.0, psf=psf, background_sky_level=0.1, add_poisson_noise=True
    )

    imaging = simulator.from_tracer_and_grid(tracer=tracer, grid=grid)

    imaging.output_to_fits(
        image_path=f"{imaging_path}/image.fits",
        noise_map_path=f"{imaging_path}/noise_map.fits",
        psf_path=f"{imaging_path}/psf.fits",
        overwrite=True,
    )
