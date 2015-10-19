C275 Assignment 1 Part 2

by:
Hammad Jutt, Section EB1
Shivansh Singla, Section EB1

1. DESCRIPTION:

This Assignment consists of two programs: client.cpp which is to be run on the arduino board, and server.py which is to be run on the computer the arduino board is connected to.

The client (arduino) will be able to select two points on a map of edmonton using a joystick. It will then send the latitude and longitude coordinates of these points over the serial port to the python server (server.py). The server will receive the coordinates of these two points by reading off the serial port and will calculate the shortest path between them based on data of Edmonton roads. It will then send the information for this shortest path back over the serial port to the arduino, waiting for aknowledgement of data receipt for each waypoint in the path. The arduino will then take this shortest path data and draw it onto the map.


2. HOW TO USE:

To use this program, build and upload the client.cpp program to the arduino using make upload. Ensure the arduino is wired correctly as per the specifications on eClass.

To run the server program, run server.py on the computer the arduino is connected to. Ensure that the client.cpp program is already running on the arduino.

When both programs are running (client.cpp on arduino and server.py on the computer), you can then move the joystick and click it to select a start point. Move it again and click again to select an endpoint. Then, the arduino will communicate with the server and draw the shortest path onto the LCD Map.


****NOTE****
If an error is displayed when running server.py, simply re-run server.py 
If error persists, restart interpreter and run server.py twice


3. CREDIT

All functions in graph_v2.py were taken from eClass. All code in path_functions.py was written by us. Every other file was taken from eClass and modified as per the assignment requirements. The serial_readline function was modified to work with timeouts.


