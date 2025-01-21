import socket
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font as tkFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import serial
import serial.tools.list_ports
from time import sleep
from time import sleep, time
import math
import serial
import datetime
import os
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import pickle
import joblib

#this is the file for seperated hardware detectors, calculate the acceleration and real-time displacement

class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Integration")
        self.ports = [port.device for port in serial.tools.list_ports.comports()]

        # Set the initial size and position of the popup window
        self.width = 1000
        self.height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Configure the grid to be expandable
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Create a frame
        self.frame1 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width / 3, height=self.height / 2)
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame2 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width * 2 / 3, height=self.height / 2)
        self.frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


        self.frame3 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width / 3, height=self.height / 2)
        self.frame3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.frame4 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width * 2 / 3, height=self.height / 2)
        self.frame4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.frame4.grid_propagate(False)
        label4 = tk.Label(self.frame4, text="Section 4")
        label4.place(relx=0.5, rely=0.5, anchor='center')
        self.start_button = tk.Button(self.frame2, text="Game Start", command=self.game_Start, width=15, height=1,
                                      font=("Helvetica", 12))
        self.start_button.place(relx=0.7, rely=0.15, anchor='center')

        self.imu_thread = threading.Thread(target=self.initial_IMU)
        self.emg_thread = threading.Thread(target=self._initialise_EMG_graph)
        self.emg_thread.start()
        self.imu_thread.start()



        self.emg_data_1 = [-1] * 41
        self.emg_data_2 = [-1] * 41

        #self.initial_IMU()
        #self._initialise_EMG_graph()
        self.display_IMU_thread=threading.Thread(target=self.update_display)
        self.display_EMG_thread=threading.Thread(target=self.EMG_Display)

    def send_command_to_unity(self,command):
        host = '127.0.0.1'  # Unity服务器的IP地址
        port = 65432  # Unity服务器监听的端口

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(command.encode())
            response = s.recv(1024)
            print('Received', repr(response))



    def initial_IMU(self):
        # Serial Port Setup
        if'COM6' in self.ports:#port maybe different on different laptop

            self.label2 = tk.Label(self.frame2, text="Port: COM6 ")
            self.label2.place(relx=0.35, rely=0.8, anchor='center')
            self.label1 = tk.Label(self.frame2,
                                   text="click the Connect button to see the animation",
                                   wraplength=self.width / 2)
            self.label1.place(relx=0.5, rely=0.9, anchor='center')
            # Add a button to start data transmission
            self.start_buttonConnect = tk.Button(self.frame2, text="connect", command=self.start_data_transmission)
            self.start_buttonConnect.place(relx=0.5, rely=0.8, anchor='center')

            self.start_buttonDisConnect = tk.Button(self.frame2, text="Disconnect", command=self.disconnect)
            self.start_buttonDisConnect.place(relx=0.7, rely=0.8, anchor='center')

        else:
            print("IMU is not connected")
            self.label2 = tk.Label(self.frame2, text="Port: None ")
            self.label2.place(relx=0.35, rely=0.8, anchor='center')
            self.label1 = tk.Label(self.frame2,
                                   text="Please check the IUM connection",
                                   wraplength=self.width / 2)
            self.label1.place(relx=0.5, rely=0.9, anchor='center')

        sleep(1)

        # Conversions

        self.quaternionsList=[]
        self.accelerations=[]
        self.transmitting = False
        self.toRad = 2 * np.pi / 360
        self.toDeg = 1 / self.toRad

        # Initialize Parameters
        self.count = 0
        self.averageroll = 0
        self.averageyaw = 0
        self.averagepitch = 0
        self.averageemg = 0
        self.iterations = 10  # EMG measurements to get average

        # Create a figure for the 3D plot
        self.fig = Figure(figsize=((self.width / 300), (self.height / 200)))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Set Limits
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_zlim(-2, 2)

        # Set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z',labelpad=0)

        # Draw Axes
        self.ax.quiver(0, 0, 0, 2, 0, 0, color='red', label='X-Axis', arrow_length_ratio=0.1)  # X Axis (Red)
        self.ax.quiver(0, 0, 0, 0, -2, 0, color='green', label='Y-Axis', arrow_length_ratio=0.1)  # Y Axis (Green)
        self.ax.quiver(0, 0, 0, 0, 0, 4, color='blue', label='Z-Axis', arrow_length_ratio=0.1)  # Z Axis (Blue)

        # Draw the board as a rectangular prism (solid)
        self.prism_vertices = np.array([
            [-1.5, -1, 0], [1.5, -1, 0], [1.5, 1, 0], [-1.5, 1, 0],  # bottom vertices
            [-1.5, -1, 0.1], [1.5, -1, 0.1], [1.5, 1, 0.1], [-1.5, 1, 0.1]
            # top vertices (height=0.1 for visual thickness)
        ])

        self.prism_faces = [
            [self.prism_vertices[j] for j in [0, 1, 2, 3]],  # bottom face
            [self.prism_vertices[j] for j in [4, 5, 6, 7]],  # top face
            [self.prism_vertices[j] for j in [0, 1, 5, 4]],  # side face
            [self.prism_vertices[j] for j in [1, 2, 6, 5]],  # side face
            [self.prism_vertices[j] for j in [2, 3, 7, 6]],  # side face
            [self.prism_vertices[j] for j in [3, 0, 4, 7]]  # side face
        ]

        self.prism_collection = Poly3DCollection(self.prism_faces, facecolors='gray', linewidths=1, edgecolors='black',
                                                 alpha=0.25)
        self.ax.add_collection3d(self.prism_collection)

        # Front Arrow (Purple)
        self.front_arrow, = self.ax.plot([0, 2], [0, 0], [0, 0], color='purple', marker='o', markersize=10,
                                         label='Front Arrow')

        # Up Arrow (Magenta)
        self.up_arrow, = self.ax.plot([0, 0], [0, -1], [0, 1], color='magenta', marker='o', markersize=10,
                                      label='Up Arrow')

        # Side Arrow (Orange)
        self.side_arrow, = self.ax.plot([0, 1], [0, -1], [0, 1], color='orange', marker='o', markersize=10,
                                        label='Side Arrow')

        # Create a canvas to draw on
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame1)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create a label for average EMG
        # self.emg_label = tk.Label(self.frame1, text="Average EMG: 0", font=("Arial", 14))
        # self.emg_label.pack(pady=10)

        self.roll_label = tk.Label(self.frame2, text="roll is : " )
        self.roll_label.config(font=("Arial", 12))
        self.roll_label.place(relx=0.2, rely=0.3, anchor='w')
        self.pitch_label = tk.Label(self.frame2, text="pitch is : " )
        self.pitch_label.config(font=("Arial", 12))
        self.pitch_label.place(relx=0.2, rely=0.4, anchor='w')
        self.yaw_label = tk.Label(self.frame2, text="yaw is : " )
        self.yaw_label.config(font=("Arial", 12))
        self.yaw_label.place(relx=0.2, rely=0.5, anchor='w')


        self.left_label = tk.Label(self.frame2, text="left is : ")
        self.left_label.config(font=("Arial", 12))
        self.left_label.place(relx=0.2, rely=0.6, anchor='w')
        self.up_label = tk.Label(self.frame2, text="up is : ")
        self.up_label.config(font=("Arial", 12))
        self.up_label.place(relx=0.2, rely=0.7, anchor='w')
        self.forward_label = tk.Label(self.frame2, text="forward is : ")
        self.forward_label.config(font=("Arial", 12))
        self.forward_label.place(relx=0.2, rely=0.8, anchor='w')





    def _initialise_EMG_graph(self):
        if 'COM5' in self.ports:#port maybe different on different laptop

            self.label2 = tk.Label(self.frame3, text="Port: COM5 ")
            self.label2.place(relx=0.23, rely=0.8, anchor='center')
            self.label1 = tk.Label(self.frame3,
                                   text="click the Connect button to see the animation",
                                   wraplength=self.width / 2)
            self.label1.place(relx=0.5, rely=0.9, anchor='center')
            # Add a button to start data transmission
            self.start_button = tk.Button(self.frame3, text="connect", command=self.start_EMG_data_transmission)
            self.start_button.place(relx=0.45, rely=0.8, anchor='center')

            self.start_button = tk.Button(self.frame3, text="Disconnect", command=self.EMG_disconnect)
            self.start_button.place(relx=0.7, rely=0.8, anchor='center')



        else:
            print("EMG is not connected")
            self.label2 = tk.Label(self.frame3, text="Port: None ")
            self.label2.place(relx=0.35, rely=0.8, anchor='center')
            self.label1 = tk.Label(self.frame3,
                                   text="Please check the IUM connection",
                                   wraplength=self.width / 2)
            self.label1.place(relx=0.5, rely=0.9, anchor='center')

     # Create a figure and axis
        self.EMG_transmitting = False
        self.start = False
        fig = Figure(figsize=((self.width / 200), (self.height / 200)))  # Adjusting figsize based on frame size
        self.ax1 = fig.add_subplot(111)

        self.ax1.set_title("Electromyography Envelope", fontsize=14, pad=0)


        self.ax1.set_xlim(0, 5)
        self.ax1.set_ylim(0, 5)

        self.ax1.set_xlabel("Sample(20 samples per second)",fontsize=8,labelpad=-2)
        self.ax1.set_ylabel("Magnitude",labelpad=0)

        self.ax1.set_xticks(np.arange(0, 41, 8))
        self.ax1.set_yticks(np.arange(0, 1001, 200))

        for x_tick in self.ax1.get_xticks():
            self.ax1.axvline(x_tick, color='gray', linestyle='--', linewidth=0.5)
        for y_tick in self.ax1.get_yticks():
            self.ax1.axhline(y_tick, color='gray', linestyle='--', linewidth=0.5)




            # Plot two lines
        self.line1, = self.ax1.plot([], [], color='red', label='Outer Wrist Muscle (Extensor Carpi Ulnaris)')
        self.line2, = self.ax1.plot([], [], color='blue', label='Inner Wrist Muscle (Flexor Carpi Radialis)')
        self.ax1.legend(fontsize=9, loc='upper right')




            # Embed the plot in the tkinter frame
        self.canvas1 = FigureCanvasTkAgg(fig, master=self.frame4)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.EMG_Display()

        self.outer_EMG_label = tk.Label(self.frame3, text=f"EMG for Extensor Carpi Ulnaris is :")
        self.outer_EMG_label.config(font=("Arial", 12))
        self.outer_EMG_label.place(relx=0.1, rely=0.2, anchor='w')
        self.outer_EMG_Number = tk.Label(self.frame3, text="",fg="red")
        self.outer_EMG_Number.config(font=("Arial", 12))
        self.outer_EMG_Number.place(relx=0.2, rely=0.3, anchor='w')
        self.inner_EMG_label = tk.Label(self.frame3, text=f"EMG for Flexor Carpi Radialis is :")
        self.inner_EMG_label.config(font=("Arial", 12))
        self.inner_EMG_label.place(relx=0.1, rely=0.4, anchor='w')
        self.inner_EMG_Number = tk.Label(self.frame3, text="",fg="blue")
        self.inner_EMG_Number.config(font=("Arial", 12))
        self.inner_EMG_Number.place(relx=0.2, rely=0.5, anchor='w')
        self.gesture_label = tk.Label(self.frame3, text=f"Gesture is :")
        self.gesture_label.config(font=("Arial", 12))
        self.gesture_label.place(relx=0.1, rely=0.6, anchor='w')
        self.gesture_predict = tk.Label(self.frame3, text="")
        self.gesture_predict.config(font=("Arial", 12))
        self.gesture_predict.place(relx=0.2, rely=0.7, anchor='w')
        self.a, self.b = self.load_Function()





    def start_data_transmission(self):
        # Set the transmitting flag to True and start the update loop
        self.arduino = serial.Serial('COM6', 115200)
        self.transmitting = True
        self.update_display()

    def start_EMG_data_transmission(self):
        # Set the transmitting flag to True and start the update loop
        self.arduino_EMG = serial.Serial('COM5', 9600, timeout=1)
        self.EMG_transmitting = True
        self.EMG_Display()

    def game_Start(self):
        self.root.destroy()  # Close the welcome window
        new_root = tk.Tk()
        app = gameScreen(new_root)
        new_root.mainloop()

    def disconnect(self):
        self.transmitting = False
        self.root.after_cancel(self.update_display_id)
        if self.arduino is not None:
            self.arduino.close()
            self.arduino = None

    def EMG_disconnect(self):
        self.EMG_transmitting = False
        self.start =False
        self.root.after_cancel(self.EMG_display_id)
        if self.arduino_EMG is not None:
            self.arduino_EMG.close()
            self.arduino_EMG = None



    def update_display(self):
        if self.transmitting:
            try:
                while ((self.arduino.inWaiting() > 0)and
                       (self.transmitting==True)):
                    dataPacket = self.arduino.readline()
                    dataPacket = dataPacket.decode()
                    cleandata = dataPacket.replace("\r\n", "")
                    row = cleandata.strip().split(',')

                    if len(row) == 9:
                        splitPacket = cleandata.split(',')

                        emg = float(splitPacket[0])  # EMG sensor data
                        q0 = float(splitPacket[1])  # qw
                        q1 = float(splitPacket[2])  # qx
                        q2 = float(splitPacket[3])  # qy
                        q3 = float(splitPacket[4])  # qz
                        qs = [q0, q1, q2, q3]
                        #print(f"qs :{qs}")
                        self.quaternionsList.append(qs)
                        if(len(self.quaternionsList)>3):
                            self.quaternionsList.pop(0)


                        quaternionsArray = np.array(self.quaternionsList)
                        dt = 0.1  # 时间间隔
                        position_vector = [1, 0, 0]  # 位置矢量

                        motion = QuaternionMotion(quaternionsArray, dt, position_vector)
                        linear_acceleration = motion.linear_acceleration()
                        print("acceleration: ", linear_acceleration)
                        self.accelerations.append(linear_acceleration)
                        if(len(self.accelerations)>3):
                            self.accelerations.pop(0)
                        accelerationsArray = np.array(self.accelerations)
                        displacement=self.calculate_displacement(accelerationsArray,dt)

                        displacement_array = np.array(displacement)
                        combined_displacement = np.sum(displacement_array, axis=0)
                        print(f"combined_displacement :{combined_displacement}")



                        # Calculate Angles
                        roll = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))
                        pitch = -math.asin(2 * (q0 * q2 - q3 * q1))
                        yaw = -math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))

                        self.roll_label.config( text="roll is : "+str(roll))
                        self.pitch_label.config(text="pitch is : "+str(pitch))
                        self.yaw_label.config(text="yaw is : "+str(yaw))

                        up=roll*90/2.6
                        if(up>35):
                            left = -yaw * 90 / 1.5
                        if(35>up>0):
                            left = -yaw * 90 / 2.26
                        if(up<0):
                            left = -yaw * 90 / 2


                        self.left_label.config(text="left : "+str(combined_displacement))
                        #self.up_label.config(text="up is : "+str(displacement))



                        # Rotation matrices
                        Rz = np.array([
                            [np.cos(yaw), -np.sin(yaw), 0],
                            [np.sin(yaw), np.cos(yaw), 0],
                            [0, 0, 1]
                        ])

                        Ry = np.array([
                            [np.cos(pitch), 0, np.sin(pitch)],
                            [0, 1, 0],
                            [-np.sin(pitch), 0, np.cos(pitch)]
                        ])

                        Rx = np.array([
                            [1, 0, 0],
                            [0, np.cos(roll), -np.sin(roll)],
                            [0, np.sin(roll), np.cos(roll)]
                        ])

                        R = Rz @ Ry @ Rx  # Combined rotation matrix

                        # Apply the rotation
                        rotated_vertices = (R @ self.prism_vertices.T).T

                        prism_faces_rotated = [
                            [rotated_vertices[j] for j in [0, 1, 2, 3]],  # bottom face
                            [rotated_vertices[j] for j in [4, 5, 6, 7]],  # top face
                            [rotated_vertices[j] for j in [0, 1, 5, 4]],  # side face
                            [rotated_vertices[j] for j in [1, 2, 6, 5]],  # side face
                            [rotated_vertices[j] for j in [2, 3, 7, 6]],  # side face
                            [rotated_vertices[j] for j in [3, 0, 4, 7]]   # side face
                        ]

                        # Update the collection
                        self.prism_collection.set_verts(prism_faces_rotated)

                        # Update Arrows
                        k = np.array([np.cos(yaw) * np.cos(pitch), np.sin(pitch), np.sin(yaw) * np.cos(pitch)])  # X vector
                        y = np.array([0, 1, 0])  # Y vector: pointing down
                        s = np.cross(k, y)  # Side vector
                        v = np.cross(s, k)  # Up vector
                        vrot = v * np.cos(roll) + np.cross(k, v) * np.sin(roll)  # Rotated Up vector

                        self.front_arrow.set_data([0, k[0] * 2], [0, k[1] * 2])
                        self.front_arrow.set_3d_properties([0, k[2] * 2])
                        self.up_arrow.set_data([0, vrot[0] * 1], [0, vrot[1] * 1])
                        self.up_arrow.set_3d_properties([0, vrot[2] * 1])
                        self.side_arrow.set_data([0, s[0] * 1], [0, s[1] * 1])
                        self.side_arrow.set_3d_properties([0, s[2] * 1])

                        # Update canvas
                        self.canvas.draw()

                        self.averageroll += roll * self.toDeg
                        self.averageyaw += yaw * self.toDeg
                        self.averagepitch += pitch * self.toDeg
                        self.averageemg += emg

                        if self.count == self.iterations:
                            self.averageroll = self.averageroll / self.iterations
                            self.averageyaw = self.averageyaw / self.iterations
                            self.averagepitch = self.averagepitch / self.iterations
                            self.averageemg = self.averageemg / self.iterations

                            self.averageroll = round(self.averageroll)
                            self.averageyaw = round(self.averageyaw)
                            self.averagepitch = round(self.averagepitch)

                            # Print the averaged results
                            print("iterations:", self.iterations)
                            print("averageroll is", self.averageroll)
                            print("averageyaw is", self.averageyaw)
                            print("averagepitch is", self.averagepitch)
                            print("averageemg=", self.averageemg)

                            self.count = 0

                            self.averageyaw = 0
                            self.averageroll = 0
                            self.averagepitch = 0
                            self.averageemg = 0
                        else:
                            self.count += 1

                        # Update EMG Label
                        #self.emg_label.config(text=f"Average EMG: {self.averageemg:.2f}")

            except Exception as e:
                print(f"An error occurred: {e}")

            # Call update_display() again after 50 milliseconds
            self.update_display_id =self.root.after(50, self.update_display)

    def EMG_Display(self):
        if self.EMG_transmitting:
            try:
             while ((self.arduino_EMG.inWaiting() > 0) and
                       (self.EMG_transmitting == True)):
                data = self.arduino_EMG.readline()
                emg_data = self._decode(data)
                if emg_data is not None:
                    #print(f"EMG 1: {emg_data[0]} , EMG 2: {emg_data[1]}")


                    self.outer_EMG_Number.config(text=f"{emg_data[0]}")
                    self.inner_EMG_Number.config(text=f"{emg_data[1]}")
                    data=[emg_data[0],emg_data[1]]
                    predictions = self.predict(data,self.a,self.b)
                    ges_predictions = None
                    if predictions is not None:
                        if predictions==-1:
                            ges_predictions="Hand Open"
                        if predictions==1:
                            ges_predictions="Hand Close"
                        if predictions==0 :
                            ges_predictions="Unknown"
                    self.gesture_predict.config(text=f"{ges_predictions}")





                    # Append the new data to the lists

                    self.emg_data_1.append(emg_data[0])
                    self.emg_data_1.pop(0)
                    self.emg_data_2.append(emg_data[1])
                    self.emg_data_2.pop(0)

                    # Update the line data to shift the line from right to left
                    self.line1.set_data(range(len(self.emg_data_1)), self.emg_data_1)
                    self.line2.set_data(range(len(self.emg_data_2)), self.emg_data_2)

                    # Redraw the canvas
                    self.canvas1.draw()  # Redraw the canvas

            except Exception as e:
                print(f"An error occurred: {e}")


            # Call update_display() again after 50 milliseconds
            self.EMG_display_id=self.root.after(1, self.EMG_Display)

    def _decode(self, serial_data):
        serial_string = serial_data.decode(errors="ignore")
        adc_string_1 = ""
        adc_string_2 = ""
        self.adc_values = [0, 0]
        if '\n' in serial_string:
            # remove new line character
            serial_string = serial_string.replace("\n", "")
            if serial_string != '':
                # Convert number to binary, placing 0s in empty spots
                serial_string = format(int(serial_string, 10), "024b")

                # Separate the input number from the data
                for i0 in range(0, 12):
                    adc_string_1 += serial_string[i0]
                for i0 in range(12, 24):
                    adc_string_2 += serial_string[i0]

                self.adc_values[0] = int(adc_string_1, base=2)
                self.adc_values[1] = int(adc_string_2, base=2)

                return self.adc_values

    def load_Function(self,filename='trained.txt'):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    raise ValueError("File content is insufficient to read the vertical line parameters.")

                a = float(lines[0].strip())
                b = float(lines[1].strip())
                print(f"a is {a}, b is {b}")

                return a,b

        except FileNotFoundError:
            raise FileNotFoundError(f"The file {filename} does not exist.")
        except ValueError as e:
            raise ValueError(f"Error reading the file: {e}")

    def predict(self, point,a,b):
        """判断点是否在垂直线的左侧或右侧"""
        x, y = point
        # 计算点的y值与垂直线的y值比较
        line_y = a * x + b
        if y < line_y:
            return -1  # 点在垂直线的左侧
        elif y > line_y:
            return 1  # 点在垂直线的右侧
        else:
            return 0  # 点在垂直线上（可选）

    def calculate_displacement(self,acceleration, dt):
        velocity = np.zeros_like(acceleration)
        velocity[1:] = np.cumsum(acceleration[:-1] * dt, axis=0)

        # 计算位移（通过对速度进行积分）
        displacement = np.zeros_like(velocity)
        displacement[1:] = np.cumsum(velocity[:-1] * dt, axis=0)

        return displacement[1:]  # 返回位移结果，去掉初始化的零位移

