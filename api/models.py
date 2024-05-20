# Creación del modelo de la base de datos
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, index=True)
    employees = relationship("Employee", back_populates="department")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    job = Column(String, index=True)
    employees = relationship("Employee", back_populates="job")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    datetime = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))

    department = relationship("Department", back_populates="employees")
    job = relationship("Job", back_populates="employees")