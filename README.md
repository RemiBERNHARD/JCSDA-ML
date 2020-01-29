This repertory contains python notebooks (.ipynb files) and python files (.py files) which I wrote during my internship. Python notebooks have to be used in Amazon Sagemaker as it needs some packages python specific to Sagemaker, particulary to transfer files from and to Sagemaker S3 storage service.
In all these files, some code parts which are commented are here to allow you to modify the behaviour of some functions (example : choose the number of time-steps a model would be train on).
More precisely :

test_deploys3.ipynb and predict.py : code basis to deploy a neural network on data sets located in a s3 bucket.

s3_transorm_s3.ipynb : contains various functions who import a grib2 file from a s3 bucket, turn it into different formats, and put it back to s3. This notebook was used to test the executions time fo such a process to optimize the deployment of a machine learning model on data sets located in a s3 bucket.

neural_network.ipynb : contains the code to overfit a neural model on a data set corresponding so a single time-step, plot some results and do the inference on the next 46 hours.

linear-regression.ipynb : contains the code to have the training performances of a simple linear regression.

Weights_NN_functions.ipynb : contains some useful functions to store the weight values (in files or variables) of a neural network after each batch, each epochs,...

Plot_TrueColor_ncdf4.py : python script to plot an approximated true-color GOES16 image, from ncdf4 files.

Plot_BT_grib2.py : python script to plot the variables values, from a grib2 file.

download_grib2files_py3.py : python script used to download all the 2017 grib2 files from the university of Utah website and put them in the s3 bucket 'remi'.
