# utils/data_factory.py
"""用 Faker 自动生成测试数据"""
from faker import Faker

fake = Faker("zh_CN")  # 用中文数据


def generate_post():
    """生成一篇博客文章测试数据"""
    return {
        "title": fake.sentence(),
        "body": fake.paragraph(),
        "userId": fake.random_int(min=1, max=10)
    }


def generate_user():
    """生成一个用户测试数据"""
    return {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "website": fake.domain_name()
    }


def generate_comment():
    """生成评论测试数据"""
    return {
        "postId": fake.random_int(min=1, max=100),
        "name": fake.name(),
        "email": fake.email(),
        "body": fake.paragraph()
    }
