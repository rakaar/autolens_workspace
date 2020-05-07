# %%
"""
__Fitting__

In this example, we'll fit the imaging data we simulated in the previous exercise. We'll do this using model images generated via a tracer, and by comparing to the simulated image we'll get diagostics about the quality of the fit.
"""

# %%
#%matplotlib inline

import autolens as al
import autolens.plot as aplt

# %%
"""
First you need to change the path below to the chapter 1 directory so we can load the data we output previously.
"""

# %%
chapter_path = "/home/jammy/PycharmProjects/PyAuto/autolens_workspace/howtolens/chapter_1_introduction"

# %%
"""
The data path specifies where the data was output in the last tutorial, this time in the directory 'chapter_path/data'
"""

# %%
dataset_path = f"{chapter_path}/dataset"

imaging = al.Imaging.from_fits(
    image_path=f"{dataset_path}/image.fits",
    noise_map_path=f"{dataset_path}/noise_map.fits",
    psf_path=f"{dataset_path}/psf.fits",
    pixel_scales=0.1,
)

# %%
"""
'imaging' is a ImagingData object, which is a 'package' of all components of the Imaging instrument of the lens, 
in particular:

1) The image.
2) The Point Spread Function (PSF).
3) Its noise map.
"""

# %%
print("Image:")
print(imaging.image)
print("Noise-Map:")
print(imaging.noise_map)
print("PSF:")
print(imaging.psf)

# %%
"""
To fit an image, we first specify a mask. A mask describes the sections of the image that we fit.

Typically, we want to mask regions of the image where the lens and source galaxies are not visible, for example at 
the edges where the signal is entirely background sky and noise.

For the image we simulated, a 3" circular mask will do the job.

A mask also takes the 'sub_size' parameter we are used to giving a grid. This does what it does for a grid - defining 
the (masked) sub-grid used to calculate lensing quantities from a mask.
"""

# %%
mask = al.Mask.circular(
    shape_2d=imaging.shape_2d, pixel_scales=imaging.pixel_scales, sub_size=1, radius=3.0
)

print(mask)  # 1 = True, which means the pixel is masked. Edge pixels are indeed masked.
print(mask[48:53, 48:53])  # Whereas central pixels are False and therefore unmasked.

# %%
"""
We can use a imaging_plotter to compare the mask and the image - this is useful if we really want to 'tailor' a 
mask to the lensed source's light (which in this example, we won't).
"""

# %%
aplt.Imaging.image(imaging=imaging, mask=mask)

# %%
"""
We also use the mask to 'zoom' our plot around the masked region only - meaning that if our image is very large, we 
focus-in on the lens and source galaxies.

The mask also remove all pixels outside the mask in the plot, meaning bright pixels outside the mask won't impact the 
plot's color range.

You'll see this is an option for pretty much every plotter in PyAutoLens, and is something we'll do often throughout 
the tutorials.
"""

# %%
"""
A masked data object is a 'package' of all parts of a data-set we need in order to fit it with a lens model:

1) The imaging-data, including the image, PSF (so that when we compare a tracer's image to the image instrument we 
can include blurring due to the telescope optics) and noise map (so our goodness-of-fit measure accounts for 
noise in the observations).

2) The mask, so that only the regions of the image with a signal are fitted.

3) A grid aligned to the imaging data's pixels, so the tracer's image is generated on the same (masked) grid as the image.
"""

# %%
masked_imaging = al.MaskedImaging(imaging=imaging, mask=mask)

aplt.Imaging.image(imaging=masked_imaging.imaging)

# %%
"""
By printing its attribute, we can see that it does indeed contain the mask, masked image, masked noise map, psf and so on.
"""

# %%
print("Mask")
print(masked_imaging.mask)
print()
print("Masked Image:")
print(masked_imaging.image)
print()
print("Masked Noise-Map:")
print(masked_imaging.noise_map)
print()
print("PSF:")
print(masked_imaging.psf)
print()

# %%
"""
The masked image and noise map are again stored in 2D and 1D. 

However, the 1D array now corresponds only to the pixels that were not masked, whereas for the 2D array, all edge 
values are masked and are therefore zeros.
"""

# %%
print("The 2D Masked Image and 1D Image of unmasked entries")
print(masked_imaging.image.shape_2d)
print(masked_imaging.image.shape_1d)
print(masked_imaging.image.in_2d)
print(masked_imaging.image.in_1d)
print()
print("The 2D Masked Noise-Map and 1D Noise-Map of unmasked entries")
print(masked_imaging.noise_map.shape_2d)
print(masked_imaging.noise_map.shape_1d)
print(masked_imaging.noise_map.in_2d)
print(masked_imaging.noise_map.in_1d)

# %%
"""
The masked data also has a grid, where only coordinates which are not masked are included (the masked 2D values are 
set to [0.0. 0.0]).
"""

# %%
print("Masked Grid")
print(masked_imaging.grid.in_2d)
print(masked_imaging.grid.in_1d)

