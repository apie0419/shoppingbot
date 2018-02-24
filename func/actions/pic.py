from imgurpython import ImgurClient
from PIL import Image
from linebot.models import *
import os
from linebot import LineBotApi

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
client_id = os.getenv('IMGUR_CLIENT_ID', None)
client_secret = os.getenv('IMGUR_CLIENT_SECRET', None)

def save_pic(event, pic_id, con) :
    db = con.cursor()
    os.system("touch pic.jpg")
    os.system("touch pic-p.jpg")
    os.system("touch pic-b.jpg")
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('pic.jpg', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    img = Image.open('pic.jpg')
    width= img.width
    height = img.height
    if width > height :
        p_size = [240, int(height*(240/width))]
        new_size = [1024, int(height*(1024/width))]
    else : 
        p_size = [int(width*(240/height)), 240]
        new_size = [int(width*(1024/height)), 1024]
    print (p_size,new_size)
    new_img= img.resize((p_size[0], p_size[1]),Image.ANTIALIAS)
    new_img.save('pic-p.jpg',quality=100)
    new_img = img.resize((new_size[0], new_size[1]),Image.ANTIALIAS)
    new_img.save('pic-b.jpg',quality=100)
    client = ImgurClient(client_id, client_secret)
    picb = client.upload_from_path('pic-b.jpg', config = None, anon = False)
    picp = client.upload_from_path('pic-p.jpg', config = None, anon = False)
    db.execute("INSERT INTO pic_list(id, p_pic_path, b_pic_path) VALUES ({},'{}','{}')".format(pic_id, picp['link'], picb['link']))
    con.commit()
    db.close()
    return "OK"

def Trans_Pic(pic_id, con) :
    db = con.cursor()
    db.execute("SELECT b_pic_path,p_pic_path FROM pic_list WHERE id = {}".format(pic_id))
    pic_path = db.fetchone()
    db.close()
    if pic_path :
        return ImageSendMessage(
            original_content_url = pic_path[0],
            preview_image_url = pic_path[1]
        )
    else :
        return TextSendMessage(
            text = "本商品沒有相片喔～"
        )
        
