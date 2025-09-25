import os
import uuid
import sys
import json
import requests

function_list=["document", "new_knowledge_base", "document_parser", "document_parser_embedding", "delete_knowledge_base", "question_rag_search",
           "list_kbs", "list_docs", "delete_docs", "get_total_status", "upload_faqs", "get_qa_info", "get_files_statu", "chunk_embedding"]
question=""
user_id=""
kb_id=""
file_id=""
file_path=""


def document(host, port):
    url = f"http://{host}:{port}/api/docs"
    print("request url: ",url)
    try:
        response = requests.request("GET", url)
        print(response.text)
        # data=json.loads(response.text)
        # data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        # print(data_dumps)
    except Exception as e:
        print("Error:", e)


def new_knowledge_base(host, port):
    global user_id, kb_id
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    print("new_knowledge_base")
    url = f"http://{host}:{port}/api/qanything/new_knowledge_base"
    headers = {
        "Content-Type": "application/json",
    }

    payload = {"user_id": user_id, "kb_id": kb_id, "kb_name": "政务知识库"} #kb_id}
    # payload = {"user_id": "zzp", "kb_id": "KB6dae785cdd5d47a997e890521acbe1c2", "kb_name": "残联政策"}
    # payload = {"user_id": "zzp", "kb_id": "KB6dae785cdd5d47a997e890521acbe1c3", "kb_name": "发改局政策文件"}
    # payload = {"user_id": "zzp", "kb_id": "KB6dae785cdd5d47a997e890521acbe1c4", "kb_name": "区公安分局“答”板块"}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def delete_knowledge_base(host, port):
    global user_id, kb_id, file_id
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/delete_knowledge_base"
    headers = {
        "Content-Type": "application/json",
    }

    payload = {"user_id": user_id, "kb_id": kb_id}
    if file_id!="":
        payload["file_ids"]=[file_id]
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def list_kbs(host, port):
    global user_id
    if user_id == "":
        raise ValueError("user_id is empty")
    url = f"http://{host}:{port}/api/qanything/list_knowledge_base"
    headers = {
        "Content-Type": "application/json",
    }

    # payload = {"user_id": "zzp"}
    payload = {"user_id": user_id}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def list_docs(host, port):
    global user_id, kb_id
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/list_files"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {"user_id": user_id, "kb_id": kb_id}    
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def get_files_statu(host, port):
    global user_id, kb_id, file_id
    if user_id == "" or kb_id=="" or file_id=="":
        raise ValueError("user_id or kb_id or file_id is empty")
    url = f"http://{host}:{port}/api/qanything/get_files_statu"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {"user_id": user_id, "kb_id": kb_id, "file_ids": [file_id]}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)

    except Exception as e:
        print("Error:", e)


def document_parser(host, port):
    global user_id, file_path
    if user_id == "" or file_path=="":
        raise ValueError("user_id or file_path is empty")
    url = f"http://{host}:{port}/api/qanything/document_parser"

    payload = {"user_id": user_id}
    print("prompt:", payload)
    files=[('file', open(file_path,'rb'))]

    try:
        response = requests.request("POST", url, data=payload, files=files)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)

    except Exception as e:
        print("Error:", e)


def document_parser_embedding(host, port):
    global user_id, kb_id, file_path
    if user_id == "" or kb_id=="" or file_path=="":
        raise ValueError("user_id or kb_id or file_path is empty")
    url = f"http://{host}:{port}/api/qanything/document_parser_embedding"    
    payload = {
        "user_id": user_id,
        "kb_id": kb_id,
        "mode": "strong" #"soft"
    }

    files = []
    file_ids = []
    for root, dirs, file_names in os.walk(file_path):
        for file_name in file_names:
            # if file_name.endswith(".md"):  # 这里只上传后缀是md的文件，请按需修改，支持类型：
            if file_name.startswith("."):
                continue    
            file_path = os.path.join(root, file_name)
            # files.append(("files", open(file_path, "rb")))
            # file_ids.append(str(uuid.uuid4().hex))

            files = [("files", open(file_path, "rb"))]
            try:
                response = requests.post(url, data=payload, files=files)
                data=json.loads(response.text)
                data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
                print(data_dumps)
            
            except Exception as e:
                print("Error:", e)
            
        
    # payload["file_ids"] = ",".join(file_ids)
    # print("payload:",payload)
    # try:
    #     response = requests.post(url, data=payload, files=files)
    #     data=json.loads(response.text)
    #     data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
    #     print(data_dumps)
    
    # except Exception as e:
    #     print("Error:", e)