# %%
"""
To fit an image, create an image using a tracer. Lets use the same tracer we simulated the imaging instrument with 
(thus, our fit is 'perfect').

Its worth noting that below, we use the masked imaging's grid to setup the tracer. This ensures that our image-plane 
image is the same resolution and alignment as our lens data's masked image.
"""

# %%
lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
    ),
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

tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

aplt.Tracer.profile_image(tracer=tracer, grid=masked_imaging.grid)

# %%
"""
To fit the image, we pass the lens data and tracer to the 'lens_fit' module. This performs the following:

1) Blurs the tracer's image with the lens data's PSF, ensuring the telescope optics are included in the fit. This 
creates the fit's 'model_image'.

2) Computes the difference between this model_image and the observed image-data, creating the fit's 'residual_map'.

3) Divides the residual-map by the noise map and squares each value, creating the fit's 'chi_squared_map'.

4) Sums up these chi-squared values and converts them to a 'log_likelihood', which quantifies how good the tracer's fit to 
the data was (higher log_likelihood = better fit).
"""

# %%
fit = al.FitImaging(masked_imaging=masked_imaging, tracer=tracer)

aplt.FitImaging.subplot_fit_imaging(fit=fit, include=aplt.Include(mask=True))

# %%
"""
We can print the fit's attributes. As usual, we can choose whether to return the fits in 2d or 1d, and in 2d if we 
don't specify where we'll get all zeros, as the edges were masked:
"""

# %%
print("Model-Image:")
print(fit.model_image.in_2d)
print(fit.model_image.in_1d)
print()
print("Residual Maps:")
print(fit.residual_map.in_2d)
print(fit.residual_map.in_1d)
print()
print("Chi-Squareds Maps:")
print(fit.chi_squared_map.in_2d)
print(fit.chi_squared_map.in_1d)

# %%
"""
Of course, the central unmasked pixels have non-zero values.
"""

# %%
model_image = fit.model_image.in_2d
print(model_image[48:53, 48:53])
print()

residual_map = fit.residual_map.in_2d
print("Residuals Central Pixels:")
print(residual_map[48:53, 48:53])
print()

print("Chi-Squareds Central Pixels:")
chi_squared_map = fit.chi_squared_map.in_2d
print(chi_squared_map[48:53, 48:53])

# %%
"""
The fit also gives a log likelihood, which is a single-figure estimate of how good the model image fitted the simulated 
image (in unmasked pixels only!).
"""

# %%
print("Likelihood:")
print(fit.log_likelihood)

# %%
"""
We used the same tracer to create and fit the image, giving an excellent fit. The residual-map and chi-squared-map, 
show no signs of the source galaxy's light present, indicating a good fit. This solution will translate to one of the 
highest-log_likelihood solutions possible.

Lets change the tracer, so that it's near the correct solution, but slightly off. Below, we slightly offset the lens 
galaxy, by 0.005"
"""

# %%
lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.005, 0.005), einstein_radius=1.6, axis_ratio=0.7, phi=45.0
    ),
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

tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

fit = al.FitImaging(masked_imaging=masked_imaging, tracer=tracer)

aplt.FitImaging.subplot_fit_imaging(fit=fit, include=aplt.Include(mask=True))

# %%
"""
Residuals now appear at the locations of the source galaxy, increasing the chi-squared values (which determine 
our log_likelihood).

Lets compare the log likelihood to the value we computed above (which was 4372.90):
"""

# %%
print("Previous Likelihood:")
print(4593.8596)
print("New Likelihood:")
print(fit.log_likelihood)

# %%
"""
It decreases! As expected, this model us a worse fit to the data.

Lets change the tracer, one more time, to a solution nowhere near the correct one.
"""

# %%
lens_galaxy = al.Galaxy(
    redshift=0.5,
    mass=al.mp.EllipticalIsothermal(
        centre=(0.005, 0.005), einstein_radius=1.5, axis_ratio=0.72, phi=60.0
    ),
)

source_galaxy = al.Galaxy(
    redshift=1.0,
    light=al.lp.EllipticalSersic(
        centre=(0.2, 0.0),
        axis_ratio=0.8,
        phi=60.0,
        intensity=0.5,
        effective_radius=0.8,
        sersic_index=2.5,
    ),
)

tracer = al.Tracer.from_galaxies(galaxies=[lens_galaxy, source_galaxy])

fit = al.FitImaging(masked_imaging=masked_imaging, tracer=tracer)

aplt.FitImaging.subplot_fit_imaging(fit=fit, include=aplt.Include(mask=True))

# %%
"""
Clearly, the model provides a terrible fit and this tracer is not a plausible representation of the image-data 
(of course, we already knew that, given that we simulated it!)

The log likelihood drops dramatically, as expected.
"""

# %%
print("Previous Likelihoods:")
print(4593.8596)
print(4478.4995)
print("New Likelihood:")
print(fit.log_likelihood)

# %%
"""
Congratulations, you've fitted your first strong lens with PyAutoLens! Perform the following exercises:

1) In this example, we 'knew' the correct solution, because we simulated the lens ourselves. In the real Universe, 
we have no idea what the correct solution is. How would you go about finding the correct solution? Could you find a 
solution that fits the data reasonable through trial and error?

"""

# %%


# %%
