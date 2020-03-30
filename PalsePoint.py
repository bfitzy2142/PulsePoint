#!/usr/bin/env python3
"""
    In order to get the HR value, I made use of another project on
    GitHub which can be found here at
    this URL: https://github.com/jlennox/HeartRate

    Specaial Thanks to jlennox with his amazing program written
    in C++ allowing me to quickly make
    this project to fruition. Check out his project if you would like to
    learn bluetooth interaction in C++.

    Interactions with the Wifi switch also make use of another exisiting
    project called smartplug written by: Stefan Wendler

    Please note that this project assumes the use of a EDIMAX Smart Plug
    Switch of model type SP1101W or SP2101W. If you would like to use your
    own, you will need to determine if API is open to write code for, or if
    there is implementation already available as I had made use of
    for this project. The code for the edimax type is from this
    github repo: https://github.com/wendlers/ediplug-py

    Author: Bradley Fitzgerald
    Date: March 26 2020
"""

import csv
import xml.etree.ElementTree as ET
from time import sleep
from lean_smartplug import SmartPlug
import os
import threading


def write_config():
    """
        Write_config modifies the setting.xml file used by the HR program.
        By default the HR program is set up without logging functionality,
        so this function enables it along with disabling some annoying alerts.
    """
    homepath = os.environ["HOMEPATH"]
    # Set log location
    settings_path = f'{homepath}/AppData/Roaming/HeartRate/settings.xml'

    tree = ET.parse(settings_path)
    root = tree.getroot()

    for child in root:
        if (child.tag == 'AlertLevel'):
            child.text = '0'
        elif (child.tag == 'WarnLevel'):
            child.text = '0'
        elif (child.tag == 'LogFile'):
            child.text = get_log_file()

    tree.write(settings_path)


def get_log_file():
    """
    get_log_file finds the location of the log file of which HR data is logged

    returns:
        str - heartrate.csv file location
    """
    return f"{os.getcwd()}\log\heartrate.csv"


def get_hr():
    """
    Get heartrate parses a CSV file which is updated constantly by the
    heartrate program created by GitHub user Jlenix. 

    returns:
        hr {int} - latest HR entry in the heartrate.csv
    """
    with open(get_log_file()) as hrcsv:
        read_csv = csv.reader(hrcsv, delimiter=',')
        csv_list = list(read_csv)

        if (csv_list == []):
            # Recurive call in case the file was just emptied.
            return get_hr()
        else:
            top_row = csv_list[len(csv_list)-1]
            hr = int(top_row[1])
    return hr


def run_hr_fetcher():
    """
    Runs the C++ HR program
    """
    directory = os.getcwd()
    os.system(f'{directory}/HRM_Logger/HeartRate.exe')


def print_banner():
    """
    Prints list of - as a banner
    """
    print('-----------------------')


def run(switchpoint, ip, user_pass):
    """
    run is the primary method used which continuely scrapes HR data from the
    latest entries in the heartrate.csv file. This function contains the logic
    to determine if the Wi-Fi switch should be on or off. Note that this is the
    function to modify if you wish to integrate this project with a different
    type of Wi-Fi smart plug.

    Attributes:
        switchpoint {int} - the tipping hr value of which determines if the
                            switch should be on or off
        ip {str} - the IP address of the smart switch
        user_pass {tupple} - (username, password) for the wifi switch.
    """
    p = SmartPlug(ip, user_pass)
    time_running = 0

    while(True):
        hr = get_hr()

        # HR Program Hasn't logged any data yet
        if (hr == 0 or hr is None):
            print("Can't get HR Data")

        else:
            # Process HRM data and make decision
            if (hr >= switchpoint and p.state == "OFF"):
                p.state = "ON"
                print_banner()
                print('Turning on FAN!')
                print_banner()
            elif (hr < switchpoint and p.state == "ON"):
                p.state = "OFF"
                print_banner()

                print('Turning off FAN!')
                print_banner()

            time_running += 1

            # Display stats at 5 sec intervals
            if (time_running % 5 == 0):
                print_banner()
                print(f'Seconds running: {time_running}')
                print(f'Heart Rate:{hr} bpm')
                print_banner()

            # Clear the log file to prevent it from gowing too large
            if (time_running == 300):
                with open(get_log_file(), 'w'):
                    pass
                time_running = 0
                sleep(4)

        sleep(1)


def main():
    """
    Main function to control flow of program

    Modify the following to run the program:
        ip
        user
        passw
        switchpoint (optional)
    """

    # Wi-Fi switch creditentals
    ip = '192.168.0.21'
    user = 'admin'
    passw = '1234'

    # Heart Rate Tipping Point (where switch turns on)
    switchpoint = 100

    # If first run, need to run program and close to create settings file
    homepath = os.environ["HOMEPATH"]
    settings_path = f'{homepath}/AppData/Roaming/HeartRate/settings.xml'

    if (os.path.isfile(settings_path) == False):
        first_run = threading.Thread(target=run_hr_fetcher, daemon=True)
        first_run.start()
        sleep(5)
        first_run._running = False

    # Run C++ pogram as a daemon thread
    heart_rate = threading.Thread(target=run_hr_fetcher, daemon=True)
    heart_rate.start()

    print('Welcome to PalsePoint!')
    print('Make sure your HRM is connected to bluetooth!')

    # Allowing HeartRate program time to start
    sleep(5)

    # Edit HR config file so HR logging starts
    write_config()

    # Parse HR and determine switch status, runs until user quits the program
    run(switchpoint, ip, (user, passw))


if __name__ == "__main__":
    main()