def chunk_embedding(host, port):
    global user_id, kb_id
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/chunk_embedding"
    payload = {"user_id": user_id, "kb_id": kb_id}
    
    chunk_datas = ["""OpenCV（Open Source Computer Vision）是一个开源的计算机视觉和机器学习软件库，广泛应用于图像处理和计算机视觉领域。以下是对OpenCV库的详细介绍：

一、概述

OpenCV是一个基于Apache 2.0许可的跨平台库，可以运行在Linux、Windows、Android和Mac OS等操作系统上。它由一系列C函数和少量C++类构成，同时提供了Python、Ruby、MATLAB等语言的接口，实现了图像处理和计算机视觉方面的很多通用算法。OpenCV主要倾向于实时视觉应用，并在可用时利用MMX和SSE指令。

二、功能特点

图像和视频I/O：支持多种格式的图像和视频数据的读写。
图像处理：包括图像缩放、旋转、仿射变换、图像平滑、边缘检测、直方图均衡化、二值化等操作。
特征检测和描述：包括SIFT、SURF、ORB、FAST等算法，能够检测图像中的关键点，并提取其特征描述符。
目标检测和跟踪：支持Haar级联检测、人脸识别、行人检测、物体跟踪等功能。
模板匹配：通过给定的模板，在图像中寻找与之匹配的区域。
机器学习：提供了一些机器学习算法的接口，如SVM、KNN、神经网络等，可以用于分类、回归等任务。
三维重建：通过多张2D图像，重建出3D模型。
图像分割：将图像分成若干个区域，每个区域都具有相似的属性，如颜色、纹理等。
深度学习：OpenCV还提供了一些深度学习相关的函数和工具，如深度学习模型的加载和推理。
三、版本历史

OpenCV的发展经历了多个版本，从最初的OpenCV alpha 3到现在的4.x系列版本，每个版本都带来了性能上的提升和新功能的加入。例如，OpenCV 4.7.0版带来了全新的ONNX层，大大提高了DNN代码的卷积性能。

四、特点归纳

开源性：OpenCV是一个开源的计算机视觉库，可以免费使用和修改。
跨平台性：支持多种操作系统和编程语言。
高效性：使用了优化的算法和数据结构，能够实现高效的图像处理和计算。
多功能性：提供了丰富的图像处理和计算机视觉算法。
可扩展性：支持与其他库的集成，方便进行扩展和定制。
用户友好性：提供了详细的在线文档和丰富的示例代码，方便用户快速入门和使用。
五、应用领域

OpenCV在计算机视觉领域有着广泛的应用，包括但不限于图像处理和分析、特征提取和描述、目标检测和跟踪、机器学习和模式识别、视频分析和处理、摄像头和摄像机标定、三维重建和深度感知等。由于其丰富的功能和高效的性能，OpenCV被广泛应用于各种实际场景中，如安全监控、自动驾驶、医疗影像分析等。""", 
"""Docker是一个开源的应用容器引擎，旨在让开发者能够更轻松地将应用及其依赖打包到可移植的容器中，并在任何流行的Linux或Windows操作系统上运行。以下是Docker的详细介绍：

1. Docker的概述
Docker基于客户端-服务器（C/S）架构，其中Docker客户端向Docker守护进程（Docker daemon）发送请求，守护进程执行请求并返回结果。
Docker使用沙箱机制，确保容器之间完全隔离，不会有任何接口。
Docker容器使用“写时复制”（copy-on-write）模型，使容器启动迅速，并减少资源消耗。
2. Docker的主要组件
Docker Client：客户端，用于与Docker守护进程通信，发送请求。
Docker Daemon：守护进程，接受客户端请求并执行操作。
Docker Image：镜像，是只读的容器模板，包含启动容器所需的文件系统结构和内容。
Docker Container：容器，基于镜像创建的实例，用于运行应用程序。
Registry：镜像仓库，用于存储和分发Docker镜像。
3. Docker的特点
上手快：用户只需几分钟就可以将应用程序“Docker化”，并且大多数Docker容器只需不到1秒即可启动。
职责的逻辑分类：开发人员只需关心容器中运行的应用程序，而运维人员只需关心如何管理容器。
快速高效的开发生命周期：Docker缩短了从开发、测试到部署、上线的周期，提高了应用程序的可移植性和可构建性。
微服务架构支持：Docker鼓励使用面向服务的体系结构和微服务架构，每个微服务可以封装为一个独立的容器。
4. Docker的应用场景
应用程序的快速部署和交付：Docker允许将应用程序及其依赖项打包为容器，简化了在不同环境中的部署过程。
多租户隔离：Docker可以在同一物理主机上运行多个隔离的容器，避免了应用程序之间的冲突和干扰。
快速开发和测试环境：开发人员可以使用Docker快速创建开发和测试环境，减少在不同机器上配置环境的麻烦。
混合云和多云部署：Docker容器可以在不同的云平台和服务器上运行，实现了跨云和混合云部署。
5. Docker的架构
Docker的总体架构是一个C/S模式的架构，用户通过Docker Client与Docker Daemon建立通信，发送请求给守护进程，守护进程处理请求并返回结果。Docker Daemon中包含了Docker Server、Docker Engine、镜像管理驱动Graphdriver、网络管理驱动Networkdriver和Execdriver等组件，它们共同协作完成Docker内部的工作。

总之，Docker通过其强大的功能和灵活的应用场景，已经成为现代软件开发和运维中不可或缺的工具之一。
"""]
    payload["chunk_datas"] =chunk_datas
    print("payload:",payload)
    try:
        response = requests.post(url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    
    except Exception as e:
        print("Error:", e)


def delete_docs(host, port):
    global user_id, kb_id, file_id
    if user_id == "" or kb_id=="" or file_id=="":
        raise ValueError("user_id or kb_id or file_id is empty")
    url = f"http://{host}:{port}/api/qanything/delete_files"
    payload = {"user_id": user_id, "kb_id": kb_id, "file_ids": [file_id]}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def question_rag_search(host, port):
    global user_id, kb_id, question
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/question_rag_search"
    if question=="":
        question = input("请输入问题：")
        print("问题：", question)

    payload = {"user_id": user_id, "question": question, "kb_ids": [kb_id], "networking": False}
    print("payload:",payload)

    try:
        response = requests.request("POST", url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)
    except Exception as e:
        print("Error:", e)


def get_total_status(host, port):
    global user_id
    if user_id == "":
        raise ValueError("user_id is empty")
    url = f"http://{host}:{port}/api/qanything/get_total_status"
    payload = {"user_id": user_id}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)

    except Exception as e:
        print("Error:", e)


