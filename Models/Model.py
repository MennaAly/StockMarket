from sqlalchemy import Column, Integer, String ,ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    closingPrice = Column(String(120))

    def __init__(self, name, closingPrice):
        self.name = name
        self.closingPrice = closingPrice

    def __repr__(self):
        return '<Asset %r>' % (self.name)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<Asset %r>' % (self.email)


class UserAssets(Base):
    __tablename__ = 'userAssets'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    amountOfInvestemnt = Column(String(120))
    status = Column(String(120))
    userID = Column(Integer,ForeignKey('users.id'))
    subject = Column(String(120) )
    numOfStocks = Column(String(120))

    def __init__(self, name, amountOfInvestemnt ,status ,userID , subject,numOfStocks):
        self.name = name
        self.amountOfInvestemnt = amountOfInvestemnt
        self.status = status
        self.userID = userID
        self.subject =  subject
        self.numOfStocks = numOfStocks

    def __repr__(self):
        return '<Asset %r>' % (self.name)