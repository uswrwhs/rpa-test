# import base64
# import requests
# import datetime
# from io import BytesIO
#
# from DrissionPage._pages.chromium_page import ChromiumPage
# from PIL import Image
#
# t1 = datetime.datetime.now()
#
#
# # PIL图片保存为base64编码
# def PIL_base64(img, coding='utf-8'):
#     img_format = img.format
#     if img_format == None:
#         img_format = 'JPEG'
#
#     format_str = 'JPEG'
#     if 'png' == img_format.lower():
#         format_str = 'PNG'
#     if 'gif' == img_format.lower():
#         format_str = 'gif'
#
#     if img.mode == "P":
#         img = img.convert('RGB')
#     if img.mode == "RGBA":
#         format_str = 'PNG'
#         img_format = 'PNG'
#
#     output_buffer = BytesIO()
#     # img.save(output_buffer, format=format_str)
#     img.save(output_buffer, quality=100, format=format_str)
#     byte_data = output_buffer.getvalue()
#     base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode(coding)
#
#     return base64_str
#
#
# def rotate_image_f(page: ChromiumPage, outer: ChromiumPage):
#
#
#
#     # 加载外圈大图
#     img1 = Image.open('./publicPicture/big.jpeg')
#     # 图片转base64
#     img1_base64 = PIL_base64(img1)
#     # 加载内圈小图
#     img2 = Image.open('./publicPicture/little.jpeg')
#     # 图片转base64
#     img2_base64 = PIL_base64(img2)
#
#     # 验证码识别接口
#     url = "http://www.detayun.cn/openapi/verify_code_identify/"
#     data = {
#         # 用户的key
#         "key": "Yrebvsf3hz73ZGqles5D",
#         # 验证码类型
#         "verify_idf_id": "37",
#         # 外圈大图
#         "img1": img1_base64,
#         # 内圈小图
#         "img2": img2_base64,
#     }
#     header = {"Content-Type": "application/json"}
#
#     # 发送请求调用接口
#     response = requests.post(url=url, json=data, headers=header)
#
#     # 获取响应数据，识别结果
#     result = response.json()
#     print(result)
#
#     length = 270 / 360 * result['data']['angle']
#     print(length)
#     print("耗时：", datetime.datetime.now() - t1)
#
#
# if __name__ == '__main__':
#     # rotate_image()
#     pass
