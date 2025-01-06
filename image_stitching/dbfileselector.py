from datetime import datetime
import os
import os.path
import time

import psycopg2

from mylog import MyLog
import os.path
from config import Configuration

# connection to index database where all filenames are listed

config = Configuration("config.yaml")
log = MyLog("environment_data.log")
from homography_helper import getEnum

def selectFilesByTimestamp(datestring, rootFolder):
    dbdatestring=convertDatetimeToDBString(convertStringToDatetime(datestring))
    print("Select imagepaths from db for: ", dbdatestring)
    dronelist=['drone-0-0', 'drone-0-2', 'drone-1-0', 'drone-E-1', 'drone-1-2', 'drone-2-0', 'drone-2-1', 'drone-2-2', 'drone-3-0', 'drone-3-1', 'drone-3-2']
    result={}
    try:
        db_conn = psycopg2.connect(host=config.db_host, database=config.db_database, user=config.db_user, password=config.db_password)
        cur = db_conn.cursor()
        for drone in dronelist:
            print("search for drone: ", drone)
            beevent_statement="select b.filename from bayerfiles b where b.source=%s order by abs(extract(epoch from (b.timestamp - timestamp %s))) limit 1;"
            cur.execute(beevent_statement,(drone, dbdatestring))
            filename =cur.fetchone()
            result[getEnum(drone)]=os.path.join(rootFolder, filename[0])
            
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("err",error)
        log.error(error)
    finally:
        if db_conn is not None:
            db_conn.close()
    return result


def selectFilesOfDrone(drone, rootFolder):
    print("Select imagepaths from db for: ", drone)
    result=[]
    try:
        db_conn = psycopg2.connect(host=config.db_host, database=config.db_database, user=config.db_user, password=config.db_password)
        cur = db_conn.cursor()
        beevent_statement="select b.filename from bayerfiles b where b.source=%s;"
        cur.execute(beevent_statement,(drone))
        filenames =cur.fetchall()
        for file in filenames:
            result.append(os.path.join(rootFolder, file[0]))
            
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("err",error)
        log.error(error)
    finally:
        if db_conn is not None:
            db_conn.close()
    return result

def convertStringToDatetime(datestring):
    """Converts a string in format 22-03-2023_18-15-13 to a datetime"""
    return datetime.strptime(datestring, '%d-%m-%Y_%H-%M-%S')

def convertDatetimeToDBString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    timestamp ="01-05-2023_05-00-00"
    selectFilesByTimestamp(timestamp, "K:/raw")