class QuaternionMotion:
    def __init__(self, quaternions, dt, position_vector):
        self.quaternions = quaternions
        self.dt = dt
        self.position_vector = np.array(position_vector)

    def quaternion_derivative(self):
        q_next = self.quaternions[1:]
        q_prev = self.quaternions[:-1]
        dq_dt = (q_next - q_prev) / self.dt
        return dq_dt

    def angular_velocity(self):
        dq_dt = self.quaternion_derivative()
        angular_velocities = []
        for i in range(len(dq_dt)):
            q = self.quaternions[i]
            q_conj = np.array([q[0], -q[1], -q[2], -q[3]])  # 四元数的共轭

            # 四元数微分公式来计算角速度
            omega_quat = 2 * self.quaternion_multiply(q_conj, dq_dt[i])
            omega = omega_quat[1:]  # 提取角速度的向量部分
            angular_velocities.append(omega)
        return np.array(angular_velocities)

    def quaternion_multiply(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        ])

    def angular_acceleration(self):
        omega = self.angular_velocity()
        omega_next = omega[1:]
        omega_prev = omega[:-1]
        alpha = (omega_next - omega_prev) / self.dt
        return alpha

    def linear_acceleration(self):
        alpha = self.angular_acceleration()
        linear_accelerations = np.cross(alpha, self.position_vector)
        return linear_accelerations

