#include "serial_handling.h"

#include <Arduino.h>
#include <errno.h>
#include <assert13.h>
#include <stdio.h> // isdigit


int srv_get_pathlen(LonLat32 start, LonLat32 end) {
    //Sends start and end coordinates to server 
    //and returns the number of waypoints in the path
    //times out after 10 seconds if no response from server

    bool valid_response = false;
    char buffer[50]; //Allocate memory for buffer
    char pathlenstr[10]; 
    int pathlen;
    int timeout; 

    //Send coordinates over serial port
    Serial.println();
    Serial.print("R ");
    Serial.print(String(start.lat) + " ");
    Serial.print(String(start.lon) + " ");
    Serial.print(String(end.lat) + " ");
    Serial.println(String(end.lon));

    //Wait for server to send number of waypoints
    while(!valid_response) {
        if (buffer[0] == 'N') {
            valid_response = true;
        } 
        else {
            memset(buffer, 0, sizeof buffer); //clear the buffer
            timeout = serial_readline(buffer, sizeof buffer, 10000);
            //If no response for server within 10 sec, return 0 for pathlen
            if (timeout == 1) {
                return 0;
            }
        }
    }
    //Ignore the first character and read the number into pathlenstr
    string_read_field(buffer, 2, pathlenstr, 10, "\0");  
    pathlen = string_get_int(pathlenstr); //convert to integer

    return pathlen;
}

int srv_get_waypoints(LonLat32* waypoints, int path_len) {
    //Listens for path data from server and saves the path into waypoints
    //times out after one second if no response from server

    bool valid_response = false;
    char buffer[100];
    char latstring[20];
    char lonstring[20];
    int32_t lat;
    int32_t lon;
    int timeout;

    //Send first aknowledgement to server
    Serial.println('A');

    //Receive data from server for x waypoints. x = path_len
    //Save lat/lon coordinates of each waypoint in waypoints
    for (int i=0; i<path_len; ++i) {

        while(!valid_response) {
            if (buffer[0] == 'W') {
                valid_response = true;   
            } 
            else {
                memset(buffer, 0, sizeof buffer); //clear the buffer
                timeout = serial_readline(buffer, sizeof buffer, 1000);
                if (timeout == 1) {
                    return -1;
                }
            }            
        }

        //ignore first character and read fields starting at second field
        int fieldindex = 2;
        fieldindex = string_read_field(buffer, fieldindex, latstring, 20, " ");
        string_read_field(buffer, fieldindex, lonstring, 20, " ");

        //Convert received field strings into integers
        lat = string_get_int(latstring);
        lon = string_get_int(lonstring);
        //save data to waypoints
        waypoints[i] = LonLat32(lon,lat);

        //reset response state, clear buffer, and send aknowledgement
        valid_response = false;
        memset(buffer, 0, sizeof buffer);
        Serial.println('A');
    }

    //After all data received, check for end acknowledgement 'E'
    while(!valid_response) {
        if (buffer[0] == 'E') {
            //return 1 if data received correctly
            return 1;  
        } 
        else {
            //return -1 if 'E' not received or timeout (1 second)
            memset(buffer, 0, sizeof buffer);
            timeout = serial_readline(buffer, sizeof buffer, 1000);
            if (timeout == 1) {
                return -1;
            }
        }            
    }
}

uint16_t serial_readline(char *line, uint16_t line_size, uint32_t timeout) {
    int bytes_read = 0;    // Number of bytes read from the serial port.
    int32_t t1 = millis(); //initizlize timeout timer
    int32_t t2;

    // Read until we hit the maximum length, or a newline, or timeout
    // One less than the maximum length because we want to add a null terminator.
    while (bytes_read < line_size - 1) {
        while (Serial.available() == 0) {
            t2 = millis() - t1;
            if (t2 > timeout) {
                return 1; //return 1 if time to read line exceeds timeout
            }

        }

        line[bytes_read] = (char) Serial.read();

        // A newline is given by \r or \n, or some combination of both
        // or the read may have failed and returned 0
        if ( line[bytes_read] == '\r' || line[bytes_read] == '\n' ||
             line[bytes_read] == 0 ) {
                // We ran into a newline character!  Overwrite it with \0
                break;    // Break out of this - we are done reading a line.
        } else {
            bytes_read++;
        }
    }

    // Add null termination to the end of our string.
    line[bytes_read] = '\0';
    return 0;
}

uint16_t string_read_field(const char *str, uint16_t str_start
    , char *field, uint16_t field_size, const char *sep) {

    // Want to read from the string until we encounter the separator.

    // Character that we are reading from the string.
    uint16_t str_index = str_start;    

    while (1) {
        if ( str[str_index] == '\0') {
            str_index++;  // signal off end of str
            break;
        }

        if ( field_size <= 1 ) break;

        if (strchr(sep, str[str_index])) {
            // field finished, skip over the separator character.
            str_index++;    
            break;
        }

        // Copy the string character into buffer and move over to next
        *field = str[str_index];    
        field++;
        field_size--;
        // Move on to the next character.
        str_index++;    
    }

    // Make sure to add NULL termination to our new string.
    *field = '\0';

    // Return the index of where the next token begins.
    return str_index;    
}

int32_t string_get_int(const char *str) {
    // Attempt to convert the string to an integer using strtol...
    int32_t val = strtol(str, NULL, 10);

    if (val == 0) {
        // Must check errno for possible error.
        if (errno == ERANGE) {
            Serial.print("string_get_int failed: "); Serial.println(str);
            assert13(0, errno);
        }
    }

    return val;
}
