from linebot.models import *
from datetime import datetime
import os
import csv
import time
from linebot import (
    LineBotApi
)
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
def Excel(thing_id, userid, con) :
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['save_credentials_file'] = os.path.join(os.path.dirname(__file__), 'credentials.json')
    gauth.DEFAULT_SETTINGS['save_credentials'] = True
    gauth.DEFAULT_SETTINGS['save_credentials_backend'] = 'file'
    gauth.LoadCredentials()
    print (gauth.credentials)
    gauth.Refresh()
    gauth.Authorize()
    drive = GoogleDrive(gauth)
    db = con.cursor()
    db.execute("SELECT * FROM buy_list WHERE thing_id={}".format(thing_id))
    data = db.fetchall()
    os.system("touch {}.csv".format(thing_id))
    file = open('{}.csv'.format(thing_id), 'w',encoding='utf-8-sig')
    csvCursor = csv.writer(file)
    csvCursor.writerow(['買家姓名','Line暱稱','電話','購買數量','是否出貨','購買時間'])
    for d in data :
        profile = line_bot_api.get_profile(d[3])
        db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(d[3]))
        data_2 = db.fetchone()
        if d[4]=='check' :
            status = 'yes'
        else :
            status = 'no'
        csvCursor.writerow([data_2[0],profile.display_name,data_2[1],d[2],status,d[5]])
        print ([data_2[0],profile.display_name,data_2[1],d[2],status,d[5]])
    file.close()
    upload_file = drive.CreateFile()
    upload_file.SetContentFile('{}.csv'.format(thing_id))
    upload_file.Upload()
    upload_file.InsertPermission({'type' : 'anyone', 'value' : 'anyone', 'role' : 'reader'})
    return TextSendMessage(text=upload_file['alternateLink'])
