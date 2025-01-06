# Long-term monitoring of insect aggregations using a multi-camera system

In this repository, the code for the paper called
"Long-term monitoring of insect aggregations using a multi-camera system"

The paper is currently in review, link will be made available when published.


## The repository is structured as follows:
* pi_code contains the source code for the OUs executing the camera recordings
* image_stitching contains the source code to stitch images of an camera grid into one overview image


## The Oberservation Unit
To make a Observation Unit running with the source code, checkout the code on a Rapian Bullseye environment.
Follow the instructions in the install.sh file.
If a weatherstation should be operated, make sure the name of the OU with the weather station starts with "Queen". All other drones must not start with this name (use "Drone" instead).

If a light should be controlled by a pi (e.g. in indoor laboratory), the name of the drone must start with "Drone-I" (see startup.sh for details).

## The stitching process
The stitching process contains of a preprocessing step to determine the homographies of the camera images and a stitching process.
To determine the homographies first available image pairs must be determined (executing 01_findAvailablePairs.py).
Afterwards, homographies, matches and keypoints between the image pairs are extracted (executing 02_findHomographies.py), which are then combined into one dataset for each camera pair (03_calculateH.py).
Afterwards, the data is restructured for the ceres solver (see ceres_solver) by using script 04_bundleAdjustment.py. 
When these scripts were executed, overview images of the same year can be created. If the system setup changes, steps 1 to 4 needs to be redone.

To generate a concrete overview image, a timestamp must be given. With the help of an index database, the location of the images, closest matching the requested timestamp are read and the images are loaded and converted from the Network Attached Storage. 
Afterwards, the perspective tranformations are executed on the images. Moving the images to their respective place in the overview image is the next step. At the end, all images are blended into one single image using a feather blender (05_stitch.py).
