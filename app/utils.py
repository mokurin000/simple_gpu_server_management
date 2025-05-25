import subprocess
import re
import paramiko  #新引入一个包
"""
#多连接手段的get函数
def get_gpu_info(ip=None, domain=None, port=None, user=None, password=None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if domain:
            ssh.connect(domain, port=port, username=user, password=password)
        else:
            ssh.connect(ip, port=port, username=user, password=password)

        # 获取基础GPU信息，包括功率信息
        cmd = "nvidia-smi --query-gpu=index,memory.used,memory.total,power.draw,power.limit,utilization.gpu,compute_mode --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return None

        gpu_info = []
        for line in output.strip().split('\n'):
            values = line.split(', ')
            if len(values) >= 6:  # 确保有足够的字段
                index, memory_used, memory_total, power_draw, power_limit, utilization = values[:6]
                memory_usage = (float(memory_used) / float(memory_total)) * 100 if float(memory_total) != 0 else 0
                power_usage = (float(power_draw) / float(power_limit)) * 100 if float(power_limit) != 0 else 0
                gpu_info.append({
                    'index': int(index),
                    'memory_used': float(memory_used),
                    'memory_total': float(memory_total),
                    'memory_usage': memory_usage,
                    'power_draw': float(power_draw),
                    'power_limit': float(power_limit),
                    'power_usage': power_usage,
                    'utilization': float(utilization),
                    'processes': []  # 用于存储进程信息
                })

        # 获取进程信息
        cmd = "nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return gpu_info  # 即使进程信息获取失败，至少返回GPU信息

        # 创建 GPU UUID 到索引的映射
        cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        uuid_output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return gpu_info

        uuid_to_index = {}
        for line in uuid_output.strip().split('\n'):
            index, uuid = line.split(', ')
            uuid_to_index[uuid] = int(index)

        # 解析进程信息并关联到对应的GPU
        for line in output.strip().split('\n'):
            if line.strip() != "":
                try:
                    gpu_uuid, pid, used_memory = line.split(', ')
                    if gpu_uuid in uuid_to_index:
                        gpu_index = uuid_to_index[gpu_uuid]
                        for gpu in gpu_info:
                            if gpu['index'] == gpu_index:
                                gpu['processes'].append({
                                    'gpu_index': gpu_index,
                                    'pid': int(pid),
                                    'used_memory': float(used_memory)
                                })
                                break
                except Exception as e:
                    print(f"Error parsing process line '{line}': {e}")

        ssh.close()

        return gpu_info

    except Exception as e:
        print(f"Error getting GPU info for {domain}: {str(e)}")
        return None
"""
#多参数的get函数

