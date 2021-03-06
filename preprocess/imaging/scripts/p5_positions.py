"""
__Preprocess 5: - Positions (Optional)__

In this tool we mark positions on a multiply imaged strongly lensed source corresponding to a set positions / pixels 
which are anticipated to trace to the same location in the source-plane.

A non-linear sampler uses these positions to discard the mass-models where they do not trace within a threshold of
one another, speeding up the analysis and removing unwanted solutions with too much / too little mass.

If you create positions for your dataset, you must also update your runner to use them by loading them, passing them
to the pipeline run function and setting a `positions_threshold` in the pipelines. See
`autolens_workspace/runners/beginner/features/position_threshold.py` for an example.

Positions are optional, if you struggling to get PyAutoLens to infer a good model for your dataset and you haev
not tried positons yet I recommend that you do.
"""

# %%
from pyprojroot import here

workspace_path = str(here())
#%cd $workspace_path
print(f"Working Directory has been set to `{workspace_path}`")

#%matplotlib inline
from os import path
import autolens as al
import autolens.plot as aplt

# %%
"""
Setup the path to the autolens_workspace, using the correct path name below.
"""

# %%
"""
The `dataset label` is the name of the dataset folder and `dataset_name` the folder the positions are stored in e.g,
the positions will be output as `/autolens_workspace/dataset/dataset_type/dataset_name/positions.dat`.
"""

# %%
dataset_type = "imaging"
dataset_label = "no_lens_light"
dataset_name = "mass_sie__source_sersic"

# %%
"""
Returns the path where the positions will be output, which in this case is
`/autolens_workspace/dataset/imaging/no_lens_light/mass_total__source_bulge`
"""

# %%
dataset_path = path.join("dataset", dataset_type, dataset_label, dataset_name)

# %%
"""
If you use this tool for your own dataset, you *must* double check this pixel scale is correct!
"""

# %%
pixel_scales = 0.1

# %%
"""
First, load the `Imaging` dataset, so that the positions can be plotted over the strong lens image.
"""

# %%
image = al.Array.from_fits(
    file_path=path.join(dataset_path, "image.fits"), pixel_scales=pixel_scales
)

# %%
"""
Now, create a set of positions, which is a Coordinate of (y,x) values.
"""

# %%
positions = al.GridIrregularGrouped(
    grid=[[(0.8, 1.45), (1.78, -0.4), (-0.95, 1.38), (-0.83, -1.04)]]
)

# %%
"""
Now lets plot the image and positions, so we can check that the positions overlap different regions of the source.
"""

# %%
aplt.Array(array=image, positions=positions)

# %%
"""
Now we`re happy with the positions, lets output them to the dataset folder of the lens, so that we can load them from a
.dat file in our pipelines!
"""

# %%
positions.output_to_file(
    file_path=path.join(dataset_path, "positions.dat"), overwrite=True
)

# %%
"""
The workspace also includes a GUI for drawing positions, which can be found at 
`autolens_workspace/preprocess/imaging/gui/positions.py`. This tools allows you `click` on the image where an image of the
 lensed source is, and it will use the brightest pixel within a 5x5 box of pixels to select the coordinate.
"""

# %%
"""
We can input multiple lists of positions, which corresponds to pixels which are anticipated to map to different 
multiply imaged regions of the source-plane (e.g. you would need something likespectra to be able to do this)
"""

# %%
positions = al.GridIrregularGrouped(
    grid=[[(1.0, 1.0), (2.0, 0.5)], [(-1.0, -0.1), (2.0, 2.0), (3.0, 3.0)]]
)

# %%
"""
When we plot the positions, those corresponding to the same part of the source are colored the same (we reuse the image 
above meaning for this figure the positions do not correspond to the source).
"""

# %%
aplt.Array(array=image, positions=positions)
