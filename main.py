"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit person to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# python main.py -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm

# python main.py -m "resources/happy-person.png" -pt 0.6

import os
import sys
import time
import socket
import json
import cv2

import logging as log
import paho.mqtt.client as mqtt

from argparse import ArgumentParser
from inference import Network

# Variables
CPU_EXTENSION = "/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so"
# SDD_MODEL = "/home/workspace/ssd_mobilenet_v1_coco_2018_01_28/frozen_inference_graph.xml"
SDD_MODEL = "/home/workspace/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.xml"
VIDEO_PATH = "resources/Pedestrian_Detect_2_1_1.mp4"

# MQTT server environment variables
HOSTNAME = socket.gethostname()
IPADDRESS = socket.gethostbyname(HOSTNAME)
MQTT_HOST = IPADDRESS
MQTT_PORT = 3001
MQTT_KEEPALIVE_INTERVAL = 60


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", required=False, type=str,
                        default=SDD_MODEL,
                        help="Path to an xml file with a trained model.")
    parser.add_argument("-i", "--input", required=False, type=str,
                        default=VIDEO_PATH,
                        help="Path to image or video file")
    parser.add_argument("-l", "--cpu_extension", required=False, type=str,
                        default=CPU_EXTENSION,
                        help="MKLDNN (CPU)-targeted custom layers."
                             "Absolute path to a shared library with the"
                             "kernels impl.")
    parser.add_argument("-d", "--device", type=str, default="CPU",
                        help="Specify the target device to infer on: "
                             "CPU, GPU, FPGA or MYRIAD is acceptable. Sample "
                             "will look for a suitable plugin for device "
                             "specified (CPU by default)")
    parser.add_argument("-pt", "--prob_threshold", type=float, default=0.5,
                        help="Probability threshold for detections filtering"
                        "(0.5 by default)")
    return parser


def connect_mqtt():
    ### TODO: Connect to the MQTT client ###
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    return client

def ssd_output(frame, result, hist):
    current_count = 0
    for obj in result[0][0]:
        if obj[2] > prob_threshold:
            xmin = int(obj[3] * initial_width)
            ymin = int(obj[4] * initial_hight)
            xmax = int(obj[5] * initial_width)
            ymax = int(obj[6] * initial_hight)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 55, 255), 1)
            current_count = current_count + 1
			
			if current_count > 0:
                hist = 5
            elif (current_count == 0) and (hist > 0):
                current_count = 1
                hist += -1
				
    return frame, current_count, hist

def infer_on_stream(model, args, client):
        
    # Flag for a single image input
    single_image = False
    
    # Initialize variables for person count and start time
	hist = -1
    cur_request_id = 0
    last_count = 0
    total_count = 0
    start_time = 0
    
    # Declare global vars for intial frame's width and hight, along with probability threshold
    global initial_width, initial_hight, prob_threshold
    
    # Get probarility threshold from args
    prob_threshold = args.prob_threshold
    
    # Initialise the class
    infer_network = Network()
    
    ### TODO: Load the model through `infer_network` ###
    infer_network.load_model(model, args.device, args.cpu_extension)
    net_input_shape = infer_network.get_input_shape() # Input shape is  [1, 3, 300, 300]
        
    ### TODO: Handle the input stream ###    
    # Check the input
    if args.input == 'CAM':
        input_stream = 0
    elif args.input.endswith('.bmp') :
        single_image = True
        input_stream = args.input
    else:
        input_stream = args.input
        assert os.path.isfile(args.input), "Input file doesn't exist"
        
    # Get and open video capture
    cap = cv2.VideoCapture(input_stream)
    
    if input_stream:
        cap.open(args.input)
        
        #Grab the shape of the input
        initial_width = int(cap.get(3)) # Video width is 768
        initial_hight = int(cap.get(4)) # Video height is 432
       
    ### TODO: Loop until stream is over ###
    while cap.isOpened():       
        ### TODO: Read from the video capture ###
        flag, frame = cap.read()
        if not flag:
            break
        key_pressed = cv2.waitKey(60)
        
       
        ### TODO: Pre-process the image as needed ###
        p_frame = cv2.resize(frame, (net_input_shape[3], net_input_shape[2]))        
        p_frame = p_frame.transpose((2,0,1))       
        p_frame = p_frame.reshape(1, *p_frame.shape)
        
        ### TODO: Start asynchronous inference for specified request ###
        infer_network.exec_net(cur_request_id, p_frame)

        ### TODO: Wait for the result ###
        if infer_network.wait(cur_request_id) == 0:
                                    
            ### TODO: Get the results of the inference request ###
            result = infer_network.get_output(cur_request_id)
            
            # Apply a function to draw the boxes
            frame, current_count, hist = ssd_output(frame, result, hist)
            
            # A new person appears in a frame
            if current_count > last_count:

                # Get a time when a new person appears
                start_time = time.time()

                # Update total count of persons 
                total_count = total_count + current_count - last_count

                ### Topic "person": key of "total" (from "total" and "count") ###
                client.publish("person", json.dumps({"total": total_count}))

            # Duration of the person presence
            if current_count < last_count:
                # Substract a first moment a new person appeared from current time to get duration of the person presence in a frame
                duration = int(time.time() - start_time)

                ### Topic "person/duration": key of "duration" ###
                client.publish("person/duration", json.dumps({"duration": duration}))

            ### Topic "person": key of "count" (from "total" and "count") ###
            client.publish("person", json.dumps({"count": current_count}))
			
			# Update the persons count 
            last_count = current_count

			# Update request ID 
            #cur_request_id += 1 # 0 works well for this application		
            

        ### TODO: Send the frame to the FFMPEG server ###
        sys.stdout.buffer.write(frame)
        sys.stdout.flush()
    
        if key_pressed == 27:
            break
        
        ### TODO: Write an output image if `single_image_mode` ###
        if single_image:
            cv2.imwrite('resources/output_image.png', frame)
       
    # Release the capture and destroy any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()    
    client.disconnect()
        


def main():
    # Grab command line args
    args = build_argparser().parse_args()
    
    # Connect to the MQTT server
    client = connect_mqtt()
    
    # Perform inference on the input stream
    model = args.model
    infer_on_stream(model, args, client)

if __name__ == '__main__':
    main()