class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome")
        self.width = 1000
        self.height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Configure the grid to be expandable
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        try:
            self.bg_image = Image.open("backGrond.jpg")
            print("Image loaded successfully")
            self.bg_image = self.bg_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)

            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading image: {e}")

        #self.frame1 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width, height=self.height)
        #self.frame1.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        #self.button1 = tk.Button(self.frame1, text="Start", command=self.startButton)
        #self.button1.place(relx=0.5, rely=0.8, anchor='center')
        self.button1 = tk.Button(self.root, text="Start", command=self.startButton,width=18,
                                             height=2, font=("Helvetica", 15))
        self.button1.place(relx=0.8, rely=0.8, anchor='center')  # Position the button relative to the root window

    def startButton(self):
        self.root.destroy()  # Close the welcome window
        new_root = tk.Tk()
        app = trainingInterface(new_root)
        new_root.mainloop()

class trainingInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("preparation Interface")
        self.width = 1000
        self.height = 600
        self.width = 1000
        self.height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.ports = [port.device for port in serial.tools.list_ports.comports()]

        # Configure the grid to be expandable
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)


        # Create a frame
        self.frame1 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width, height=(self.height *2/ 3))
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


        self.frame2 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width, height=self.height *1/ 3)
        self.frame2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.initialEMGTraining()
        if 'COM5' in self.ports:

            self.emg_data_1 = [-1] * 41
            self.emg_data_2 = [-1] * 41
            self.savingData=[]
            self.openHandButton=tk.Button(self.frame2,text="Hand Open",command=self.EMG_connect_HandOpen,width=15, height=2,font=("Helvetica", 12))
            self.openHandButton.place(relx=0.3, rely=0.3, anchor='center')
            self.handCloseButton=tk.Button(self.frame2,text="Hand Close",command=self.handCloseButton,width=15, height=2,font=("Helvetica", 12))
            self.handCloseButton.place(relx=0.7, rely=0.3, anchor='center')
            self.gameStartButton = tk.Button(self.frame2, text="Start", command=self.startButton, width=15,
                                         height=2,font=("Helvetica", 12))
            self.gameStartButton.place(relx=0.5, rely=0.5, anchor='center')
        if 'COM5' not in self.ports:
            self.label=tk.Label(self.frame2, text="No EMG device found, Please check the hardware connection",font=("Helvetica", 15))
            self.label.place(relx=0.5, rely=0.3, anchor='center')
            self.gameStartButton = tk.Button(self.frame2, text="Start", command=self.startButton, width=15,
                                             height=2, font=("Helvetica", 12))
            self.gameStartButton.place(relx=0.5, rely=0.5, anchor='center')

    def startButton(self):
        self.root.destroy()  # Close the welcome window
        new_root = tk.Tk()
        app = Window(new_root)
        new_root.mainloop()

    def EMG_connect_HandOpen(self):
        self.arduino_EMG = serial.Serial('COM5', 9600, timeout=1)
        gesture = "handOpen"
        self.start_countdown(11)
        self.displayAndsaveDate()


    def handCloseButton(self):
        self.arduino_EMG = serial.Serial('COM5', 9600, timeout=1)
        gesture = "handOpen"
        self.start_countdown_close(11)
        self.displayAndsaveDate()


    def EMG_disconnect(self):
        if self.arduino_EMG is not None:
            self.arduino_EMG.close()
            self.arduino_EMG = None

    def start_countdown(self, count):
        if count > 0:
            self.startSave=True
            if count<11:
             self.openHandButton.config(text=str(count))
            self.frame2.after(1000, self.start_countdown, count - 1)
        else:
            self.openHandButton.config(text="Hand Open")
            self.startSave = False
            self.savedDataOpen = []
            for i in self.savingData:
                self.savedDataOpen.append(i)
            print(f"open: {self.savedDataOpen}")
            self.savingData.clear()
            self.EMG_disconnect()

    def start_countdown_close(self, count):
        if count > 0:
            self.startSave=True
            if count<11:
             self.handCloseButton.config(text=str(count))
            self.frame2.after(1000, self.start_countdown_close, count - 1)
        else:
            self.handCloseButton.config(text="Hand Close")
            self.startSave = False
            self.savedDataClose=[]
            for i in self.savingData:
             self.savedDataClose.append(i)
            self.savingData.clear()
            print(f"close:{self.savedDataClose}")
            self.EMG_disconnect()
            self.trainData()

    def displayAndsaveDate(self):
        if self.startSave:
            try:
                while self.arduino_EMG.inWaiting() > 0:
                    data = self.arduino_EMG.readline()
                    emg_data = self._decode(data)

                    if emg_data is not None:
                        # Append the new data to the lists and update plot data
                        self.emg_data_1.append(emg_data[0])
                        self.emg_data_1.pop(0)
                        self.emg_data_2.append(emg_data[1])
                        self.emg_data_2.pop(0)

                        if self.startSave:
                            self.savingData.append([emg_data[0], emg_data[1]])

                        # Update the line data to shift the line from right to left
                        self.line1.set_data(range(len(self.emg_data_1)), self.emg_data_1)
                        self.line2.set_data(range(len(self.emg_data_2)), self.emg_data_2)

                        # Redraw the canvas
                        self.canvas1.draw()

            except (OSError, ValueError, IndexError) as e:
                print(f"An error occurred: {e}")

            # Schedule the next update
            self.EMG_display_id = self.root.after(10, self.displayAndsaveDate)

    def initialEMGTraining(self):
        self.EMG_transmitting = False
        fig = Figure(figsize=(self.frame1.winfo_width() / 100, self.frame1.winfo_height() / 100))
        self.ax1 = fig.add_subplot(111)

        self.ax1.set_title("Electromyography Envelope", fontsize=14, pad=0)
        self.ax1.set_xlim(0, 5)
        self.ax1.set_ylim(0, 5)
        self.ax1.set_xlabel("Sample (20 samples per second)", fontsize=8, labelpad=-2)
        self.ax1.set_ylabel("Magnitude", labelpad=0)
        self.ax1.set_xticks(np.arange(0, 41, 8))
        self.ax1.set_yticks(np.arange(0, 1001, 200))

        for x_tick in self.ax1.get_xticks():
            self.ax1.axvline(x_tick, color='gray', linestyle='--', linewidth=0.5)
        for y_tick in self.ax1.get_yticks():
            self.ax1.axhline(y_tick, color='gray', linestyle='--', linewidth=0.5)

        self.line1, = self.ax1.plot([], [], color='red', label='Outer Wrist Muscle (Extensor Carpi Ulnaris)')
        self.line2, = self.ax1.plot([], [], color='blue', label='Inner Wrist Muscle (Flexor Carpi Radialis)')
        self.ax1.legend(fontsize=9, loc='upper right')

        # Embed the plot in the tkinter frame
        self.canvas1 = FigureCanvasTkAgg(fig, master=self.frame1)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bind the resizing event to the figure update
        self.frame1.bind("<Configure>", self.on_frame_resize)

    def on_frame_resize(self, event):
        width = self.frame1.winfo_width()
        height = self.frame1.winfo_height()
        self.canvas1.get_tk_widget().config(width=width, height=height)
        self.canvas1.draw()

    '''
    Train Data
    '''

    def trainData(self):
        # 删除文件 'trained.txt'，如果存在
        if os.path.exists('trained.txt'):
            os.remove('trained.txt')

        if (self.savedDataClose != []) and (self.savedDataOpen != []):
            vertical_line = Algorithm(self.savedDataClose, self.savedDataOpen)
            print(f"垂直线方程: y = {vertical_line.a}x + {vertical_line.b}")

            # 创建新的 'trained.txt' 文件并写入内容
            with open('trained.txt', 'w') as file:
                file.write(f"{vertical_line.a}\n")
                file.write(f"{vertical_line.b}\n")

            test_points = [[2, 5], [3, 3], [4, 1]]
            for point in test_points:
                position = vertical_line.predict(point)
                print(f"点 {point} 在垂直线的 {'左侧' if position == -1 else '右侧' if position == 1 else '上面/下面'}")

            return vertical_line

    def _decode(self, serial_data):
        serial_string = serial_data.decode(errors="ignore")
        adc_string_1 = ""
        adc_string_2 = ""
        self.adc_values = [0, 0]
        if '\n' in serial_string:
            # remove new line character
            serial_string = serial_string.replace("\n", "")
            if serial_string != '':
                # Convert number to binary, placing 0s in empty spots
                serial_string = format(int(serial_string, 10), "024b")

                # Separate the input number from the data
                for i0 in range(0, 12):
                    adc_string_1 += serial_string[i0]
                for i0 in range(12, 24):
                    adc_string_2 += serial_string[i0]

                self.adc_values[0] = int(adc_string_1, base=2)
                self.adc_values[1] = int(adc_string_2, base=2)

                return self.adc_values


