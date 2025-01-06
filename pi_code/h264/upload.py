# -*- coding: utf-8 -*-
# Attention: Please use pysmb 1.1.14

import os
from os.path import isfile, join
import time 
from socket import gethostname
from decider import Decider
import shutil
from datetime import datetime
from config import Configuration
import traceback
import sys
from mylog import MyLog


log = MyLog("upload.log")

def getFoldername(filename):
  parts = filename.split("__")[1]
  par = parts.split("_")[0]
  dateparts = par.split("-")
  return dateparts[2]+"-"+dateparts[1]+"-"+dateparts[0]
  

def doWork(config):
  if config.decider_send_to_NAS:
    
    rawdir=config.rawImageQutputDirectory 
    videodir =config.videoOutputDirectory
    videolist =os.listdir(videodir)
    if len(videolist) > 0:
      datestring = getFoldername(videolist[0])
      my_name = gethostname()
      nas_raw_folder = join(config.server_raw_folder, my_name, datestring)
      log.info("start to copy to folder: "+nas_raw_folder)
      #mkdir, exists ok
      if not os.path.exists(nas_raw_folder):
        os.makedirs(nas_raw_folder)
      #for f in files of rawdir
      for foldername in os.listdir(rawdir):
        full_subfoldername=os.path.join(rawdir, foldername)
        full_nas_subfoldername = os.path.join(nas_raw_folder, foldername)
        if not os.path.exists(full_nas_subfoldername):
          os.makedirs(full_nas_subfoldername)
        for file_name in os.listdir(full_subfoldername):
        # construct full file path
          source = os.path.join(full_subfoldername, file_name)
          destination = os.path.join(full_nas_subfoldername, file_name)
      # copy only files
          if os.path.isfile(source) and not os.path.isfile(destination):
             shutil.copy(source, destination)
        # copy file if not exists
      log.info("Copied all raw files from raw to nas")
      nas_video_folder = join(config.server_video_folder, my_name, datestring)
      log.info("start to copy to folder: "+nas_video_folder)
      if not os.path.exists(nas_video_folder):
        os.makedirs(nas_video_folder)
      #for f in files of rawdir
      for file_name in os.listdir(videodir):
        # construct full file path
        source = os.path.join(videodir, file_name)
        destination = os.path.join(nas_video_folder, file_name)
        # copy only files if they do not already exist
        if os.path.isfile(source) and not os.path.isfile(destination):
          shutil.copy(source, destination)
      log.info("Copied all video files from video to nas")
    else:
      log.info("No files to copy")
    #wait one hour to be sure
    time.sleep(3600)
    #prepare folder on usb stick
    #remove complete raw dir and create a new empty folder raw
    shutil.rmtree(config.rawImageQutputDirectory)
    log.info("removed all raw files on usbstick")
    os.makedirs(config.rawImageQutputDirectory, exist_ok = True)
    log.info("recreated raw folder on usbstick")
    #remove complete raw dir and create a new empty folder raw
    shutil.rmtree(config.videoOutputDirectory)
    log.info("removed all video files on usbstick")
    os.makedirs(config.videoOutputDirectory, exist_ok = True)
    log.info("recreated video folder on usbstick")
  
if __name__ == '__main__':
  try:
    config = Configuration("config.yaml")
    log.info("Config loaded")
    decider = Decider(config)
    log.info(decider)
    while True:
      if decider.dayOrNight() == Decider.NIGHT:
        log.info("Night ... starting work...............")
        doWork(config)
        log.info("work done")
      log.info("got sleep for "+str(decider.timeTo("dusk")))
      time.sleep(decider.timeTo("dusk"))
  except Exception as e:
    log.error(traceback.format_exc())
    sys.exit()
    
    







