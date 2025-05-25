from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.sqlite import JSON

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(15), unique=True, nullable=True)
    #ip = db.Column(db.String(15), unique=True, nullable=False)
    domain = db.Column(db.String(100), unique=True, nullable=True)
    #domain = db.Column(db.String(100), unique=True, nullable=False)  # 添加域名字段
    port = db.Column(db.Integer, nullable=False)  # 新增端口字段
    user = db.Column(db.String(64), nullable=False)  # 新增用户名字段
    password = db.Column(db.String(128))  # 新增密码字段
    gpu_count = db.Column(db.Integer)
    gpu_usage = db.Column(db.Float)
    total_memory = db.Column(db.Integer)  # 新增总内存字段（单位：GB）
    memory_usage = db.Column(db.Float)    # 新增内存使用率字段
    is_occupied = db.Column(db.Boolean, default=False)
    occupied_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    occupied_by = db.relationship('User', backref='occupied_servers')
    note = db.Column(db.Text)
    release_time = db.Column(db.DateTime)


class gpu_usage_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    usage = db.Column(db.Float, nullable=False)

class gpu_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    gpu_index = db.Column(db.Integer, nullable=False)
    memory_usage = db.Column(db.Float)
    memory_used = db.Column(db.Float)
    memory_total = db.Column(db.Float)
    utilization = db.Column(db.Float)
    power_draw = db.Column(db.Float)          # 当前功耗
    power_limit = db.Column(db.Float)         # 最大功耗
    power_usage = db.Column(db.Float)         # 功率使用率

    # 使用 JSON 字段存储进程信息
    processes = db.Column(JSON, nullable=True)  # 示例：[{ "pid": 123, "used_memory": 456 }, ...]

    # 添加唯一约束，确保同一服务器上 GPU 索引唯一
    __table_args__ = (db.UniqueConstraint('server_id', 'gpu_index', name='unique_gpu_per_server'),)