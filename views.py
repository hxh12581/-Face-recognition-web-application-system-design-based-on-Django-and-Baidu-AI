import uuid

from django.shortcuts import render
from aip import AipFace
from app01 import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse



@csrf_exempt  # 取消跨站请求伪造（CSRF）防护。
def face_login(request):
    """
    :param request:
    :return: result:
    :author:何晓辉
    :time:2023/10/27
    :function: 人脸登录
    """
    appId = ""
    apiKey = ""
    secretKey = ""
    imageType = "BASE64"
    # 前期用户申请的百度API的关键码
    client = AipFace(appId, apiKey, secretKey)
    # 初始化AipFace对象
    imageData = request.POST.get("imageData")  # 获取前端AJAX的图像数据
    # print(imageData)
    options = {"max_face_num": 1, "face_field": 'age,beauty,gender,emotion'}  # 设置请求参数
    result = client.detect(imageData, imageType, options)  # 调用人脸检测函数 有参:options
    print(result)
    # print("年龄为:{}".format(result["result"]["face_list"][0]["age"]))
    # print("颜值打分:{}".format(result["result"]["face_list"][0]["beauty"]))
    # print("性别:{}".format(result["result"]["face_list"][0]["gender"]["type"]))
    # print("情绪:{}".format(result["result"]["face_list"][0]["emotion"]["type"]))
    if result["error_msg"] in "SUCCESS":
        mr = models.Group.objects.all()  # 获取数据库中的用户信息
        for i in range(models.Group.objects.count()):
            user_obj = mr[i]
            face_list = user_obj.userFace
            mr1 = {'image': face_list, 'image_type': imageType}
            mr2 = {'image': imageData, 'image_type': imageType}
            faceList = [mr1, mr2]
            matchResult = client.match(faceList)
            print(matchResult)
            if matchResult["error_msg"] in "SUCCESS":
                score = matchResult['result']['score']
                if score > 60:
                    result["face_login"] = "SUCCESS"
                    result["match_success_username"] = user_obj.username
                    result["user_age"] = result["result"]["face_list"][0]["age"]
                    result["user_beauty"] = result["result"]["face_list"][0]["beauty"]
                    result["user_gender"] = result["result"]["face_list"][0]["gender"]["type"]
                    result["user_emotion"] = result["result"]["face_list"][0]["emotion"]["type"]
                    break

    return JsonResponse(result)



@csrf_exempt
def face_reg(request):
    """
       :param request:
       :return: result:
       :author:何晓辉
       :time:2023/10/27
       :function: 人脸录入
    """
    appId = ""
    apiKey = ""
    secretKey = ""
    imageType = "BASE64"
    client = AipFace(appId, apiKey, secretKey)
    reg_message = models.Group.objects.all()
    user_message = models.User.objects.last()
    username = user_message.username
    password = user_message.password
    all_message = models.User.objects.all()
    group_id = str(reg_message.count() // 4)
    user_id = str(all_message.count())
    imageData = request.POST.get("imageData")
    options = {"max_face_num": 10}
    result = client.detect(imageData, imageType, options)
    print(result)
    if result["error_msg"] in "SUCCESS":
        reg = client.addUser(imageData, imageType, group_id, user_id)
        # print(reg)
        if reg['error_code'] == 0:
            result["face_reg"] = "SUCCESS"
            models.Group.objects.create(user_id=user_id, username=username, password=password,
                                        group_id=group_id, count=reg_message.count() + 1, userFace=imageData)
    return JsonResponse(result)

