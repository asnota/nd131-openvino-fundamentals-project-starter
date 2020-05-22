# Project Write-Up

## 1. Explaining Custom Layers in OpenVINO™

Model Optimizer iterates through each layer of the input model and compares it to the list of known layers before building the IR (Intermediate Representation).
Each DL framework contains its own list of layers supported by OpenVino. 
If the layer is not supported, it is considered a custom layer by Model Optimizer.
The reason for a custom layer application might be a special mathemacal calculation contained in this layer, not available or heavy to achieve ith standard layers.
The conversion of custom layers differs regarding the framework of the input model. 
Let't focus on the process behind converting custom layers from TensorFlow (a framework of the input model from a current project).

There is three options for TensorFlow models with custom layers:

1) Registering those layers as extensions to the Model Optimizer. 
In this case, the Model Optimizer generates a valid and optimized IR.

2) For sub-graphs that should not be expressed with the analogous sub-graph in the IR, but another sub-graph, the Model Optimizer provides such an option. 
This feature is helpful for many TensorFlow models.

3) Experimental feature of registering definite sub-graphs of the model as those that should be offloaded to TensorFlow during inference. 
In this case, the Model Optimizer produces an Intermediate Representation that:

-Can be inferred only on CPU
-Reflects each sub-graph as a single custom layer in the IR
-It is designed only for the model with complex structure. In this case, the complex subgraphs are offloaded to TensorFlow to make sure that Model Optimizer and Inference Engine can successfully execute your model.
However, for each such subgraph, TensorFlow library is called that is not optimized for inference.
Then, the replacement of each subgraph begins with extension and a removal of its offloading to TensorFlow during inference until all the models are converted by Model Optimizer and inferred by Inference Engine only with the maximum performance.
 

## 2. Compare Model Performance

The SSD model used in this project might be run outside of the OpenVINO™ toolkit (https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb)
However for each inference a remote service, which hosts the model, must be requested at each single input, and each request inccur charges, either from per entry cloud charges or the price for maintaining the web endpoint.
The advantage throught the OpenVINO™ toolkit inference is not only in cutting of the costs related to a heavy web requests-based implementation, but also in a model speed.
By passing throught the Model Optimizer, the model might loose in accuracy, but gains in speed and CPU overload, which is crucial for IoT devices lacking the multiple GPUs and short in memory space.


## 3. Assess Model Use Cases

The application of the counter application may be used in many domains, such as security, marketing, management.
The implementation of the application in security context might help to detect any unauthorized intusion, creating the the alarm notifications for further human intervention.
In case of the marketing context, the app might help to define the flow of people in store sections, being compared with the number of items bought after the human venue.
The management use case implementation might help to control the activities of the personel in different sections of the building.  

## 4. Assess Effects on End User Needs

The ability of the model to detect a human being is dependent on the frame contast (lighting in the chamber) model accuracy and defined threshould, as well as from the image dimensions.
According to the user requirement some additional preprocessing steps might be necessary to adjust the input, so that the output of the model was in optimal limits.