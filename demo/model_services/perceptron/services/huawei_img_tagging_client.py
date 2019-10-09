import sys
import json
import requests
import base64
from ais_sdk.gettoken import get_token
from ais_sdk.utils import encode_to_base64, download_url_base64
from ais_sdk.image_tagging import image_tagging
sys.path.append('/app/utils')
try:
    from msg import Result
except Exception as e:
    pass

huawei_username='mingwei_he'
huawei_password='Hmw_30423'
huawei_account_name = 'hwstaff_y00465251' # the same as user_name in commonly use

def huawei_image_tagging_by_url(ret, url):
    token = get_token(huawei_username, huawei_password, huawei_account_name)
    str_stream = requests.get(url).content
    base64_encoded_str=base64.b64encode(str_stream)
    result = image_tagging(token, base64_encoded_str, '', 'en', 5, 60)
    huawei_res_processing(ret, result)

def huawei_image_tagging_by_str_stream(ret, str_stream):
    token = get_token(huawei_username, huawei_password, huawei_account_name)
    base64_encoded_str = base64.b64encode(str_stream)
    result = image_tagging(token, base64_encoded_str, '', 'en', 5, 60)
    huawei_res_processing(ret, result)

def huawei_res_processing(ret, raw_res):
    result = json.loads(raw_res).get('result')
    if result:
        tags = result.get('tags')
        for tag in tags:
            ret.append(Result([], tag.get('tag'), round(float(tag.get('confidence'))/100., 8), [], ['huawei-image-tagging']).__dict__)

if __name__=='__main__':
   sys.path.append('/nfs_2/mingweihe/workspace/model_services/perceptron/utils')
   from msg import Result
   R = []
   huawei_image_tagging_by_url(R, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2A6ScS4YF5yoDxHP34oU52hHDgDRCOsu_mxVX503y62hIUz0V8Q')
   print(json.dumps(R))
