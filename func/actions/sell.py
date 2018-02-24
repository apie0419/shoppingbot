from linebot.models import *
import os
from .pic import save_pic
from linebot import (
    LineBotApi
)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

def Sell(event, status, userid,con) :
    db = con.cursor()
    if not status :
        s = "enter_name"
        db.execute("INSERT INTO sell_list (userid, status) VALUES (%s, %s)",(userid, s))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入商品名:")
    elif status[0][0] == 'enter_pic' :
        if isinstance(event.message, ImageMessage) :
            db.execute("SELECT id FROM sell_list WHERE userid='{}' and status='enter_pic'".format(userid))
            pic_id = db.fetchone()
            line_bot_api.push_message(
                userid,
                TextSendMessage(
                    text="圖片上傳中，請稍候..."
                )
            )
            if save_pic(event,pic_id[0], con) == "OK" :
                db.execute("UPDATE sell_list SET status='modify_pic' WHERE userid='{}' and status='enter_pic'".format(userid))
                db.execute("SELECT b_pic_path FROM pic_list WHERE id = {}".format(pic_id[0]))
                pic_path = db.fetchone()
                con.commit()
                db.close()
                return TemplateSendMessage(
                        alt_text = 'Demo',
                        template = ButtonsTemplate(
                            text = "商品資訊會呈現這種形式，確定使用此圖嗎？",
                            thumbnail_image_url = pic_path[0],
                            actions = [
                                MessageTemplateAction(
                                    label = 'Yes',
                                    text = 'Yes',
                                ),
                                MessageTemplateAction(
                                    label = 'No',
                                    text = 'No'
                                )
                            ]
                        )
                    )
            else :
                return TextSendMessage(
                    text = "圖片傳送失敗，請重傳"
                    )
        else :
            db.close()
            return TextSendMessage(text="請傳入圖片喔～\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
    elif (status[0][0]=="enter_price" or status[0][0]=="enter_amount" or status[0][0]=="modify_price" or status[0][0]=="modify_amount") and not event.message.text.isdigit() :
        db.close()
        return TextSendMessage(text="只需要輸入數字，請重新輸入\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
    elif status[0][0]=="enter_name":
        s = "enter_price"
        SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='enter_name' and userid='{}';".format(event.message.text, s, userid)
        db.execute(SQL)
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入單價:")
    elif status[0][0]=="enter_price":
        s = "enter_amount"
        db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='enter_price' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入提供數量:")
    elif status[0][0]=="enter_amount":
        s = "enter_intro"
        db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='enter_amount' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TextSendMessage(text="請輸入介紹或優惠:")
    elif status[0][0]=="enter_intro":
        s = "modify"
        db.execute("SELECT name,price,amount FROM sell_list WHERE status='enter_intro' and userid='{}'".format(userid))
        data = db.fetchall()
        db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='enter_intro' and userid='{}'".format(event.message.text, s, userid))
        con.commit()
        db.close()
        line_bot_api.push_message(
            userid,
            TextSendMessage(
                text="商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+event.message.text
                )
            )
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確",
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
    elif status[0][0]=="ask_pic" :
        if event.message.text=='Yes' :
            db.execute("UPDATE sell_list SET status='enter_pic' WHERE userid='{}' and status='ask_pic'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(
                text='請傳入你想使用的圖片\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"'
            )
        else :
            s = 'finish'
            db.execute("SELECT * FROM group_list")
            ids = db.fetchall()
            db.execute("SELECT id,name,amount,price FROM sell_list WHERE userid='{}' and status='ask_pic'".format(userid))
            data = db.fetchall()
            number = data[0][0]
            name = data[0][1]
            amount = data[0][2]
            price = data[0][3]
            db.execute("UPDATE sell_list SET status='{}' WHERE status='ask_pic' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            profile = line_bot_api.get_profile(userid)
            for i in ids :
                line_bot_api.push_message(
                    i[0],
                    TemplateSendMessage(
                        alt_text='template',
                        template=ButtonsTemplate(
                            title='商品編號#{}'.format(number),
                            text='商品名稱: {}\n單價: {}\n數量: {}'.format(name, price, amount),
                            actions=[
                                PostbackTemplateAction(
                                    label='商品詳情',
                                    data='info,{}'.format(number),
                                )
                            ]
                        )
                    )
                )
            db.close()
            return TextSendMessage(text="產品新增成功")
    elif status[0][0]=="modify_name":
        db.execute("SELECT price,amount,intro FROM sell_list WHERE status='modify_name' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        SQL = "UPDATE sell_list SET name='{}',status='{}' WHERE status='modify_name' and userid='{}';".format(event.message.text, s, userid)
        db.execute(SQL)
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+event.message.text+"\n單價:"+str(data[0][0])+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_price":
        db.execute("SELECT name,amount,intro FROM sell_list WHERE status='modify_price' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET price={},status='{}' WHERE status='modify_price' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+data[0][0]+"\n單價:"+event.message.text+"\n數量:"+str(data[0][1])+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_amount":
        db.execute("SELECT name,price,intro FROM sell_list WHERE status='modify_amount' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET amount={},status='{}' WHERE status='modify_amount' and userid='{}'".format(int(event.message.text), s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+event.message.text+"\n介紹及優惠:"+data[0][2],
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
    elif status[0][0]=="modify_intro":
        db.execute("SELECT name,price,amount FROM sell_list WHERE status='modify_intro' and userid='{}'".format(userid))
        data = db.fetchall()
        s = "modify"
        db.execute("UPDATE sell_list SET intro='{}',status='{}' WHERE status='modify_intro' and userid='{}'".format(event.message.text, s, userid))
        con.commit()
        db.close()
        return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+event.message.text,
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
    elif status[0][0] == "modify_pic" :
        if event.message.text=="Yes" :
            s = 'finish'
            db.execute("SELECT * FROM group_list")
            ids = db.fetchall()
            db.execute("SELECT id,name,amount,price FROM sell_list WHERE userid='{}' and status='modify_pic'".format(userid))
            data = db.fetchall()
            number = data[0][0]
            name = data[0][1]
            amount = data[0][2]
            price = data[0][3]
            db.execute("SELECT b_pic_path FROM pic_list WHERE id = {}".format(number))
            pic_path = db.fetchone()
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify_pic' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            profile = line_bot_api.get_profile(userid)
            for i in ids :
                line_bot_api.push_message(
                    i[0],
                    TemplateSendMessage(
                        alt_text='template',
                        template=ButtonsTemplate(
                            thumbnail_image_url = pic_path[0],
                            title = '商品編號#{}'.format(number),
                            text = '商品名稱: {}\n單價: {}\n數量: {}'.format(name, price, amount),
                            actions = [
                                PostbackTemplateAction(
                                    label='商品詳情',
                                    data='info,{}'.format(number),
                                )
                            ]
                        )
                    )
                )
            db.close()
            return TextSendMessage(text="產品新增成功")
        else :
            db.execute("UPDATE sell_list SET status='enter_pic' WHERE status='modify_pic' and userid='{}'".format(userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請重新傳入圖片\n若要取消本次交易，請按\"功能列表\"內的\"取消輸入\"")
    elif status[0][0]=="modify" :
        if event.message.text=='Yes' : 
            db.execute("UPDATE sell_list SET status='ask_pic' WHERE userid='{}' and status='modify'".format(userid))
            con.commit()
            db.close()
            return TemplateSendMessage(
                alt_text="Confirm",
                template=ConfirmTemplate(
                    text="請問需要新增圖片嗎？",
                    actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='Yes'
                        ),
                    MessageTemplateAction(
                        label='No',
                        text='No'
                        )
                    ]
                )
            )
        elif event.message.text=='No' :
            line_bot_api.push_message(
                userid,
                TextSendMessage(text="請點選需要修改的項目")
            )
            return ImagemapSendMessage(
                base_url='https://stu-web.tkucs.cc/404411091/linebot/Change/260.png?_ignored=',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=260, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='商品名',
                        area=ImagemapArea(
                            x=0, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='單價',
                        area=ImagemapArea(
                            x=347, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='數量',
                        area=ImagemapArea(
                            x=694, y=0, width=346, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='介紹及優惠',
                        area=ImagemapArea(
                            x=0, y=130, width=520, height=130
                        )
                    ),
                    MessageImagemapAction(
                        text='Yes',
                        area=ImagemapArea(
                            x=520, y=130, width=520, height=130
                        )
                    )
                ]
            )
        elif event.message.text=="商品名" :
            s = "modify_name"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return  TextSendMessage(text="請輸入商品名:")
        elif event.message.text=="單價" :
            s = "modify_price"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入單價:")
        elif event.message.text=="數量" :
            s = "modify_amount"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入數量:")
        elif event.message.text=="介紹及優惠":
            s = "modify_intro"
            db.execute("UPDATE sell_list SET status='{}' WHERE status='modify' and userid='{}'".format(s, userid))
            con.commit()
            db.close()
            return TextSendMessage(text="請輸入介紹及優惠:")
        else :
            db.execute("SELECT name,price,amount,intro FROM sell_list WHERE userid='{}' and status='modify'".format(userid))
            data = db.fetchall()
            db.close()
            return TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text="輸入完畢，請確認內容是否正確\n商品名:"+data[0][0]+"\n單價:"+str(data[0][1])+"\n數量:"+str(data[0][2])+"\n介紹及優惠:"+data[0][3],
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