# Deploy a People Counter App at the Edge

| Details            |              |
|-----------------------|---------------|
| Programming Language: |  Python 3.5 or 3.6 |

![people-counter-python](./images/people-counter-image.png)

## What it Does

The people counter application will demonstrate how to create a smart video IoT solution using Intel® hardware and software tools. The app will detect people in a designated area, providing the number of people in the frame, average duration of people in frame, and total count.

## How it Works

The counter will use the Inference Engine included in the Intel® Distribution of OpenVINO™ Toolkit. The model used should be able to identify people in a video frame. The app should count the number of people in the current frame, the duration that a person is in the frame (time elapsed between entering and exiting a frame) and the total count of people. It then sends the data to a local web server using the Paho MQTT Python package.

You will choose a model to use and convert it with the Model Optimizer.

![architectural diagram](./images/arch_diagram.png)

## Requirements

### Hardware

* 6th to 10th generation Intel® Core™ processor with Iris® Pro graphics or Intel® HD Graphics.
* OR use of Intel® Neural Compute Stick 2 (NCS2)
* OR Udacity classroom workspace for the related course

### Software

*   Intel® Distribution of OpenVINO™ toolkit 2019 R3 release
*   Node v6.17.1
*   Npm v3.10.10
*   CMake
*   MQTT Mosca server
  
        
## Setup

### Install Intel® Distribution of OpenVINO™ toolkit

Utilize the classroom workspace, or refer to the relevant instructions for your operating system for this step.

- [Linux/Ubuntu](./linux-setup.md)
- [Mac](./mac-setup.md)
- [Windows](./windows-setup.md)

### Install Nodejs and its dependencies

Utilize the classroom workspace, or refer to the relevant instructions for your operating system for this step.

- [Linux/Ubuntu](./linux-setup.md)
- [Mac](./mac-setup.md)
- [Windows](./windows-setup.md)

### Install npm

There are three components that need to be running in separate terminals for this application to work:

-   MQTT Mosca server 
-   Node.js* Web server
-   FFmpeg server
     
From the main directory:

* For MQTT/Mosca server:
   ```
   cd webservice/server
   npm install
   ```

* For Web server:
  ```
  cd ../ui
  npm install
  ```
  **Note:** If any configuration errors occur in mosca server or Web server while using **npm install**, use the below commands:
   ```
   sudo npm install npm -g 
   rm -rf node_modules
   npm cache clean
   npm config set registry "http://registry.npmjs.org"
   npm install
   ```

## Steps to convert SDD_mobilenet_v2 TF model into intermediate representation:

```
wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
```

```
tar -xvf ssd_mobilenet_v2_coco_2018_03_29.tar.gz
```

```
cd ssd_mobilenet_v2_coco_2018_03_29
```

```
export MOD_OPT=/opt/intel/openvino/deployment_tools/model_optimizer
export CUST_OPS=/opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf
python $MOD_OPT/mo.py --input_model frozen_inference_graph.pb --tensorflow_object_detection_api_pipeline_config pipeline.config --reverse_input_channels --tensorflow_use_custom_operations_config $CUST_OPS/ssd_v2_support.json
```

## Run the application

From the main directory:

### Step 1 - Start the Mosca server

```
cd webservice/server/node-server
node ./server.js
```

You should see the following message, if successful:
```
Mosca server started.
```

### Step 2 - Start the GUI

Open new terminal and run below commands.
```
cd webservice/ui
npm run dev
```

You should see the following message in the terminal.
```
webpack: Compiled successfully
```

### Step 3 - FFmpeg Server

Open new terminal and run the below commands.
```
sudo ffserver -f ./ffmpeg/server.conf
```

### Step 4 - Run the code

Open a new terminal to run the code. 

#### Setup the environment

You must configure the environment to use the Intel® Distribution of OpenVINO™ toolkit one time per session by running the following command:
```
source /opt/intel/openvino/bin/setupvars.sh -pyver 3.5
```

You should also be able to run the application with Python 3.6, although newer versions of Python will not work with the app.

#### Running on the CPU

When running Intel® Distribution of OpenVINO™ toolkit Python applications on the CPU, the CPU extension library is required. This can be found at: 

```
/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/
```

*Depending on whether you are using Linux or Mac, the filename will be either `libcpu_extension_sse4.so` or `libcpu_extension.dylib`, respectively.* (The Linux filename may be different if you are using a AVX architecture)

Though by default application runs on CPU, this can also be explicitly specified by ```-d CPU``` command-line argument:

```
python main.py -i resources/Pedestrian_Detect_2_1_1.mp4 -m your-model.xml -l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so -d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```
If you are in the classroom workspace, use the “Open App” button to view the output. If working locally, to see the output on a web based interface, open the link [http://0.0.0.0:3004](http://0.0.0.0:3004/) in a browser.

#### Running on the Intel® Neural Compute Stick

To run on the Intel® Neural Compute Stick, use the ```-d MYRIAD``` command-line argument:

```
python3.5 main.py -d MYRIAD -i resources/Pedestrian_Detect_2_1_1.mp4 -m your-model.xml -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```

To see the output on a web based interface, open the link [http://0.0.0.0:3004](http://0.0.0.0:3004/) in a browser.

**Note:** The Intel® Neural Compute Stick can only run FP16 models at this time. The model that is passed to the application, through the `-m <path_to_model>` command-line argument, must be of data type FP16.

#### Using a camera stream instead of a video file

To get the input video from the camera, use the `-i CAM` command-line argument. Specify the resolution of the camera using the `-video_size` command line argument.

For example:
```
python main.py -i CAM -m your-model.xml -l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so -d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```

To see the output on a web based interface, open the link [http://0.0.0.0:3004](http://0.0.0.0:3004/) in a browser.

**Note:**
User has to give `-video_size` command line argument according to the input as it is used to specify the resolution of the video or image file.

## A Note on Running Locally

The servers herein are configured to utilize the Udacity classroom workspace. As such,
to run on your local machine, you will need to change the below file:

```
webservice/ui/src/constants/constants.js
```

The `CAMERA_FEED_SERVER` and `MQTT_SERVER` both use the workspace configuration. 
You can change each of these as follows:

```
CAMERA_FEED_SERVER: "http://localhost:3004"
...
MQTT_SERVER: "ws://localhost:3002"
```

## A motivation for using OpenVINO™
### 1. Explaining Custom Layers in OpenVINO™

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
 

### 2. Compare Model Performance

The SSD model used in this project might be run outside of the OpenVINO™ toolkit (https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb)
However for each inference a remote service, which hosts the model, must be requested at each single input, and each request inccur charges, either from per entry cloud charges or the price for maintaining the web endpoint.
The advantage throught the OpenVINO™ toolkit inference is not only in cutting of the costs related to a heavy web requests-based implementation, but also in a model speed.
By passing throught the Model Optimizer, the model might loose in accuracy, but gains in speed and CPU overload, which is crucial for IoT devices lacking the multiple GPUs and short in memory space.


### 3. Assess Model Use Cases

The application of the counter application may be used in many domains, such as security, marketing, management.
The implementation of the application in security context might help to detect any unauthorized intusion, creating the the alarm notifications for further human intervention.
In case of the marketing context, the app might help to define the flow of people in store sections, being compared with the number of items bought after the human venue.
The management use case implementation might help to control the activities of the personel in different sections of the building.  

 ### 4. Assess Effects on End User Needs

The ability of the model to detect a human being is dependent on the fame contast (lighting in the chamber)? model accuracy and defined threshould, as ell as from the image dimensions.
According to the user requirement some additional preprocessing steps might be necessary to adjust the input, so that the output of the model was in optimal limits.