def upload_faqs(host, port):
    global user_id, kb_id, file_path
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/upload_faqs"
    payload = {
        "user_id": user_id, 
        "kb_id": kb_id, 
        "faqs": [{"question": "如何使用python", "answer": "python是一种编程语言，可以用来开发各种应用程序。参考教程：https://www.runoob.com/python3/python3-tutorial.html"}, 
                 {"question": "如何使用docker", "answer": "Docker是一个开源的应用容器引擎，参考教程：https://www.runoob.com/docker/docker-tutorial.html"}]}
    print("prompt:", payload)

    
    if os.path.exists(file_path):
        import pandas as pd
        df = pd.read_excel(file_path)
        faqs = [{"question": row["question"], "answer": row["answer"]} for index, row in df.iterrows()]
        payload["faqs"] = faqs
        print("payload load file faqs size:", len(faqs))

    try:
        response = requests.request("POST", url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)

    except Exception as e:
        print("Error:", e)


def get_qa_info(host, port):
    global user_id, kb_id
    if user_id == "" or kb_id=="":
        raise ValueError("user_id or kb_id is empty")
    url = f"http://{host}:{port}/api/qanything/get_qa_info"
    payload = {"user_id": user_id, "kb_id": kb_id}
    print("prompt:", payload)

    try:
        response = requests.request("POST", url, json=payload)
        data=json.loads(response.text)
        data_dumps = json.dumps(data, ensure_ascii=False, indent=4)
        print(data_dumps)

    except Exception as e:
        print("Error:", e)



def usage():
    print("Usage:")
    print(f"python {sys.argv[0]} --api=\"api_name\" [--host=0.0.0.0 --port=8777 --user_id=xxx --kb_id=xxx --file_id=xxx --file_path=xxx]")
    print("可用的api：", function_list)





if __name__ == "__main__":
    host = "127.0.0.1" #"0.0.0.0"
    port = 8777
    api = ""
    
    for arg in sys.argv[1:]:
        if arg=='--help' or arg=='-h':
            usage()
            sys.exit(0)
        elif arg.startswith('--host='):
            host = arg.split('=')[1]
        elif arg.startswith('--port='):
            port = int(arg.split('=')[1])
        elif arg.startswith('--api='):
            api = arg.split('=')[1]
        elif arg.startswith('--question='):
            question = arg.split('=')[1]
        elif arg.startswith('--user_id='):
            user_id = arg.split('=')[1]
        elif arg.startswith('--kb_id='):
            kb_id = arg.split('=')[1]
        elif arg.startswith('--file_id='):
            file_id = arg.split('=')[1]
        elif arg.startswith('--file_path='):
            file_path = arg.split('=')[1]
        else:
            print(f"Unknown argument: {arg}")
        
            
    print(f"host: {host}, port: {port}")
    print(f"api: {api}")

    if api in function_list:
        eval(api)(host, port)
    else:
        print(f"api:{api} is not exsit.")
        usage()
        



