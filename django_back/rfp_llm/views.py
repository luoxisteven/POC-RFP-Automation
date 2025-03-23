import os
import json
import shutil 
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from RAG_Chain import *

# Create your views here.

def get_client_ip(request):
    """获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


## get
def get(request):
    # 获取客户端 IP 地址
    client_ip = get_client_ip(request)
    print(f"Request received from IP: {client_ip}")  # 打印 IP 地址
    
    data_dir = "./data"
    company_profile_dir = os.path.join(data_dir, "company_profile")
    rfp_dir = os.path.join(data_dir, "rfp")

    # 获取 company_profile 文件夹下的文件，包括子文件夹中的文件
    def list_files(directory):
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                # 忽略 .DS_Store 文件
                if filename != ".DS_Store":
                    files.append(filename)
        return files

    company_profiles = list_files(company_profile_dir)

    # 获取 rfp 文件夹下的文件
    rfps = {}
    if os.path.exists(rfp_dir):
        for rfp_folder in os.listdir(rfp_dir):
            rfp_folder_path = os.path.join(rfp_dir, rfp_folder)
            if os.path.isdir(rfp_folder_path):
                rfps[rfp_folder] = [
                    file for file in os.listdir(rfp_folder_path) if file != ".DS_Store"
                ]

    # 组织成 JSON 格式
    data = {
        "company_profiles": company_profiles,
        "rfps": rfps,
    }
    return JsonResponse(data)


## add_company_profile
@csrf_exempt
def add_company_profile(request):
    if request.method == "POST":
        # 检查是否有文件在请求中
        if "file" not in request.FILES:
            return HttpResponseBadRequest("No file provided in request")

        # 获取上传的文件
        uploaded_file = request.FILES["file"]

        # 获取文件的原始文件名
        original_file_name = uploaded_file.name

        # 文件保存路径
        data_dir = "./data"
        company_profile_dir = os.path.join(data_dir, "company_profile")
        os.makedirs(company_profile_dir, exist_ok=True)
        file_path = os.path.join(company_profile_dir, original_file_name)

        # 删掉所有的rag_chain
        cache.clear()
        
        # 将文件内容写入到指定路径
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():  # 使用 .chunks() 处理大文件
                f.write(chunk)
        
        return JsonResponse({"status": "success", "message": f"File '{original_file_name}' uploaded to company profiles."})
    else:
        return HttpResponseBadRequest("Invalid request method")


## del_company_profile
@csrf_exempt  # 开发环境使用，生产环境请确保添加 CSRF token
def del_company_profile(request):
    if request.method == "POST":
        # 从请求的 JSON 数据中获取文件名
        try:
            data = json.loads(request.body)
            file_name = data.get("file_name")
            print(file_name)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")

        # 确保 file_name 不为空
        if not file_name:
            return HttpResponseBadRequest("Missing file name")

        # 文件路径
        data_dir = "./data"
        company_profile_dir = os.path.join(data_dir, "company_profile")
        file_path = os.path.join(company_profile_dir, file_name)
        
        # 打印调试路径
        print("文件路径：", file_path)

        # 检查文件是否存在
        if os.path.exists(file_path):
            os.remove(file_path)
            return JsonResponse({"status": "success", "message": f"File '{file_name}' deleted from company profiles."})
        else:
            return JsonResponse({"status": "error", "message": "File not found"})

    else:
        return HttpResponseBadRequest("Invalid request method")

## add_project
@csrf_exempt
def add_project(request):
    if request.method == "POST":
        # 尝试解析 JSON 数据
        try:
            data = json.loads(request.body)
            project_name = data.get("project_name")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")

        # 确保 project_name 不为空
        if not project_name:
            return HttpResponseBadRequest("Missing project name")

        # 项目文件夹路径
        data_dir = "./data"
        rfp_dir = os.path.join(data_dir, "rfp")
        project_dir = os.path.join(rfp_dir, project_name)

        # 检查是否已经存在同名文件夹
        if os.path.exists(project_dir):
            return JsonResponse({"status": "error", "message": f"Project '{project_name}' already exists."})

        # 创建项目文件夹
        os.makedirs(project_dir, exist_ok=True)

        return JsonResponse({"status": "success", "message": f"Project '{project_name}' created in rfp directory."})
    else:
        return HttpResponseBadRequest("Invalid request method")


## del_project
@csrf_exempt
def del_project(request):
    if request.method == "POST":
        # 尝试解析 JSON 数据
        try:
            data = json.loads(request.body)
            project_name = data.get("project_name")
            print(123)
            print(project_name)
            print(1234)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")

        # 确保 project_name 不为空
        if not project_name:
            return HttpResponseBadRequest("Missing project name")

        # 项目文件夹路径
        data_dir = "./data"
        rfp_dir = os.path.join(data_dir, "rfp")
        project_dir = os.path.join(rfp_dir, project_name)

        # 检查文件夹是否存在
        if not os.path.exists(project_dir):
            return JsonResponse({"status": "error", "message": f"Project '{project_name}' not found."})

        try:
            # Delete cache
            cache_key = f"rag_chain_{project_name}"
            rag_chain = cache.get(cache_key)
            if rag_chain:
                cache.delete(cache_key)
                
             # 删除文件夹及其所有内容
            shutil.rmtree(project_dir)
            return JsonResponse({"status": "success", "message": f"Project '{project_name}' and all its contents were deleted."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to delete project '{project_name}': {str(e)}"})

    else:
        return HttpResponseBadRequest("Invalid request method")


## add_project_file
@csrf_exempt
def add_project_file(request):
    if request.method == "POST":
        # 从请求中获取 project_name
        project_name = request.POST.get("project_name")

        # 确保 project_name 和文件存在
        if not project_name:
            return HttpResponseBadRequest("Missing project name")
        if "file" not in request.FILES:
            return HttpResponseBadRequest("No file provided in request")

        # 获取上传的文件
        uploaded_file = request.FILES["file"]
        file_name = uploaded_file.name  # 获取文件的原始文件名

        # 目标文件夹路径
        data_dir = "./data"
        project_dir = os.path.join(data_dir, "rfp", project_name)

        # 检查项目文件夹是否存在
        if not os.path.exists(project_dir):
            return JsonResponse({"status": "error", "message": f"Project '{project_name}' directory not found."})

        # 保存文件路径
        file_path = os.path.join(project_dir, file_name)
        
        # Delete cache
        cache_key = f"rag_chain_{project_name}"
        rag_chain = cache.get(cache_key)
        if rag_chain:
            cache.delete(cache_key)

        # 将文件内容写入到指定路径
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():  # 使用 .chunks() 处理大文件
                f.write(chunk)

        return JsonResponse({"status": "success", "message": f"File '{file_name}' added to project '{project_name}'."})
    else:
        return HttpResponseBadRequest("Invalid request method")


## del_project_file
@csrf_exempt
def del_project_file(request):
    if request.method == "POST":
        # 从请求中获取 project_name 和 file_name
        project_name = request.POST.get("project_name")
        file_name = request.POST.get("file_name")

        # 确保 project_name 和 file_name 不为空
        if not project_name:
            return HttpResponseBadRequest("Missing project name")
        if not file_name:
            return HttpResponseBadRequest("Missing file name")

        # 构建文件路径
        data_dir = "./data"
        project_dir = os.path.join(data_dir, "rfp", project_name)
        file_path = os.path.join(project_dir, file_name)

        # 检查项目文件夹和文件是否存在
        if not os.path.exists(project_dir):
            return JsonResponse({"status": "error", "message": f"Project '{project_name}' directory not found."})
        if not os.path.isfile(file_path):
            return JsonResponse({"status": "error", "message": f"File '{file_name}' not found in project '{project_name}'."})

        try:
             # Delete cache
            cache_key = f"rag_chain_{project_name}"
            rag_chain = cache.get(cache_key)
            if rag_chain:
                cache.delete(cache_key)
                
            # 删除文件
            os.remove(file_path)
        
            return JsonResponse({"status": "success", "message": f"File '{file_name}' deleted from project '{project_name}'."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to delete file '{file_name}': {str(e)}"})
    else:
        return HttpResponseBadRequest("Invalid request method")
    

@csrf_exempt
def get_question(request):
    project_name = request.POST.get("project_name")

    if not project_name:
        return HttpResponseBadRequest("Missing project name")
    
    data_dir = "./data"
    project_dir = os.path.join(data_dir, "rfp", project_name)

    # Check if the project directory exists
    if not os.path.exists(project_dir):
        return JsonResponse({"status": "error", "message": f"Project directory '{project_name}' not found."})
    
    # Create a new RAG_Chain instance and store it in cache
    rag_chain = RAG_Chain(rfp_path=project_dir)
    # cache.set(cache_key, rag_chain, timeout=None)  # Cache indefinitely

    # Get the list of questions
    question_list = rag_chain.question_extraction()

    # Convert the list to a numbered string
    answer = "\n".join([f"{i+1}. {question}" for i, question in enumerate(question_list)])
    
    return JsonResponse({"status": "success", "answer": answer})
    

# Get answer function to retrieve the answer using cached RAG_Chain instance
@csrf_exempt
def get_simple_answer(request):
    project_name = request.POST.get("project_name")
    query = request.POST.get("query")

    if not project_name or not query:
        return HttpResponseBadRequest("Missing project name or query")
    
    data_dir = "./data"
    project_dir = os.path.join(data_dir, "rfp", project_name)

    # Check if the project directory exists
    if not os.path.exists(project_dir):
        return JsonResponse({"status": "error", "message": f"Project directory '{project_name}' not found."})
    
    # Create a new RAG_Chain instance and store it in cache
    rag_chain = RAG_Chain(rfp_path=project_dir)
        # cache.set(cache_key, rag_chain, timeout=None)  # Cache indefinitely

    # Get the answer
    answer = rag_chain.simple_query_answering(query)
    
    return JsonResponse({"status": "success", "answer": answer})


@csrf_exempt
def get_detailed_answer(request):
    project_name = request.POST.get("project_name")
    query = request.POST.get("query")

    if not project_name or not query:
        return HttpResponseBadRequest("Missing project name or query")
    
    data_dir = "./data"
    project_dir = os.path.join(data_dir, "rfp", project_name)

    # Check if the project directory exists
    if not os.path.exists(project_dir):
        return JsonResponse({"status": "error", "message": f"Project directory '{project_name}' not found."})
    
    # Create a new RAG_Chain instance and store it in cache
    rag_chain = RAG_Chain(rfp_path=project_dir)
        # cache.set(cache_key, rag_chain, timeout=None)  # Cache indefinitely

    # Get the answer
    answer = rag_chain.detailed_query_answering(query)
    
    return JsonResponse({"status": "success", "answer": answer})


@csrf_exempt
def get_detailed_answer_verbose(request):
    project_name = request.POST.get("project_name")
    query = request.POST.get("query")

    if not project_name or not query:
        return HttpResponseBadRequest("Missing project name or query")
    
    data_dir = "./data"
    project_dir = os.path.join(data_dir, "rfp", project_name)

    # Check if the project directory exists
    if not os.path.exists(project_dir):
        return JsonResponse({"status": "error", "message": f"Project directory '{project_name}' not found."})
    
    # Create a new RAG_Chain instance and store it in cache
    rag_chain = RAG_Chain(rfp_path=project_dir)
        # cache.set(cache_key, rag_chain, timeout=None)  # Cache indefinitely

    # Get the answer
    answer = rag_chain.detailed_query_answering_verbose(query)
    
    return JsonResponse({"status": "success", "answer": answer})


@csrf_exempt
def get_simple_answer_verbose(request):
    project_name = request.POST.get("project_name")
    query = request.POST.get("query")

    if not project_name or not query:
        return HttpResponseBadRequest("Missing project name or query")
    
    data_dir = "./data"
    project_dir = os.path.join(data_dir, "rfp", project_name)

    # Check if the project directory exists
    if not os.path.exists(project_dir):
        return JsonResponse({"status": "error", "message": f"Project directory '{project_name}' not found."})
    
    # Create a new RAG_Chain instance and store it in cache
    rag_chain = RAG_Chain(rfp_path=project_dir)
        # cache.set(cache_key, rag_chain, timeout=None)  # Cache indefinitely

    # Get the answer
    answer = rag_chain.simple_query_answering_verbose(query)
    
    return JsonResponse({"status": "success", "answer": answer})


from rfp_llm.models import User
@csrf_exempt
def sign_up(request):
    if request.method == 'POST':
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")

            # Validate user input
            if not username or not password or not email:
                return JsonResponse({'status': 'error', 'message': 'Username, password, and email cannot be empty'}, status=400)

            # Check if the username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=409)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already exists'}, status=409)

            # Create a new user
            user = User.objects.create(username=username, password=password, email=email)
            return JsonResponse({'status': 'success', 'message': f'User {user.username} registered successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in the request body'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)


@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Validate user input
            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password cannot be empty'}, status=400)

            # Query the user
            try:
                user = User.objects.get(username=username)
                if user.password == password:
                    return JsonResponse({'status': 'success', 'message': f'Welcome back, {user.username}!'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Incorrect password'}, status=401)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)
