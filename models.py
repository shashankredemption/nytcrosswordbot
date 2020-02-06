from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):  
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    win_count = Column(Integer)
    loss_count = Column(Integer)
    dnf_count = Column(Integer)
    stupid_alex_count = Column(Integer)
    top_apache_count = Column(Integer)
    # counts how many times someone didn't participate
    lame_count = Column(Integer, default=0)