def get_gpu_info(domain, port, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("新服务器信息:", domain)
        ssh.connect(domain, port=port, username=user, password=password)

        # 获取基础GPU信息，包括功率信息
        cmd = "nvidia-smi --query-gpu=index,memory.used,memory.total,power.draw,power.limit,utilization.gpu,compute_mode --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return None

        gpu_info = []
        for line in output.strip().split('\n'):
            values = line.split(', ')
            if len(values) >= 6:  # 确保有足够的字段
                index, memory_used, memory_total, power_draw, power_limit, utilization = values[:6]
                memory_usage = (float(memory_used) / float(memory_total)) * 100 if float(memory_total) != 0 else 0
                power_usage = (float(power_draw) / float(power_limit)) * 100 if float(power_limit) != 0 else 0
                gpu_info.append({
                    'index': int(index),
                    'memory_used': float(memory_used),
                    'memory_total': float(memory_total),
                    'memory_usage': memory_usage,
                    'power_draw': float(power_draw),
                    'power_limit': float(power_limit),
                    'power_usage': power_usage,
                    'utilization': float(utilization),
                    'processes': []  # 用于存储进程信息
                })

        # 获取进程信息
        cmd = "nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return gpu_info  # 即使进程信息获取失败，至少返回GPU信息

        # 创建 GPU UUID 到索引的映射
        cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        uuid_output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return gpu_info

        uuid_to_index = {}
        for line in uuid_output.strip().split('\n'):
            index, uuid = line.split(', ')
            uuid_to_index[uuid] = int(index)

        # 解析进程信息并关联到对应的GPU
        for line in output.strip().split('\n'):
            if line.strip() != "":
                try:
                    gpu_uuid, pid, used_memory = line.split(', ')
                    if gpu_uuid in uuid_to_index:
                        gpu_index = uuid_to_index[gpu_uuid]
                        for gpu in gpu_info:
                            if gpu['index'] == gpu_index:
                                gpu['processes'].append({
                                    'gpu_index': gpu_index,
                                    'pid': int(pid),
                                    'used_memory': float(used_memory)
                                })
                                break
                except Exception as e:
                    print(f"Error parsing process line '{line}': {e}")

        ssh.close()

        return gpu_info

    except Exception as e:
        print(f"Error getting GPU info for {domain}: {str(e)}")
        return None

#修改后的get函数
"""
def get_gpu_info(domain, port, user, password):
    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        # 自动添加策略，保存服务器的主机名和密钥信息
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #print("新服务器 IP:", ip)
        #print("新服务器端口:", port)
        #print("新用户名:", username)
        #print("新密码:", password)
        # 连接SSH服务器
        ssh.connect(domain, port=port, username=user, password=password)  # 使用username和password连接
        # 获取服务器内存信息
        mem_cmd = "free -g | awk 'NR==2 {print $2, $3}'"  # 获取总内存和已用内存（单位：GB）
        stdin, stdout, stderr = ssh.exec_command(mem_cmd)
        mem_output = stdout.read().decode().strip()
        total_mem, used_mem = mem_output.split()
        total_mem = int(total_mem)
        used_mem = int(used_mem)
        mem_usage = (used_mem / total_mem) * 100 if total_mem != 0 else 0
        # 获取基础GPU信息
        cmd = "nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,compute_mode --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return None, None, None#由一个变为三个

        gpu_info = []
        for line in output.strip().split('\n'):
            index, memory_used, memory_total, utilization, compute_mode = line.split(', ')
            memory_usage = (float(memory_used) / float(memory_total)) * 100
            gpu_info.append({
                'index': int(index),
                'memory_usage': memory_usage,
                'utilization': float(utilization),
                'process_name': None,
                'process_id': None
            })

        # 获取进程信息
        cmd = "nvidia-smi --query-compute-apps=gpu_uuid,pid,name --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return None

        # 创建 GPU UUID 到索引的映射
        cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        uuid_output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
            return None

        uuid_to_index = {}
        for line in uuid_output.strip().split('\n'):
            index, uuid = line.split(', ')
            uuid_to_index[uuid] = int(index)

        for line in output.strip().split('\n'):
            if line:
                gpu_uuid, pid, name = line.split(', ')
                if gpu_uuid in uuid_to_index:
                    gpu_index = uuid_to_index[gpu_uuid]
                    for gpu in gpu_info:
                        if gpu['index'] == gpu_index:
                            gpu['process_name'] = name
                            gpu['process_id'] = int(pid)
                            break

        # 关闭SSH连接
        ssh.close()

        return gpu_info, total_mem, mem_usage  # 返回GPU信息、总内存、内存使用率
    except Exception as e:
        print(f"Error getting GPU info for {domain}: {str(e)}")
        #print(f"Error getting GPU info for {ip}: {str(e)}")
        return None, None, None#由一个变为三个
"""
"""
def get_gpu_info(ip,password):
    try:
        cmd = f"ssh {ip} nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,compute_mode --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        
        gpu_info = []
        for line in output.strip().split('\n'):
            index, memory_used, memory_total, utilization, compute_mode = line.split(', ')
            memory_usage = (float(memory_used) / float(memory_total)) * 100
            gpu_info.append({
                'index': int(index),
                'memory_usage': memory_usage,
                'utilization': float(utilization),
                'process_name': None,
                'process_id': None
            })
        
        # 获取进程信息
        cmd = f"ssh {ip} nvidia-smi --query-compute-apps=gpu_uuid,pid,name --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        
        # 创建 GPU UUID 到索引的映射
        uuid_to_index = {}
        cmd = f"ssh {ip} nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits"
        uuid_output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        for line in uuid_output.strip().split('\n'):
            index, uuid = line.split(', ')
            uuid_to_index[uuid] = int(index)
        
        for line in output.strip().split('\n'):
            if line:
                gpu_uuid, pid, name = line.split(', ')
                if gpu_uuid in uuid_to_index:
                    gpu_index = uuid_to_index[gpu_uuid]
                    for gpu in gpu_info:
                        if gpu['index'] == gpu_index:
                            gpu['process_name'] = name
                            gpu['process_id'] = int(pid)
                            break
        
        return gpu_info
    except Exception as e:
        print(f"Error getting GPU info for {ip}: {str(e)}")
        return None
"""


def update_server_gpu_info(server):
    if server.domain:
        print("服务器信息:", server.domain)
        gpu_info = get_gpu_info(domain=server.domain, port=server.port, user=server.user, password=server.password)
    elif server.ip:
        print("服务器信息:", server.ip)
        gpu_info = get_gpu_info(domain=server.ip, port=server.port, user=server.user, password=server.password)
    else:
        return None

    if gpu_info:
        server.gpu_count = len(gpu_info)
        server.gpu_usage = sum(gpu['utilization'] for gpu in gpu_info) / len(gpu_info)
        return gpu_info
    return None
"""       
def update_server_gpu_info(server):
    #print("服务器 IP:", server.ip)
    #print("服务器端口:", server.port)
    #print("用户名:", server.user)
    #print("密码:", server.password)
    gpu_info, total_mem, mem_usage = get_gpu_info(server.domain, server.port, server.user, server.password)
    if gpu_info:
        server.gpu_count = len(gpu_info)
        server.gpu_usage = sum(gpu['utilization'] for gpu in gpu_info) / len(gpu_info)
        return gpu_info
    return None
"""