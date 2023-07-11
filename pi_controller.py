#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 22:18:47 2023

@author: devbot
"""
import PySimpleGUI as sg
import paramiko
import webbrowser
import subprocess

# Define the GUI layout for SSH connection input
ssh_layout = [
    [sg.Text('Raspberry Pi IP', font='Any 15')],
    [sg.InputText(key='-IP-', font='Any 15')],
    [sg.Text('Raspberry Pi Username', font='Any 15')],
    [sg.InputText(key='-USERNAME-', font='Any 15')],
    [sg.Text('Raspberry Pi Password', font='Any 15')],
    [sg.InputText(key='-PASSWORD-', password_char='*', font='Any 15')],
    [sg.Button('SSH', size=(15, 1), pad=(20, 10), font='Any 15')],
    [sg.Text('', key='-STATUS-', size=(30, 1), justification='center', font='Any 15')]
]

# Create the SSH connection input window
ssh_window = sg.Window('SSH Connection', ssh_layout, size=(500, 300))

# Function to establish an SSH connection
def establish_ssh_connection(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        return ssh
    except Exception as e:
        print(e)
        return None

# Event loop to handle SSH connection input and window updates
while True:
    event, values = ssh_window.read()

    if event == sg.WINDOW_CLOSED:
        # Close the window and exit the program
        break

    if event == 'SSH':
        # Retrieve the SSH connection details from the input values
        ip = values['-IP-']
        if ip == 'beans':
            ip = '192.168.86.97'
            username = 'devbot'
            password = 'CameraToolProject'
        else:
            username = values['-USERNAME-']
            password = values['-PASSWORD-']

        # Attempt to establish an SSH connection
        ssh = establish_ssh_connection(ip, username, password)

        if ssh is not None:
            # SSH connection successful
            ssh_window.close()

            # Create the Raspberry Pi Controller window
            controller_layout = [
                [sg.Text('Raspberry Pi Camera Stream', font='Any 20', justification='center')],
                [sg.Checkbox('High Res', default=True, key='-HIGH_RES-', enable_events=True, font='Any 15'),
                 sg.Checkbox('Wireless', default=True, key='-WIRELESS-', enable_events=True, font='Any 15')],
                [sg.Checkbox('High FPS', key='-HIGH_FPS-', enable_events=True, font='Any 15'),
                 sg.Checkbox('HDMI', key='-HDMI-', enable_events=True, font='Any 15')],
                [sg.Button('Start Camera Stream', size=(20, 1), font='Any 15')],
                [sg.Button('End Camera Stream', size=(20, 1), font='Any 15')],
            ]

            terminal_layout = [
                [sg.Multiline('', key='-TERMINAL_OUTPUT-', size=(80, 20), disabled=True, autoscroll=True, font='Any 12')],
                [sg.InputText(key='-TERMINAL_INPUT-', font='Any 12', enable_events=True)],
                [sg.Button('Send Command', size=(15, 1), font='Any 12')]
            ]

            layout = [
                [sg.TabGroup([
                    [sg.Tab('Raspberry Pi Commands', controller_layout)],
                    [sg.Tab('SSH Terminal', terminal_layout)]
                ])]
            ]

            window = sg.Window('Raspberry Pi Controller', layout, size=(800, 500), finalize=True)

            current_directory = ''
            terminal_log = f'{username}@raspberrypi:~ $ '
            window['-TERMINAL_OUTPUT-'].update(terminal_log.strip())

            camera_mode = 3
            stream_mode = 'wireless'
            streaming = False

            while True:
                event, values = window.read()

                if event == sg.WINDOW_CLOSED:
                    # Close the window and exit the program
                    break

                if event == '-HIGH_RES-' and values['-HIGH_RES-']:
                    # High Res toggle enabled
                    window['-HIGH_FPS-'].update(value=False)
                    camera_mode = 3

                if event == '-HIGH_FPS-' and values['-HIGH_FPS-']:
                    # High FPS toggle enabled
                    window['-HIGH_RES-'].update(value=False)
                    camera_mode = 2

                if event == '-WIRELESS-' and values['-WIRELESS-']:
                    # Wireless toggle enabled
                    window['-HDMI-'].update(value=False)
                    stream_mode = 'wireless'

                if event == '-HDMI-' and values['-HDMI-']:
                    # HDMI toggle enabled
                    window['-WIRELESS-'].update(value=False)
                    stream_mode = 'HDMI'

                if event == 'Start Camera Stream':
                    if not streaming:
                        streaming = True
                        # Start the camera stream on the Raspberry Pi
                        ssh.exec_command(f"python Python_Executables/CameraToolProject/camera_stream.py {camera_mode} {stream_mode}")
                        sg.popup('Camera stream started')

                        if stream_mode == 'wireless':
                            # Start the Nginx service on the external computer
                            subprocess.run(['sudo', 'service', 'nginx', 'start'])
                            print('Starting Nginx service and opening web browser')
                            webbrowser.open('http://localhost:8080')
                            print('http://localhost:8080')

                if event == 'End Camera Stream':
                    if streaming:
                        streaming = False
                        # Find the PID of the camera_stream_hdmi.py process
                        pid_command = "pgrep -f camera_stream.py"
                        _, stdout, _ = ssh.exec_command(pid_command)
                        pid = stdout.read().decode().strip()

                        # Send the termination signal to the camera_stream_hdmi.py process
                        terminate_command = f"kill -SIGTERM {pid}"
                        ssh.exec_command(terminate_command)

                        sg.popup('Camera stream stopped')

                        if stream_mode == 'wireless':
                            # Stop the Nginx service on the external computer
                            subprocess.run(['sudo', 'service', 'nginx', 'stop'])
                            print('Stopping Nginx service')

                if event == 'Send Command':
                    # Send the command to the Raspberry Pi terminal and display the output
                    command = values['-TERMINAL_INPUT-'].strip()
                    window['-TERMINAL_INPUT-'].update('')  # Clear the terminal input text box
                    terminal_log += f'{command}\n'

                    if command == 'exit':
                        # Close the GUI and stop the script
                        break
                    elif command.startswith('cd'):
                        # Check if it's a cd command
                        if len(command.split()) > 1:
                               cd_command = command.split()[-1]
                        else:
                               cd_command = ''
                        if cd_command == '' or cd_command == '~':
                            # Home directory
                            current_directory = ''
                        elif cd_command == '..':
                            # Move up one directory
                            if len(current_directory.split('/')) == 1:
                                current_directory = ''
                            else:
                                current_directory = '/'.join(current_directory.split('/')[:-1])
                        else:
                            # Split the command into base command and modifier
                            if current_directory == '':
                                current_directory = f'/{cd_command}'
                            else:
                                current_directory = f'{current_directory}/{cd_command}'
                        command_with_directory = command.split()[0] + ' ' + current_directory[1:]
                    elif current_directory == '':
                        command_with_directory = command
                    else:
                        if command == 'ls':
                            # Prepend the current directory to the command
                            command_with_directory = f'{command} {current_directory[1:]}'
                        else:
                            command_with_directory = ' '.join(command.split()[:-1]) + ' ' + current_directory[1:] + '/' + command.split()[-1]

                    stdin, stdout, stderr = ssh.exec_command(command_with_directory)
                    output = stdout.read().decode('utf-8')
                    # Updated header
                    header = f'{username}@raspberrypi:~{current_directory} $ '
                    if command == 'ls':
                        terminal_log += output.strip() + '\n' + header
                    else:
                        terminal_log += output.strip() + header
                    window['-TERMINAL_OUTPUT-'].update(terminal_log.strip())

            # Close the Raspberry Pi Controller window
            window.close()
        else:
            # SSH connection failed
            ssh_window['-STATUS-'].update('Failed to establish SSH connection.')

# Close the SSH connection input window
ssh_window.close()
