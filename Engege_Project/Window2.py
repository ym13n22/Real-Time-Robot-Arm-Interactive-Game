import threading
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import serial
import serial.tools.list_ports
from time import sleep
import math
import time
import socket
import os
from PIL import Image, ImageTk
from time import sleep, time

#this is the file for the combined hardware detector

class Window:
    def __init__(self, root):
        self.input_port='COM9'
        self.root = root
        self.root.title("Integration")
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.arduino = None

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

        #self.imu_thread = threading.Thread(target=self.initial_IMU)
        #self.emg_thread = threading.Thread(target=self._initialise_EMG_graph)
        #self.emg_thread.start()
        #self.imu_thread.start()




        self.emg_data_1 = [-1.0] * 41
        self.emg_data_2 = [-1.0] * 41

        self.initial_IMU()
        self._initialise_EMG_graph()
        self.display_IMU_thread=threading.Thread(target=self.update_display)
        self.display_EMG_thread=threading.Thread(target=self.EMG_Display)

    # initial button, commands and 3D metrics for IMU detector
    def initial_IMU(self):
        # Serial Port Setup
        if self.input_port in self.ports:#port maybe different on different laptop

            self.label2 = tk.Label(self.frame2, text=f"Port: {self.input_port} ")
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

    # initial button, commands and metrics for EMG detector
    def _initialise_EMG_graph(self):
        if self.input_port in self.ports:#port maybe different on different laptop

            self.label2 = tk.Label(self.frame3, text=f"Port: {self.input_port} ")
            self.label2.place(relx=0.23, rely=0.8, anchor='center')
            self.label1 = tk.Label(self.frame3,
                                   text="click the Connect button to see the animation",
                                   wraplength=self.width / 2)
            self.label1.place(relx=0.5, rely=0.9, anchor='center')
            # Add a button to start data transmission
            #self.start_button = tk.Button(self.frame3, text="connect", command=self.start_EMG_data_transmission)
            #self.start_button.place(relx=0.45, rely=0.8, anchor='center')

            #self.start_button = tk.Button(self.frame3, text="Disconnect", command=self.disconnect)
            #self.start_button.place(relx=0.7, rely=0.8, anchor='center')

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




    #button effect when connect
    def start_data_transmission(self):
        # Set the transmitting flag to True and start the update loop
        if self.input_port in self.ports:
            if self.arduino==None:
             self.arduino = serial.Serial(self.input_port, 9600)
        self.transmitting = True
        self.update_display()

   #button effect when connect for EMG
    def start_EMG_data_transmission(self):
        # Set the transmitting flag to True and start the update loop
        if self.input_port in self.ports:
            if self.arduino==None:
             self.arduino = serial.Serial(self.input_port, 9600)
        self.EMG_transmitting = True
        self.EMG_Display()

    #Go to the interface for metrics
    def game_Start(self):
        self.root.destroy()  # Close the welcome window
        new_root = tk.Tk()
        app = gameScreen(new_root)
        new_root.mainloop()


     #effect for disconnect button
    def disconnect(self):
        self.transmitting = False
        self.EMG_transmitting=False
        self.root.after_cancel(self.update_display_id)
        if self.arduino is not None:
            self.arduino.close()
            self.arduino = None



    #when the IMU connected show the real-time 3D metrics
    def update_display(self):
        if self.transmitting:
            try:
                while ((self.arduino.inWaiting() > 0)and
                       (self.transmitting==True)):
                    dataPacket = self.arduino.readline()
                    dataPacket = dataPacket.decode()
                    cleandata = dataPacket.replace("\r\n", "")
                    row = cleandata.strip().split(',')


                    if len(row) == 10:
                        splitPacket = cleandata.split(',')
                        q0 = float(splitPacket[2])  # qw
                        q1 = float(splitPacket[3])  # qx
                        q2 = float(splitPacket[4])  # qy
                        q3 = float(splitPacket[5])  # qz
                        emg1 = float(splitPacket[0])  # First EMG sensor data
                        emg2 = float(splitPacket[1])  # Second EMG sensor data
                        #print(f"emg1: {emg1}, emg2: {emg2}")
                        data = [emg1, emg2]
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


                        self.outer_EMG_Number.config(text=f"{emg1}")
                        self.inner_EMG_Number.config(text=f"{emg2}")
                        self.emg_data_1.append(emg1)
                        self.emg_data_1.pop(0)
                        self.emg_data_2.append(emg2)
                        self.emg_data_2.pop(0)

                            # Update the line data to shift the line from right to left
                        self.line1.set_data(range(len(self.emg_data_1)), self.emg_data_1)
                        self.line2.set_data(range(len(self.emg_data_2)), self.emg_data_2)

                            # Redraw the canvas
                        self.canvas1.draw()  # Redraw the canvas

                        # Calculate Angles
                        roll = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))
                        pitch = -math.asin(2 * (q0 * q2 - q3 * q1))
                        yaw = -math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))


                        self.roll_label.config( text="roll is : "+str(roll))
                        self.pitch_label.config(text="pitch is : "+str(pitch))
                        self.yaw_label.config(text="yaw is : "+str(yaw))
                        #print(roll, pitch, yaw)


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


                        #self.averageemg += emg


                        # Update EMG Label
                        #self.emg_label.config(text=f"Average EMG: {self.averageemg:.2f}")

            except Exception as e:
                print(f"An error occurred: {e}")

            # Call update_display() again after 50 milliseconds
            self.update_display_id =self.root.after(1, self.update_display)

    #when the EMG connected for the line metrics for EMG data
    def EMG_Display(self):
        data_collection_duration = 3
        if self.EMG_transmitting:
            try:
                while self.arduino.inWaiting() > 0:
                    dataPacket = self.arduino.readline()
                    dataPacket = dataPacket.decode()
                    cleandata = dataPacket.replace("\r\n", "")
                    row = cleandata.strip().split(',')

                    if len(row) == 10:
                        splitPacket = cleandata.split(',')



            except Exception as e:
                print(f"An error occurred: {e}")

            # Call update_display() again after 50 milliseconds
            self.EMG_display_id = self.root.after(1, self.EMG_Display)


    #decode the EMG data from detectors
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

    #load trained function for predict
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

    #predict the gestures
    def predict(self, point,a,b):
        """predict whether the point is located in the left or right"""
        x, y = point
        line_y = a * x + b
        if y < line_y:
            return -1  # left
        elif y > line_y:
            return 1  # right
        else:
            return 0  # on

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
            #print("Image loaded successfully")
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
        self.input_port='COM9'
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
        if self.input_port in self.ports:

            self.emg_data_1 = [-1.0] * 41
            self.emg_data_2 = [-1.0] * 41
            self.savingData=[]
            self.openHandButton=tk.Button(self.frame2,text="Hand Open",command=self.EMG_connect_HandOpen,width=15, height=2,font=("Helvetica", 12))
            self.openHandButton.place(relx=0.3, rely=0.3, anchor='center')
            self.handCloseButton=tk.Button(self.frame2,text="Hand Close",command=self.handCloseButton,width=15, height=2,font=("Helvetica", 12))
            self.handCloseButton.place(relx=0.7, rely=0.3, anchor='center')
            self.gameStartButton = tk.Button(self.frame2, text="Start", command=self.startButton, width=15,
                                         height=2,font=("Helvetica", 12))
            self.gameStartButton.place(relx=0.5, rely=0.5, anchor='center')
        if self.input_port not in self.ports:
            self.label=tk.Label(self.frame2, text="No EMG device found, Please check the hardware connection",font=("Helvetica", 15))
            self.label.place(relx=0.5, rely=0.3, anchor='center')
            self.gameStartButton = tk.Button(self.frame2, text="Start", command=self.startButton, width=15,
                                             height=2, font=("Helvetica", 12))
            self.gameStartButton.place(relx=0.5, rely=0.5, anchor='center')

    #Button effect for start game button
    def startButton(self):
        self.root.destroy()  # Close the welcome window
        new_root = tk.Tk()
        app = Window(new_root)
        new_root.mainloop()

    # Button effect for start recording when the gesture is handOpen
    def EMG_connect_HandOpen(self):
        self.arduino_EMG = serial.Serial(self.input_port, 9600, timeout=1)
        gesture = "handOpen"
        self.start_countdown(11)
        self.displayAndsaveDate()

    # Button effect for start recording when the gesture is handClose
    def handCloseButton(self):
        self.arduino_EMG = serial.Serial(self.input_port, 9600, timeout=1)
        gesture = "handOpen"
        self.start_countdown_close(11)
        self.displayAndsaveDate()

    # Button effect for disconnect
    def EMG_disconnect(self):
        if self.arduino_EMG is not None:
            self.arduino_EMG.close()
            self.arduino_EMG = None

    #show the countdown numbers when record hand open
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

    #show the countdown numbers hwne record hand close
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


    #save data
    def displayAndsaveDate(self):
      if self.startSave:
        try:
            while ((self.arduino_EMG.inWaiting() > 0) ):
                dataPacket = self.arduino_EMG.readline()
                dataPacket = dataPacket.decode()
                cleandata = dataPacket.replace("\r\n", "")
                row = cleandata.strip().split(',')

                if len(row) == 10:
                    splitPacket = cleandata.split(',')
                    emg1 = float(splitPacket[0])  # First EMG sensor data
                    emg2 = float(splitPacket[1])  # Second EMG sensor data
                    print(f"emg1: {emg1}, emg2: {emg2}")


                    self.emg_data_1.append(emg1)
                    self.emg_data_1.pop(0)
                    self.emg_data_2.append(emg2)
                    self.emg_data_2.pop(0)
                    if self.startSave==True:
                     self.savingData.append([emg1,emg2])
                     print(len(self.savingData))


                    # Update the line data to shift the line from right to left
                    self.line1.set_data(range(len(self.emg_data_1)), self.emg_data_1)
                    self.line2.set_data(range(len(self.emg_data_2)), self.emg_data_2)

                    # Redraw the canvas
                    self.canvas1.draw()  # Redraw the canvas

        except Exception as e:
            print(f"An error occurred: {e}")

        self.EMG_display_id = self.root.after(1, self.displayAndsaveDate)



    #draw the buttons, metrics for initial training interface
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

    #turn the saved data to the algorithm and save to the file trained.txt
    def trainData(self):
        if os.path.exists('trained.txt'):
            os.remove('trained.txt')

        if (self.savedDataClose != []) and (self.savedDataOpen != []):
            vertical_line = Algorithm(self.savedDataClose, self.savedDataOpen)
            print(f"Function is: y = {vertical_line.a}x + {vertical_line.b}")

            with open('trained.txt', 'w') as file:
                file.write(f"{vertical_line.a}\n")
                file.write(f"{vertical_line.b}\n")

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
        """calculate the average of these points"""
        n = len(lst)
        if n == 0:
            return (0, 0)
        sum_x = sum(point[0] for point in lst)
        sum_y = sum(point[1] for point in lst)
        return (sum_x / n, sum_y / n)

    def calculate_line_equation(self, list1, list2):
        """calculate the line equation in the form of y = ax + b"""
        avg1 = self.calculate_average(list1)
        avg2 = self.calculate_average(list2)

        x1, y1 = avg1
        x2, y2 = avg2

        # Calculating the slope
        if x1 == x2:
            raise ValueError("The slope of a vertical line is undefined because two points are on the same vertical line.")

        slope = (y2 - y1) / (x2 - x1)

        perpendicular_slope = -1 / slope

        # Use the point-slope form to convert the equation y - y1 = m(x - x1) to the form y = ax + b
        a = perpendicular_slope
        b = y1 - a * x1

        return a, b

    def predict(self, point):
        x, y = point
        line_y = self.a * x + self.b
        if y < line_y:
            return -1  # left
        elif y > line_y:
            return 1  # right
        else:
            return 0  # on

