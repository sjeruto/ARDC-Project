from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import Session

Base = declarative_base()
engine = create_engine("sqlite:///data.db", future=True)

class LobbyistNsw(Base):
    __tablename__ = "lobbyist_nsw"
    def __init__(self, name, abn, trading_name, on_watch_list, status, details_anchor):
        self.name = name
        self.abn = abn
        self.trading_name = trading_name
        self.on_watch_list = on_watch_list
        self.status = status
        self.status_note = ""
        self.last_updated = ""

        self.details_anchor = details_anchor

        self._clients = []
        self._employees = []
        self._owners = []
    
    # ORM Database column mappings
    id = Column(Integer, primary_key=True)
    name = Column(String(1000), nullable=False)
    abn = Column(Integer, nullable=False)
    trading_name = Column(String(1000), nullable=False)
    on_watch_list = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)
    status_note = Column(String(2000), nullable=False)
    last_updated = Column(String(100), nullable=False)

    # clients = relationship("LobbyistNsw_Client", back_populates="lobbyist")
    # employees = relationship("LobbyistNsw_Employee", back_populates="lobbyist")
    # owners = relationship("LobbyistNsw_Owner", back_populates="lobbyist")

    def as_dict(self):
        return {
            "name": self.name,
            "abn": self.abn,
            "trading_name": self.trading_name ,
            "on_watch_list": self.on_watch_list ,
            "status": self.status, 
            "status_note": self.status_note,
            "last_updated": self.last_updated
        }

    @property
    def clients(self):
        return self._clients

    @clients.setter
    def clients(self, value):
        self._clients = value

    @property
    def employees(self):
        return self._employees

    @employees.setter
    def employees(self, value):
        self._employees = value
    
    @property
    def owners(self):
        return self._owners

    @owners.setter
    def owners(self, value):
        self._owners = value

class LobbyistNsw_Client(Base):
    __tablename__ = "lobbyist_nsw_client"
    def __init__(self, name, abn, active, foreign_principal, countries, date_added):
        self.name = name
        self.abn = abn
        self.active = active
        self.foreign_principal = foreign_principal
        self.countries = countries
        self.date_added = date_added

    # ORM Database column mappings
    id = Column(Integer, primary_key=True)
    lobbyist_nsw_id = Column(Integer, ForeignKey("lobbyist_nsw.id"))
    name = Column(String(1000), nullable=False)
    abn = Column(Integer, nullable=False)
    active = Column(Boolean(), nullable=False)
    foreign_principal = Column(String(10), nullable=False)
    countries = Column(String(1000), nullable=True)
    date_added = Column(String(100), nullable=False)

    # lobbyist = relationship("LobbyistNsw", back_populates="clients")

class LobbyistNsw_Employee(Base):
    __tablename__ = "lobbyist_nsw_employee"
    def __init__(self, name, position, active, date_added):
        self.name = name
        self.postion = position
        self.active = active
        self.date_added = date_added
    
    # ORM Database column mappings
    id = Column(Integer, primary_key=True)
    lobbyist_nsw_id = Column(Integer, ForeignKey("lobbyist_nsw.id"))
    postion = Column(String(1000), nullable=False)
    name = Column(String(1000), nullable=False)
    active = Column(Boolean(), nullable=False)
    date_added = Column(String(100), nullable=False)

    # lobbyist = relationship("LobbyistNsw", back_populates="employees")

class LobbyistNsw_Owner(Base):
    __tablename__ = "lobbyist_nsw_owner"
    def __init__(self, name, active, date_added):
        self.name = name
        self.active = active
        self.date_added = date_added
    
    # ORM Database column mappings
    id = Column(Integer, primary_key=True)
    lobbyist_nsw_id = Column(Integer, ForeignKey("lobbyist_nsw.id"))
    name = Column(String(1000), nullable=False)
    active = Column(Boolean(), nullable=False)

    # lobbyist = relationship("LobbyistNsw", back_populates="owners")

class LobbyistQld(Base):
    __tablename__ = "lobbyist_qld"
    def __init__(self, name, abn, trading_name, last_updated, details_anchor):
        self.name = name
        self.abn = abn
        self.trading_name = trading_name
        self.last_updated = last_updated
        self.details_anchor = details_anchor

    # ORM Database column mappings
    id = Column(Integer, primary_key=True)
    name = Column(String(1000), nullable=False)
    abn = Column(Integer, nullable=False)
    trading_name = Column(String(1000), nullable=False)
    last_updated = Column(String(100), nullable=False)

    def as_dict(self):
        return {
            "name": self.name,
            "abn": self.abn,
            "trading_name": self.trading_name ,
            "last_updated": self.last_updated
        }