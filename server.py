"""
Hammad Jutt, Section EB1
Shivansh Singla, Seciton EB1

NOTE: 
If an error is displayed that says a function is not defined, simply re-run server.py
If error persists, restart interpreter and run server.py twice
"""

import sys
from pathfunctions import *
import argparse
# the following line actually imports serial (use this instead of import serial)
import textserial
import time

def parse_args():
	"""
	Parses arguments for this program.
	
	Returns:
	An object with the following attributes:
	 serialport (str): what is after -s or --serial on the command line
	"""
	# try to automatically find the port
	port = textserial.get_port()
	if port==None:
		port = "0"

	parser = argparse.ArgumentParser(
		  description='Serial port communication testing program.'
		, epilog = 'If the port is 0, stdin/stdout are used.\n'
		)
	parser.add_argument('-s', '--serial',
						help='path to serial port '
							 '(default value: "%s")' % port,
						dest='serialport',
						default=port)

	return parser.parse_args()

def data_transfer(serial_in, serial_out):

	while True:

		timeout = False

		filename = "roads.csv"  #name of file with road data
		road_graph = read_directed_city_graph(filename) #read data from csv into a road_graph 
		read_position(filename)							#read coordinate data into global position

		serialcoor = " "

		#keep reading from serial until a valid request is received
		while serialcoor[0]!= 'R' or len(serialcoor) != 5:
			serialcoor = serial_in.readline()
			serialcoor = serialcoor.strip('\r\n').split(' ')

		#map given coordinates to closest vertices in road_graph
		start = closest_vertex(road_graph, int(serialcoor[1]), int(serialcoor[2]))
		dest = closest_vertex(road_graph, int(serialcoor[3]), int(serialcoor[4]))

		#calculate least cost path from start and dest vertices
		path = least_cost_path(road_graph, start , dest, cost_distance)
		
		#print number of waypoints in path to serial
		print('N', len(path), '\r\n', file=serial_out)

		#print every waypoint in path after receiving response 'A\n' from client
		#if no aknowledgement received in 1 second, timeout and break the loop
		for ver in path:
			#initialize timer to measure timeout
			t1 = time.time()

			response = serial_in.readline().rstrip('\r\n')
			while response != 'A':
				t2 = time.time() - t1
				if t2 > 1:
					timeout = True
					break
				response = serial_in.readline().rstrip('\r\n')


			if timeout:
				break

			#print waypoint data to serial
			print('W', position[ver][0], position[ver][1], '\r\n', file=serial_out)


		#reset state of esrver to waiting for data if data transfer times out
		if timeout:
			print("Timeout: Aknowledgement not received.")
			timeout = False
			continue

		#reinitialize timer to measure timeout before sending end signal
		t1 = time.time()

		#send end signal to client after all waypoints have been sent
		#if final aknowledgement received within one second
		response = serial_in.readline().rstrip('\r\n')
		while response != 'A':
			t2 = time.time() - t1
			if t2 > 1:
				timeout = True
				break
			response = serial_in.readline().rstrip('\r\n')

		#reset server state if timeout
		if timeout:
			print("Timeout: Aknowledgement not received.")
			timeout = False
			continue

		#otherwise, send end signal
		print('E\r\n', file=serial_out)


def main():
	args = parse_args()
			
	if args.serialport!="0":
		print("Opening serial port: %s" % args.serialport)
		baudrate = 9600 # [bit/seconds] 115200 also works
		# we set newline = '\n' to make sure that on any system
		# we send '\n' to the arduino; as a result
		# we will need to deal with the new line ends on our own
		# in the inputs.

		#initialize serial in/out port and run data transfer
		with textserial.TextSerial(args.serialport,baudrate,newline=None) as ser:
			data_transfer(ser,ser)
			
	else:
		#use stdin/stdout if no valid serial port found
		print("No serial port. Using stdin/stdout.")
		data_transfer(sys.stdin,sys.stdout)



if __name__ == "__main__":
	main()


	
