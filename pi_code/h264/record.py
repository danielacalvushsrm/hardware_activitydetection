import cv2
from camera import PicameraStream
from output import CompressedRawOutput
from maskqueue import MaskQueue
from converter import Converter
from cluster import calculateClusterWithDimension
import time 
from datetime import datetime
from config import Configuration
from decider import Decider
import sys
import os
import numpy as np
import shutil
import traceback
from mylog import MyLog

log = MyLog("record.log")
if __name__ == '__main__':
    try:
        #initialising the instances
        config = Configuration("./config.yaml")
        stream = PicameraStream((config.greyimageResolutionWidth,config.greyimageResolutionHeight),(config.mainResolutionWidth, config.mainResolutionHeight), config.mainStreamColorFormat, config.videoOutputDirectory, config.piname)
        stream.wakeup()
        maskqueue = MaskQueue(config.maskQueueMaxFrames, config.maskQueueActivityThreshold, config.maskQueueMaskColor)
        converter = Converter(config)
        out =  CompressedRawOutput(config.rawImageQutputDirectory, config.piname)

        decider = Decider(config)
        log.info(decider)
        
        #read the prev frame in rgb
        prev = stream.readlores()
        #convert the prev frame to grey
        prev_grey = converter.convertToGrey(prev,stream.getLoresStride(), stream.getLoresHeight(), stream.getLoresWidth())
        #cv2.imwrite("Snapshot_"+str(datetime.now())+".jpg", prev_grey)
        #put the frame into the framequeue to grab it out when needed (to make a diff for the mask)
        maskqueue.setPrevGrey(prev_grey)
        maskqueue.setPrevDiff(np.zeros_like(prev_grey))
        
        #to count the frames in one image -> to know where the activity was
        noOFrames=0
      #  i=0
        while True:
            if decider.dayOrNight() == Decider.DAY:
                #for tracking the time
                start = time.time()
                # Grab the frames from video stream
                current= stream.readlores()

                #convert it to grey image, and gather previous
                current_grey=converter.convertToGrey(current,stream.getLoresStride(), stream.getLoresHeight(), stream.getLoresWidth())
                prev_grey = maskqueue.getPrevGrey()
                
                #make the diff 
                diff = cv2.absdiff(prev_grey, current_grey)
                prev_diff = maskqueue.getPrevDiff()
                #exception for start
                if not prev_diff.any():
                        log.info("exception for start executed")
                        prev_diff = diff
        
                # only check if it is enough difference in the images
             #   if np.amax(diff) > config.diff_threshold:
                        # find the center points of the movement direction
                       # activities = converter.findActivity(diff, prev_diff)
                                        #cluster the activities and filter out almost linear cluster out
                       # correlation, xvalues, yvalues=correlationInCluster(activities, config.cluster_epsilon, config.cluster_min_samples, config.greyimageResolutionWidth, config.greyimageResolutionHeight)
                       # if correlation is not None:
                         #   newDict = { key:value for (key,value) in correlation.items() if value < 0.85 and key != -1}
                            #log.info(newDict)
                            #newDict only includes the relevant cluster and not the noise
                            #filter all not relevant clusters out of x and yvalues
                           # activities = []
                           # for key in newDict.keys():
                            #     xvals = xvalues[key]
                            #     yvals = yvalues[key]
                             #    for i in range(0, len(xvals)):
                             #         activities.append([xvals[i], yvals[i]] )
                            #restore activities list with values from x and yvalues dict
              #  else:
                        
                        #log.info(" Difference image: "+str(np.amax(diff)) +"to "+str(config.diff_threshold))
                     #   activities = []

                if np.amax(diff) > config.diff_threshold:
                        # find the center points of the movement direction
                        activities = converter.findActivity(diff, prev_diff)
                        #cluster the activities and filter out almost linear cluster out
                        
                        xvalues, yvalues, correlation, cov00, cov01, cov11, dimension =calculateClusterWithDimension(activities, config.cluster_epsilon, config.cluster_min_samples)

                        if correlation is not None:
                            correlationDict = { key:value for (key,value) in correlation.items() if value < 0.85 and key != -1}
                            dimensionDict = { key:value for (key,value) in dimension.items() if value >100 and value <5000 and key != -1}
                            #correlationDict only includes the cluster which are not almost linear and not the noise
                            #dimensionDict only includes the cluster which have adequate size
                            #filter all not relevant clusters out of x and yvalues
                            activities = []
                            #must be in both dicts to be relevant
                            for key in correlationDict.keys():
                                 if key in dimensionDict.keys():
                                    xval = xvalues[key]
                                    yval = yvalues[key]
                                    activities.append([xval, yval] )
                else:
                        
                        #log.info(" Difference image: "+str(np.amax(diff)) +"to "+str(config.diff_threshold))
                    activities = []
             
                mask = converter.generateMask(current_grey, activities )
                 #add the mask to the maskqueue
                mask =maskqueue.addMask(mask)

                # save the current data for the next round
                maskqueue.setPrevGrey(current_grey)
                maskqueue.setPrevDiff(diff)
                if maskqueue.hadActivity() and not maskqueue.hasActivity():
                    stream.stopVideo()
                    log.info("Stopped Video")
                    noOFrames=0
                    log.info("No more Activity")
                elif not maskqueue.hadActivity() and maskqueue.hasActivity():
                    log.info("Start Video")
                    stream.startVideo()
                    log.info("Activity started at level: "+str(maskqueue.getActivityLevel()))
                    current_raw = stream.readraw()
                    out.save(current_raw, True, stream.getCurrentFilename(), noOFrames, int(time.time() * 1000))
                    
                    noOFrames+=1
                elif maskqueue.hadActivity() and maskqueue.hasActivity():
                    if noOFrames % config.rawImageInterval ==0:
                        log.info("Take snapshot and send cluster in file at frame "+str(noOFrames)+" and activity:"+str(maskqueue.getActivityLevel()))
                        
                        current_raw = stream.readraw()
                        out.save(current_raw, False,stream.getCurrentFilename(), noOFrames, int(time.time() * 1000))
                        curend=time.time()
                        log.info("Time elapsed: "+str(curend-start))
                    noOFrames+=1
                     
                end = time.time()
                
            #if it is night stop video and go to sleep
            else:
                if stream.isRecording:
                    stream.stopVideo()
                    log.info("Stopped Video")
                    noOFrames =0
                
                stream.sleep()
                log.info("Camera sleep")
                log.info("Night: nothing to do - sleep until "+str(decider.timeTo("sunrise")))
                time.sleep(decider.timeTo("sunrise"))
                
                stream.wakeup()
    except Exception as e:
        log.error(traceback.format_exc())
        sys.exit()
