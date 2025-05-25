import paramiko  # 新引入一个包


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
        for line in output.strip().split("\n"):
            values = line.split(", ")
            if len(values) >= 6:  # 确保有足够的字段
                (
                    index,
                    memory_used,
                    memory_total,
                    power_draw,
                    power_limit,
                    utilization,
                ) = values[:6]
                memory_usage = (
                    (float(memory_used) / float(memory_total)) * 100
                    if float(memory_total) != 0
                    else 0
                )
                power_usage = (
                    (float(power_draw) / float(power_limit)) * 100
                    if float(power_limit) != 0
                    else 0
                )
                gpu_info.append(
                    {
                        "index": int(index),
                        "memory_used": float(memory_used),
                        "memory_total": float(memory_total),
                        "memory_usage": memory_usage,
                        "power_draw": float(power_draw),
                        "power_limit": float(power_limit),
                        "power_usage": power_usage,
                        "utilization": float(utilization),
                        "processes": [],  # 用于存储进程信息
                    }
                )

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
        for line in uuid_output.strip().split("\n"):
            index, uuid = line.split(", ")
            uuid_to_index[uuid] = int(index)

        # 解析进程信息并关联到对应的GPU
        for line in output.strip().split("\n"):
            if line.strip() != "":
                try:
                    gpu_uuid, pid, used_memory = line.split(", ")
                    if gpu_uuid in uuid_to_index:
                        gpu_index = uuid_to_index[gpu_uuid]
                        for gpu in gpu_info:
                            if gpu["index"] == gpu_index:
                                gpu["processes"].append(
                                    {
                                        "gpu_index": gpu_index,
                                        "pid": int(pid),
                                        "used_memory": float(used_memory),
                                    }
                                )
                                break
                except Exception as e:
                    print(f"Error parsing process line '{line}': {e}")

        ssh.close()

        return gpu_info

    except Exception as e:
        print(f"Error getting GPU info for {domain}: {str(e)}")
        return None


def update_server_gpu_info(server):
    if server.domain:
        print("服务器信息:", server.domain)
        gpu_info = get_gpu_info(
            domain=server.domain,
            port=server.port,
            user=server.user,
            password=server.password,
        )
    elif server.ip:
        print("服务器信息:", server.ip)
        gpu_info = get_gpu_info(
            domain=server.ip,
            port=server.port,
            user=server.user,
            password=server.password,
        )
    else:
        return None

    if gpu_info:
        server.gpu_count = len(gpu_info)
        server.gpu_usage = sum(gpu["utilization"] for gpu in gpu_info) / len(gpu_info)
        return gpu_info
    return None
