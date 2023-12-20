import asyncio
import websockets
import json
import math
from sksurgerynditracker.nditracker import NDITracker
import numpy as np
from scipy.spatial.transform import Rotation as R
import socket

romfile_path_brain = "C:\\Users\\zzy12\\Documents\\Trackfile\\no-pivot.rom"
romfile_path_tool = "C:\\Users\\zzy12\\Documents\\Trackfile\\plate2.rom"
SETTINGS = {"tracker type": "polaris", "romfiles": [romfile_path_brain, romfile_path_tool]}
TRACKER = NDITracker(SETTINGS)
TRACKER.start_tracking()

tf_f1_to_marker = np.array([[1,  0,  0,  -106],
                   [0,  1,  0,  -52],
                   [0,  0,  1, 0],
                   [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
rot_y = np.array([[0,  0,  1,  0],
                   [0,  1,  0,  0],
                   [-1,  0,  0, 0],
                   [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])

async def update_tool(websocket, path):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            port_handles, timestamps, framenumbers, tracking, quality = TRACKER.get_frame()
            frame1 = tracking[0]
            if not np.isnan(tracking[1]).any():
                frame2 = tracking[1]
                print("Tool Tracked")

                #tf_o_to_marker = np.dot(tf_f1_to_marker, frame1)
                tf_o_to_marker = np.dot(frame1, tf_f1_to_marker)
                
                tf_marker_to_o = np.linalg.inv(tf_o_to_marker)

                #tf_marker_to_tool = np.dot(frame2, tf_marker_to_o)
                tf_marker_to_tool = np.dot(tf_marker_to_o, frame2)
                
                rotation_matrix = tf_marker_to_tool[:3, :3]
                euler_angles = R.from_matrix(rotation_matrix).as_euler('xyz', degrees=True)

                test1 = np.linalg.inv(frame1)
                test = np.dot(frame2, test1)
                print(test)

                position = {"x": tf_marker_to_tool[0, 3]/500, "y": -tf_marker_to_tool[1, 3]/500-0.05, "z": -tf_marker_to_tool[2, 3]/500}

                #position = {"x": tf_marker_to_tool[0, 3]/1000, "y": -tf_marker_to_tool[1, 3]/1000, "z": -tf_marker_to_tool[2, 3]/1000}
                #position = {"x": tf_marker_to_tool[0, 3]/1000, "y": -tf_marker_to_tool[1, 3]/1000, "z": -tf_marker_to_tool[2, 3]/1000}
                #position = {"x": test[2, 3]/1000, "y": -test[1, 3]/1000, "z": test[0, 3]/1000}
                rotation = {"x": 0, "y": 0, "z": 0}

                ###########################################c
                #mod_frame = np.dot(rot_y, tf_marker_to_tool)
                #position = {"x": mod_frame[1, 3]/1000, "y": mod_frame[0, 3]/1000, "z": mod_frame[2, 3]/1000+0.1}
                #position = {"x": tf_marker_to_tool[1, 3]/1000, "y": tf_marker_to_tool[2, 3]/1000, "z": -tf_marker_to_tool[0, 3]/1000}
                ###########################################

                message = {"position": position, "rotation": rotation}
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.1)
                #print(position)
        except websockets.ConnectionClosed as e:
            print(f"An error occurred: {e}")
            break
start_server = websockets.serve(update_tool, "10.203.41.101", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
