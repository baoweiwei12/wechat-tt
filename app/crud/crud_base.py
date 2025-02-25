from sqlalchemy.orm import Session
from typing import Any, Generic, List, Tuple, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.sql.elements import ColumnElement

# 定义泛型类型
ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基础的 CRUD 操作类，提供通用的增删改查功能。
    支持通过 ID 查询、条件查询、创建、更新、删除以及分页查询。
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 CRUDBase 类。

        :param model: 数据库模型类（SQLAlchemy 模型）。
        """
        self.model = model

    def get(self, db: Session, model_id: int) -> ModelType | None:
        """
        根据 ID 查询单个记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param model_id: 要查询的记录的主键 ID。
        :return: 查询到的记录对象，如果未找到则返回 None。
        """
        return (
            db.query(self.model).filter(getattr(self.model, "id") == model_id).first()
        )

    def get_by_filter(
        self,
        db: Session,
        filter: ColumnElement[bool],
    ) -> ModelType | None:
        """
        根据条件查询单个记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param filter: SQLAlchemy 的过滤条件（布尔表达式）。
        :return: 查询到的记录对象，如果未找到则返回 None。
        """
        return db.query(self.model).filter(filter).first()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """
        创建一条新记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param obj_in: 包含新记录数据的 Pydantic Schema 对象。
        :return: 新创建的记录对象。
        """
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, model_id: int, obj_in: UpdateSchemaType
    ) -> ModelType | None:
        """
        更新一条记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param model_id: 要更新的记录的主键 ID。
        :param obj_in: 包含更新数据的 Pydantic Schema 对象。
        :return: 更新后的记录对象，如果未找到记录则返回 None。
        """
        db_obj = (
            db.query(self.model).filter(getattr(self.model, "id") == model_id).first()
        )
        if db_obj:
            for field, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return None

    def delete(self, db: Session, model_id: int) -> ModelType | None:
        """
        删除一条记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param model_id: 要删除的记录的主键 ID。
        :return: 被删除的记录对象，如果未找到记录则返回 None。
        """
        db_obj = (
            db.query(self.model).filter(getattr(self.model, "id") == model_id).first()
        )
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return db_obj
        return None

    def get_multi(
        self, db: Session, page: int = 1, per_page: int = 100
    ) -> Tuple[int, List[ModelType]]:
        """
        分页查询多条记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param page: 当前页码（从 1 开始）。
        :param per_page: 每页的记录数量。
        :return: 包含总数和当前页数据的元组：(total, data)。
        """
        total = db.query(self.model).count()
        data = db.query(self.model).offset((page - 1) * per_page).limit(per_page).all()
        return total, data

    def get_multi_by_filter(
        self,
        db: Session,
        filter: ColumnElement[bool],
        page: int = 1,
        per_page: int = 100,
    ) -> Tuple[int, List[ModelType]]:
        """
        根据条件分页查询多条记录。

        :param db: SQLAlchemy 的 Session 对象，用于数据库操作。
        :param filter: SQLAlchemy 的过滤条件（布尔表达式）。
        :param page: 当前页码（从 1 开始）。
        :param per_page: 每页的记录数量。
        :return: 包含总数和当前页数据的元组：(total, data)。
        """
        query = db.query(self.model).filter(filter)
        total = query.count()
        data = query.offset((page - 1) * per_page).limit(per_page).all()
        return total, data

    def list(self, db: Session):
        """
        获取所有数据
        """
        return db.query(self.model).all()

    def list_by_filter(self, db: Session, filter: Any):
        """
        根据过滤条件获取所有数据
        """
        return db.query(self.model).filter(filter).all()
