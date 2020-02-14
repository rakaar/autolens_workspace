import os

import autofit as af
import autoarray.plot as aplt

### INTRODUCTION ####

# After fitting a large suite of data with the same pipeline, the aggregator allows us to load the results and
# manipulate / plot them using a Python script or Jupyter notebook.

# In '/autolens_workspace/aggregator/beginner_runner.py' we fitted 3 strong lenses which were simulated using different
# lens models. We fitted each image with the pipeline:

# 'autolens_workspace/pipelines/beginner/no_lens_light/lens_sie__source_inversion.py'

# This pipeline is composed of 3 phases.

### FILE OUTPUT ####

# The results of this fit are in the '/output/aggregator_sample_beginner' folder. First, take a look in this folder.
# Provided you haven't rerun the runner, you'll notice that all the results (e.g. optimizer, optimizer_backup,
# model.results, images, etc.) are in .zip files, as opposed to folders that can be instantly accessed.

# This is because when the pipeline was run, the 'remove_files' option in the 'config/general.ini' was set to True.
# This means all results (other than the .zip file) were removed. This feature is implemented because super-computers
# often have a limit on the number of files allowed per user.

# Bare in mind the fact that all results are in .zip files - we'll come back to this point in a second.

### AGGREGATOR ###

# We can load the results of each pipeline's analysis of each of the 3 images using the aggregator. This will allow us
# to manipulate the results in this Python script (or a Jupyter notebook) to plot figures, interpret results,
# check specific values, etc.

# To begin, we setup the path to the output path we want to load results from, which in this case is the folder
# 'autolens_workspace/output/aggregator_sample'.
workspace_path = "{}/../".format(os.path.dirname(os.path.realpath(__file__)))
output_path = workspace_path + "output"
aggregator_results_path = output_path + "/aggregator_sample_beginner"

# Now we'll use this path to explicitly set the config path and output path.
af.conf.instance = af.conf.Config(
    config_path=str(workspace_path + "/config"), output_path=str(output_path)
)

# To set up the aggregator we simply pass it the folder of the results we want to load.
aggregator = af.Aggregator(directory=str(aggregator_results_path))

# Before we continue, take another look at the output folder. The .zip files containing results have now all been
# unzipped, such that the results are accessible on your laptop for navigation. This means you can run fits to many
# lenses on a super computer and easily unzip all the results on your computer afterwards via the aggregator.

### MODEL RESULTS ###

# We can now create a list of the 'non-linear outputs' of every fit. An instance of the NonLinearOutput class acts as
# an interface between the results of the non-linear fit on your hard-disk and Python.

# The fits to each lens used MultiNest, so below we create a list of instances of the MultiNestOutput class (the
# non-linear output class will change dependent on whatever non-linear optimizer is used).
multi_nest_outputs = aggregator.output

# When we print this list of outputs we see 9 different MultiNestOutput instances. These correspond to all 3
# phases of each pipeline's fit to all 3 images.
print("MultiNest Outputs:")
print(multi_nest_outputs)
print("Total Outputs = ", len(multi_nest_outputs), "\n")

# If we want to remove the fits of the first 2 phases, and just keep the MultiNestOutputs of the 3rd and final
# phase of the pipeline, we can do so using the phase's name.
phase_name = "phase_3__source_inversion"
multi_nest_outputs = aggregator.filter(phase=phase_name).output

# As expected, this list now has only 3 MultiNestOutputs, one for each image we fitted.
print("Phase Name Filtered MultiNest Outputs:")
print(multi_nest_outputs)
print("Total Outputs = ", len(multi_nest_outputs), "\n")

# In this example, we only fitted the 3 images using one pipeline. But suppose used multiple pipelines. In this case,
# the aggregator would load the MultiNestOutputs of all fits of all phases of all pipelines!

# In such circumstances, we can filter by pipeline name.
pipeline_name = "pipeline__lens_sie__source_inversion"
multi_nest_outputs = aggregator.filter(pipeline=pipeline_name, phase=phase_name).output

# As expected, this list again now has 3 MultiNestOutputs.
print("Pipeline Name Filtered MultiNest Outputs:")
print(multi_nest_outputs)
print("Total Outputs = ", len(multi_nest_outputs), "\n")

# We can use outputs to create a list of the most-likely (e.g. highest likelihood) model of each fit to our three
# images (in this case in phase 3).
most_likely_model_parameters = [
    out.most_probable_model_parameters for out in multi_nest_outputs
]
print("Most Likely Model Parameter Lists:")
print(most_likely_model_parameters, "\n")

# This provides us with lists of all model parameters. However, this isn't that much use - which values correspond
# to which parameters?

# Its more useful to create the model instance of every fit.
most_likely_model_instances = [
    out.most_probable_model_instance for out in multi_nest_outputs
]
print("Most Likely Model Instances:")
print(most_likely_model_instances, "\n")

# We can also access the 'most probable' model, which is the model computed by marginalizing over the MultiNest samples
# of every parameter in 1D and taking the median of this PDF.
most_probable_model_parameters = [
    out.most_probable_model_parameters for out in multi_nest_outputs
]
most_probable_model_instances = [
    out.most_probable_model_instance for out in multi_nest_outputs
]

print("Most Probable Model Parameter Lists:")
print(most_probable_model_parameters, "\n")
print("Most probable Model Instances:")
print(most_probable_model_instances, "\n")

# We can compute the upper and lower errors on each parameter at a given sigma limit.
upper_errors = [
    out.model_errors_at_upper_sigma_limit(sigma_limit=3.0) for out in multi_nest_outputs
]
upper_error_instances = [
    out.model_errors_instance_at_upper_sigma_limit(sigma_limit=3.0)
    for out in multi_nest_outputs
]
lower_errors = [
    out.model_errors_at_lower_sigma_limit(sigma_limit=3.0) for out in multi_nest_outputs
]
lower_error_instances = [
    out.model_errors_instance_at_lower_sigma_limit(sigma_limit=3.0)
    for out in multi_nest_outputs
]

print("Errors Lists:")
print(upper_errors, "\n")
print(lower_errors, "\n")
print("Errors Instances:")
print(upper_error_instances, "\n")
print(lower_error_instances, "\n")

# The maximum likelihood of each model fit and its Bayesian evidence (estimated via MultiNest) are also available.

# Given each fit is to a different image, these arn't all that useful. However, in tutorial 4 we'll look at using the
# aggregator for images that we fit with many different models and many different pipelines, in which case compairing
# the evidences allows us to perform Bayesian model comparison!
print("Likelihoods:")
print([out.maximum_log_likelihood for out in multi_nest_outputs])
print([out.maximum_evidence for out in multi_nest_outputs])

# We can also print the "model_results" of all phases, which is string that summarizes every fit's lens model providing
# quick inspection of all results.
results = aggregator.filter(pipeline=pipeline_name).model_results
print("Model Results Summary:")
print(results, "\n")
