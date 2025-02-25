from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import CONFIG


class DbStore:
    def __init__(self, db_url: str | URL):
        self.db_url = db_url
        self.engine = create_engine(
            self.db_url,
            pool_size=10,  # 设置连接池大小为10
            max_overflow=20,  # 设置允许的最大连接数（超出连接池大小时）
            pool_timeout=30,  # 设置获取连接的超时时间（秒）
            pool_recycle=3600,  # 设置连接的回收时间（秒）
            pool_pre_ping=True,  # 启用连接保活机制，自动检查连接是否有效
            echo=False,  # 当为True时，将打印所有与数据库交互的SQL语句
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_db(self):
        return self.SessionLocal()


main_db = DbStore(
    URL.create(
        "mysql",
        username=CONFIG.MYSQL.USER,
        password=CONFIG.MYSQL.PASSWORD,
        host=CONFIG.MYSQL.HOST,
        port=CONFIG.MYSQL.PORT,
        database=CONFIG.MYSQL.DATABASE,
    )
)
