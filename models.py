from sqlalchemy import Column, String, Integer  
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):  
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    win_count = Column(Integer)
    loss_count = Column(Integer)
    dnf_count = Column(Integer)
    idiot_alex_count = Column(Integer)
    chink = Column(Integer)