class gameScreen:
    def __init__(self, root):
        self.input_port='COM9'
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

        if self.input_port in self.ports :
            #self.arduino_EMG = serial.Serial(self.input_port, 9600, timeout=1)
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
            #self.emg_thread = threading.Thread(target=self.EMG_Display)
           # self.emg_thread.start()


            #self.EMG_Display()
        if self.input_port in self.ports:
            self.column_limit = 9
            self.last_averageRoll = 0
            self.last_averageyaw = 0
            self.last_averagePitch = 0

            self.averageroll = 0
            self.averageyaw = 0
            self.averagepitch = 0
            self.last_print_time = time()
            self.arduino = serial.Serial(self.input_port, 115200)
            self.roll_label = tk.Label(self.frame1, text="roll is : ")
            self.roll_label.config(font=("Arial", 12))
            self.roll_label.place(relx=0.2, rely=0.3, anchor='w')
            self.pitch_label = tk.Label(self.frame1, text="pitch is : ")
            self.pitch_label.config(font=("Arial", 12))
            self.pitch_label.place(relx=0.2, rely=0.4, anchor='w')
            self.yaw_label = tk.Label(self.frame1, text="yaw is : ")
            self.yaw_label.config(font=("Arial", 12))
            self.yaw_label.place(relx=0.2, rely=0.5, anchor='w')
            self.IMU_Display()
            #self.imu_thread = threading.Thread(target=self.IMU_Display)
            #self.imu_thread.start()
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

    #display the real-time IMU data and sent to Unity by Socket
    def IMU_Display(self):
            try:
                while (self.arduino.inWaiting() > 0):
                    dataPacket = self.arduino.readline()
                    dataPacket = dataPacket.decode()
                    cleandata = dataPacket.replace("\r\n", "")
                    row = cleandata.strip().split(',')


                    if len(row) == 10:
                        splitPacket = cleandata.split(',')
                        q0 = float(splitPacket[2])  # qw
                        q1 = float(splitPacket[3])  # qx
                        q2 = float(splitPacket[4])  # qy
                        q3 = float(splitPacket[5])  # qz
                        emg1 = float(splitPacket[0])  # First EMG sensor data
                        emg2 = float(splitPacket[1])  # Second EMG sensor data
                        #print(f"emg1: {emg1}, emg2: {emg2}")
                        data = [emg1, emg2]
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
                        self.outer_EMG_Number.config(text=f"{emg1}")
                        self.inner_EMG_Number.config(text=f"{emg2}")
                        self.send_command_to_unity(f"Hand :{ges_predictions}")


                        # Calculate Angles
                        roll = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))
                        pitch = -math.asin(2 * (q0 * q2 - q3 * q1))
                        yaw = -math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))


                        self.roll_label.config( text="roll is : "+str(roll))
                        self.pitch_label.config(text="pitch is : "+str(pitch))
                        self.yaw_label.config(text="yaw is : "+str(yaw))
                        print(roll, pitch, yaw)
                        current_time = time()
                        if current_time - self.last_print_time >= 0.01:
                            print(f"roll is: {roll}")
                            print(f"last roll is: {self.last_averageRoll}")
                            differ_roll = self.last_averageRoll - roll
                            print(f"differ roll is: {differ_roll}")
                            CalculatedAngle = differ_roll * 3000 / 2.5
                            print(f"CalculatedAngle is: {CalculatedAngle}")
                            if (differ_roll) > 0:
                                print("send_command_to_unity"+(f"Command : down {CalculatedAngle}"))
                                self.send_command_to_unity(f"Command : down {CalculatedAngle}")
                            if (differ_roll) < 0:
                                print("send_command_to_unity" + (f"Command : down {CalculatedAngle}"))
                                self.send_command_to_unity(f"Command : up {-CalculatedAngle}")

                            if (yaw < 0):
                                yaw = -yaw

                            print(f"yaw is: {yaw}")
                            print(f"last yaw is: {self.last_averageyaw}")
                            differ_yaw = self.last_averageyaw - yaw
                            print(f"differ yaw is: {differ_yaw}")
                            yawAngle = differ_yaw * 90 / 2
                            print(f"yawAngle is: {yawAngle}")
                            if (differ_yaw) < 0:
                                print("send_command_to_unity"+(f"Command : back {-yawAngle}"))
                                self.send_command_to_unity(f"Command : back {-yawAngle}")
                            if (differ_yaw) > 0:
                                print("send_command_to_unity" + (f"Command : roll {-yawAngle}"))
                                self.send_command_to_unity(f"Command : roll {yawAngle}")

                            self.last_print_time = current_time
                            self.last_averageRoll = roll
                            self.last_averageyaw = yaw
                            self.last_averagePitch = pitch



            except Exception as e:
                print(f"An error occurred: {e}")

            # Call update_display() again after 50 milliseconds
            self.update_display_id =self.root.after(1, self.IMU_Display)

   #load the function for predict
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
        x, y = point
        line_y = a * x + b
        if y < line_y:
            return -1  # left
        elif y > line_y:
            return 1  # right
        else:
            return 0  # on

    #build the connect to unity with Socket and send the response command
    def send_command_to_unity(self,command):
        host = '127.0.0.1'  #  IP address for the Unity server
        port = 65432  # The port that the Unity server listens on

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(command.encode())
            response = s.recv(1024)
            print('Received', repr(response))





if __name__ == "__main__":
    root1 = tk.Tk()
    appWelcome = WelcomeWindow(root1)
    root1.mainloop()
