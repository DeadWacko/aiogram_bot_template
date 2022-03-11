from sqlalchemy import Column, String, ForeignKey, Table, BIGINT
from sqlalchemy.orm import relationship

from .base import Base


student_group = Table(
    "student_group", Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(BIGINT, primary_key=True)

    teacher_id = Column(BIGINT, ForeignKey("teachers.id"))
    student_id = Column(BIGINT, ForeignKey("students.id"))

    teacher = relationship("Teacher", back_populates="tg_user")
    student = relationship("Student", back_populates="tg_user")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(BIGINT, primary_key=True)

    groups = relationship("Group", back_populates="teacher")
    tg_user = relationship("User", back_populates="teacher")
    name = Column(String)


class Group(Base):
    __tablename__ = "groups"

    id = Column(BIGINT, primary_key=True)

    teacher_id = Column(BIGINT, ForeignKey("teachers.id"))
    group_name = Column(String)
    students = relationship("Student", secondary=student_group, back_populates="groups")
    teacher = relationship("Teacher", back_populates="groups")


class Student(Base):
    __tablename__ = "students"

    id = Column(BIGINT, primary_key=True)

    name = Column(String)
    groups = relationship("Group", secondary=student_group, back_populates="students")
    tg_user = relationship("User", back_populates="student")
