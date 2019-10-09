import requests
from PIL import Image
from io import BytesIO

def get_image_size_by_url(url):
    data = requests.get(url).content
    im = Image.open(BytesIO(data))    
    return im.size

def get_image_size_by_str_stream(str_stream):
    im = Image.open(BytesIO(str_stream))
    return im.size

def oic_box2std(box, img_width, img_height, dec_digits=8):
    left = round(box[0]/img_width, dec_digits)
    top = round(box[1]/img_height, dec_digits)
    width = round((box[2]-box[0])/img_width, dec_digits)
    height = round((box[3]-box[1])/img_height, dec_digits)
    return [left, top, width, height]

if __name__ == "__main__":
    url = "http://4.bp.blogspot.com/_A2NamGQmyCc/TO1nWedGQQI/AAAAAAAAAnA/WxBVyEGHxjc/s1600/sbn_pic_2.jpg"
    width, height = get_image_size(url)
    print width, height