class Algorithm:
    def __init__(self, list1, list2):
        self.a, self.b = self.calculate_line_equation(list1, list2)

    def calculate_average(self, lst):
        """计算列表中点的平均坐标"""
        n = len(lst)
        if n == 0:
            return (0, 0)
        sum_x = sum(point[0] for point in lst)
        sum_y = sum(point[1] for point in lst)
        return (sum_x / n, sum_y / n)

    def calculate_line_equation(self, list1, list2):
        """计算垂直线方程 y = ax + b"""
        avg1 = self.calculate_average(list1)
        avg2 = self.calculate_average(list2)

        x1, y1 = avg1
        x2, y2 = avg2

        # 计算斜率
        if x1 == x2:
            raise ValueError("垂直线的斜率是未定义的，因为两个点在同一垂直线上。")

        slope = (y2 - y1) / (x2 - x1)

        # 垂直线的斜率是原斜率的负倒数
        perpendicular_slope = -1 / slope

        # 使用点斜式方程 y - y1 = m(x - x1) 转换为 y = ax + b 的形式
        a = perpendicular_slope
        b = y1 - a * x1

        return a, b

    def predict(self, point):
        """判断点是否在垂直线的左侧或右侧"""
        x, y = point
        # 计算点的y值与垂直线的y值比较
        line_y = self.a * x + self.b
        if y < line_y:
            return -1  # 点在垂直线的左侧
        elif y > line_y:
            return 1  # 点在垂直线的右侧
        else:
            return 0  # 点在垂直线上（可选）

class gameScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("game Interface")
        self.width = 1000
        self.height = 600
        self.width = 1000
        self.height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.ports = [port.device for port in serial.tools.list_ports.comports()]

        # Configure the grid to be expandable
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Create a frame
        self.frame1 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width, height=(self.height * 1 / 2))
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame2 = tk.Frame(self.root, borderwidth=1, relief="solid", width=self.width, height=self.height * 1 / 2)
        self.frame2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        if 'COM5' in self.ports :
            self.last_printEMG_time = time()
            self.arduino_EMG = serial.Serial('COM5', 9600, timeout=1)
            self.outer_EMG_label = tk.Label(self.frame2, text=f"EMG for Extensor Carpi Ulnaris is :")
            self.outer_EMG_label.config(font=("Arial", 12))
            self.outer_EMG_label.place(relx=0.1, rely=0.2, anchor='w')
            self.outer_EMG_Number = tk.Label(self.frame2, text="", fg="red")
            self.outer_EMG_Number.config(font=("Arial", 12))
            self.outer_EMG_Number.place(relx=0.2, rely=0.3, anchor='w')
            self.inner_EMG_label = tk.Label(self.frame2, text=f"EMG for Flexor Carpi Radialis is :")
            self.inner_EMG_label.config(font=("Arial", 12))
            self.inner_EMG_label.place(relx=0.1, rely=0.4, anchor='w')
            self.inner_EMG_Number = tk.Label(self.frame2, text="", fg="blue")
            self.inner_EMG_Number.config(font=("Arial", 12))
            self.inner_EMG_Number.place(relx=0.2, rely=0.5, anchor='w')
            self.gesture_label = tk.Label(self.frame2, text=f"Gesture is :")
            self.gesture_label.config(font=("Arial", 12))
            self.gesture_label.place(relx=0.1, rely=0.6, anchor='w')
            self.gesture_predict = tk.Label(self.frame2, text="")
            self.gesture_predict.config(font=("Arial", 12))
            self.gesture_predict.place(relx=0.2, rely=0.7, anchor='w')
            self.a, self.b = self.load_Function()
            self.emg_thread = threading.Thread(target=self.EMG_Display)
            self.emg_thread.start()


            #self.EMG_Display()
        if 'COM6' in self.ports:
            self.column_limit = 9
            self.last_averageRoll = 0
            self.last_averageyaw = 0
            self.last_averagePitch = 0
            self.averageroll = 0
            self.averageyaw = 0
            self.averagepitch = 0
            self.last_print_time = time()
            self.last_EMG_Command=None
            self.arduino = serial.Serial('COM6', 115200)
            self.roll_label = tk.Label(self.frame1, text="roll is : ")
            self.roll_label.config(font=("Arial", 12))
            self.roll_label.place(relx=0.2, rely=0.3, anchor='w')
            self.pitch_label = tk.Label(self.frame1, text="pitch is : ")
            self.pitch_label.config(font=("Arial", 12))
            self.pitch_label.place(relx=0.2, rely=0.4, anchor='w')
            self.yaw_label = tk.Label(self.frame1, text="yaw is : ")
            self.yaw_label.config(font=("Arial", 12))
            self.yaw_label.place(relx=0.2, rely=0.5, anchor='w')
            self.imu_thread = threading.Thread(target=self.IMU_Display)
            self.imu_thread.start()
            #self.IMU_Display()


    def _decode(self, serial_data):
        serial_string = serial_data.decode(errors="ignore")
        adc_string_1 = ""
        adc_string_2 = ""
        self.adc_values = [0, 0]
        if '\n' in serial_string:
            # remove new line character
            serial_string = serial_string.replace("\n", "")
            if serial_string != '':
                # Convert number to binary, placing 0s in empty spots
                serial_string = format(int(serial_string, 10), "024b")

                # Separate the input number from the data
                for i0 in range(0, 12):
                    adc_string_1 += serial_string[i0]
                for i0 in range(12, 24):
                    adc_string_2 += serial_string[i0]

                self.adc_values[0] = int(adc_string_1, base=2)
                self.adc_values[1] = int(adc_string_2, base=2)

                return self.adc_values

    def EMG_Display(self):
            try:
                while (self.arduino_EMG.inWaiting() > 0):
                    data = self.arduino_EMG.readline()
                    emg_data = self._decode(data)
                    if emg_data is not None:
                        print(f"EMG 1: {emg_data[0]} , EMG 2: {emg_data[1]}")
                        self.outer_EMG_Number.config(text=f"{emg_data[0]}")
                        self.inner_EMG_Number.config(text=f"{emg_data[1]}")
                        data = [emg_data[0], emg_data[1]]
                        predictions = self.predict(data, self.a, self.b)
                        ges_predictions = None
                        if predictions is not None:
                            if predictions == -1:
                                ges_predictions = "Hand Open"
                            if predictions == 1:
                                ges_predictions = "Hand Close"
                            if predictions == 0:
                                ges_predictions = "Unknown"
                            self.gesture_predict.config(text=f"{ges_predictions}")
                            self.send_command_to_unity(f"Hand :{ges_predictions}")
                        #current_time_EMG = time()
                        #if ges_predictions=="Hand Open":
                         #if current_time_EMG - self.last_print_time >= 0.01:
                          #if ges_predictions!=self.last_EMG_Command:
                             #self.send_command_to_unity(f"Hand :{ges_predictions}")
                        #self.last_print_time = current_time_EMG
                        #self.last_EMG_Command=ges_predictions





            except Exception as e:
                print(f"An error occurred: {e}")

            # Call update_display() again after 50 milliseconds
            self.EMG_display_id = self.root.after(1, self.EMG_Display)

    def IMU_Display(self):
      while True:
        try:
            while self.arduino.inWaiting() == 0:
                pass

            dataPacket = self.arduino.readline().decode()
            cleandata = dataPacket.replace("\r\n", "")
            row = cleandata.strip().split(',')

            if len(row) == self.column_limit:
                splitPacket = cleandata.split(',')

                emg = float(splitPacket[0])  # emg sensor data
                q0 = float(splitPacket[1])  # qw
                q1 = float(splitPacket[2])  # qx
                q2 = float(splitPacket[3])  # qy
                q3 = float(splitPacket[4])  # qz

                # Callibration Statuses
                aC = float(splitPacket[5])  # Accelerometer
                gC = float(splitPacket[6])  # Gyroscope
                mC = float(splitPacket[7])  # Magnetometer
                sC = float(splitPacket[8])  # Whole System

                # calculate angle
                roll = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))
                pitch = -math.asin(2 * (q0 * q2 - q3 * q1))
                yaw = -math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))

                k = np.array([np.cos(yaw) * np.cos(pitch), np.sin(pitch), np.sin(yaw) * np.cos(pitch)])  # X vector
                y = np.array([0, 1, 0])  # Y vector: pointing down
                s = np.cross(k, y)  # Side vector
                v = np.cross(s, k)  # Up vector
                vrot = v * np.cos(roll) + np.cross(k, v) * np.sin(roll)  # Rotated Up vector


                self.roll_label.config(text="roll is : " + str(roll))
                self.pitch_label.config(text="pitch is : " + str(pitch))
                self.yaw_label.config(text="yaw is : " + str(yaw))

                current_time = time()

                if current_time - self.last_print_time >= 0.01:

                    print(f"roll is: {roll}")
                    print(f"last roll is: {self.last_averageRoll}")
                    differ_roll = self.last_averageRoll - roll
                    print(f"differ roll is: {differ_roll}")
                    CalculatedAngle = differ_roll * 3000 / 1.5
                    print(f"CalculatedAngle is: {CalculatedAngle}")
                    if (differ_roll) > 0:
                        self.send_command_to_unity(f"Command : down {CalculatedAngle}")
                    if (differ_roll) < 0:
                        self.send_command_to_unity(f"Command : up {-CalculatedAngle}")

                    if (yaw < 0):
                        yaw = -yaw

                    print(f"yaw is: {yaw}")
                    print(f"last yaw is: {self.last_averageyaw}")
                    differ_yaw = self.last_averageyaw - yaw
                    print(f"differ yaw is: {differ_yaw}")
                    up = roll * 90 / 2.6
                    yawAngle = differ_yaw * 90 / 2
                    '''
                     if (up > 35):
                        yawAngle = differ_yaw * 90 / 1.5
                    if (35 > up > 0):
                        yawAngle = differ_yaw * 90 / 2.26
                    if (up <= 0):
                        yawAngle = differ_yaw * 90 / 2

                    
                    '''

                   # yawAngle = differ_yaw * 110 / 2.5
                    print(f"yawAngle is: {yawAngle}")
                    if (differ_yaw) < 0:
                        self.send_command_to_unity(f"Command : back {-yawAngle}")
                    if (differ_yaw) > 0:
                        self.send_command_to_unity(f"Command : roll {yawAngle}")



                    self.last_print_time = current_time
                    self.last_averageRoll = roll
                    self.last_averageyaw = yaw
                    self.last_averagePitch = pitch

        except Exception as e:
            print("Error:", str(e))


    def load_Function(self,filename='trained.txt'):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    raise ValueError("File content is insufficient to read the vertical line parameters.")

                a = float(lines[0].strip())
                b = float(lines[1].strip())
                print(f"a is {a}, b is {b}")

                return a,b

        except FileNotFoundError:
            raise FileNotFoundError(f"The file {filename} does not exist.")
        except ValueError as e:
            raise ValueError(f"Error reading the file: {e}")

    def predict(self, point, a, b):
        """判断点是否在垂直线的左侧或右侧"""
        x, y = point
        # 计算点的y值与垂直线的y值比较
        line_y = a * x + b
        if y < line_y:
            return -1  # 点在垂直线的左侧
        elif y > line_y:
            return 1  # 点在垂直线的右侧
        else:
            return 0  # 点在垂直线上（可选）

    def send_command_to_unity(self,command):
        host = '127.0.0.1'  # Unity服务器的IP地址
        port = 65432  # Unity服务器监听的端口

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(command.encode())
            response = s.recv(1024)
            print('Received', repr(response))





if __name__ == "__main__":
    root1 = tk.Tk()
    appWelcome = WelcomeWindow(root1)
    root1.mainloop()
