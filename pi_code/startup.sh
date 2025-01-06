#!/bin/bash
# update mountpoint source to your maschine
sudo mount /dev/sda1 /media/usbstick
# update mountpoint of NAS system 
sudo mount -v -t nfs -o vers=3 xxx.xxx.xxx:/?? /media/nas
sleep 2
cd ~/raspbee_image

git pull
if [[ $(hostname -s) != queen* ]]; then
    echo "hostname is not the queen"
	if ps -ef | grep upload.py | grep -v grep; then
		echo "upload.py is running"
	else
		echo "upload.py is not running: git pull and restart"
		#update via git
		cd h264
		nohup python ./upload.py &> upload_nohup.out &
		cd ..
	fi

	if ps -ef | grep record.py | grep -v grep; then
		echo "record.py is running"
	else
		echo "record.py is not running: git pull and restart"
		#update via git
		cd h264
		nohup python ./record.py &> record_nohup.out &
		cd ..
	fi
	
else
	echo "hostname is the queen"
fi

if ps -ef | grep EmergencyRoom.py | grep -v grep; then
	echo "EmergencyRoom.py is running"
else
	echo "EmergencyRoom.py is not running: git pull and restart"
	#update via git
	cd RaspberryEmergencyRoom
	nohup python ./EmergencyRoom.py &> er_nohup.out &
	cd ..
fi

#if the host is the queen, also start the weatherhat.py
if [[ $(hostname -s) = queen* ]]; then
    echo "hostname is the queen"
    if ps -ef | grep sensors.py | grep -v grep; then
		echo "sensors.py is running"
	else
		echo "sensors.py is not running: git pull and restart"
		#update via git
		cd sensors
		nohup python ./sensors.py &> sensors_nohup.out &
		cd ..
	fi
else
	echo "hostname is not the queen"
fi


#if the host is the an indoor pi drone-I-*, also start the light.py
if [[ $(hostname -s) = drone-I-* ]]; then
    echo "hostname is the an indoor drone"
    if ps -ef | grep light.py | grep -v grep; then
		echo "light.py is running"
	else
		echo "light.py is not running: git pull and restart"
		#update via git
		cd light
		nohup python ./light.py &> light_nohup.out &
		cd ..
	fi
else
	echo "hostname is not the an indoor drone"
fi