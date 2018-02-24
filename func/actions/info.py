from linebot.models import *
import os
import re
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

# test
def Info(event, userid, status,con) :
    db = con.cursor()
    if not status :
        db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        db.execute("UPDATE user_list SET status='modify' WHERE userid='{}'".format(userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
	        alt_text='Confirm template',
	        template=ConfirmTemplate(
	            text="資料正確嗎？\n姓名:"+data[0][0]+"\n手機:"+data[0][1],
	            actions=[
	            MessageTemplateAction(
	                label='Yes',
	                text='Yes',
	                    ),
	            MessageTemplateAction(
	                label='No',
	                text='No'
	                )
	             ]
	        )
         )
    if status[0][0] == "new" :
        db.execute("UPDATE user_list SET status='enter_name' WHERE userid='{}'".format(userid))
        con.commit()
        db.close()
        return TextSendMessage(
    	text="您是第一次輸入資料\n請先輸入姓名:"
    	)
    elif status[0][0] == "enter_name" :
        db.execute("UPDATE user_list SET status='enter_phone', name='{}' WHERE userid='{}'".format(event.message.text, userid))
        con.commit()
        db.close()
        return TextSendMessage(
    	text="請輸入手機號碼 : "
    	)
    elif status[0][0] == "enter_phone" :
        if len(event.message.text)!=10 or not re.match(r'09(.+)',event.message.text) :
            return TextSendMessage(
    	    text="格式輸入錯誤 請重新輸入"
    	)
        db.execute("UPDATE user_list SET status='modify', phone='{}' WHERE userid='{}'".format(event.message.text, userid))
        con.commit()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n姓名:"+data[0][0]+"\n手機:"+event.message.text,
                actions=[
                MessageTemplateAction(
                    label='Yes',
                    text='Yes',
                        ),
                MessageTemplateAction(
                    label='No',
                    text='No'
                    )
                 ]
            )
         )
    elif status[0][0] == "modify" :
        if event.message.text == "Yes" :
            db.execute("UPDATE user_list SET status='finish' WHERE userid='{}'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(
                 text="用戶資料更改完成"
            )
        elif event.message.text == "No" :
            db.close()
            line_bot_api.push_message(
                userid,
                TextSendMessage(
                    text="請點選需要更改的項目"
                )
            )
            return ImagemapSendMessage(
                base_url='https://stu-web.tkucs.cc/404411091/linebot/Change/130_2.png?_ignored=',
                alt_text='用戶資料更改',
                base_size=BaseSize(height=130, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='姓名',
                        area=ImagemapArea(
                            x=0, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='手機',
                        area=ImagemapArea(
                            x=347, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='Yes',
                        area=ImagemapArea(
                            x=694, y=0, width=346, height=130
                        )
                    )
                ]
            )
        elif event.message.text == "姓名" :
              db.execute("UPDATE user_list SET status='modify_name' WHERE userid='{}'".format(userid))
              con.commit()
              db.close()
              return TextSendMessage(
                    text="請輸入姓名:"
                    )
        elif event.message.text == "手機" :
              db.execute("UPDATE user_list SET status='modify_phone' WHERE userid='{}'".format(userid))
              con.commit()
              db.close()
              return TextSendMessage(
                   text="請輸入手機號碼 : "
                   )
        else :
            db.execute("SELECT name,phone FROM user_list WHERE userid='{}'".format(userid))
            data = db.fetchone()
            db.close()
            return TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text="輸入完畢，請確認內容是否正確\n姓名:"+data[0]+"\n手機:"+data[1],
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes',
                      ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                    )
                    ]
                )
             )
    elif status[0][0] == "modify_name" :
        db.execute("UPDATE user_list SET status='modify',name='{}' WHERE userid='{}'".format(event.message.text,userid))
        con.commit()
        db.execute("SELECT phone FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n姓名:"+event.message.text+"\n手機:"+data[0][0],
                actions=[
                MessageTemplateAction(
                    label='Yes',
                    text='Yes',
                        ),
                MessageTemplateAction(
                    label='No',
                    text='No'
                    )
                 ]
            )
         )
    elif status[0][0] == "modify_phone" :
        if len(event.message.text)!=10 or not re.match(r'09(.+)',event.message.text) :
            return TextSendMessage(
    	    text="格式輸入錯誤 請重新輸入"
    	)
        db.execute("UPDATE user_list SET status='modify',phone='{}' WHERE userid='{}'".format(event.message.text,userid))
        con.commit()
        db.execute("SELECT name FROM user_list WHERE userid='{}'".format(userid))
        data = db.fetchall()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n姓名:"+data[0][0]+"\n手機:"+event.message.text,
                actions=[
                MessageTemplateAction(
                    label='Yes',
                    text='Yes',
                        ),
                MessageTemplateAction(
                    label='No',
                    text='No'
                    )
                 ]
            )
         )