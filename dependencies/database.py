
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import sqlalchemy
import alembic


from typing import Optional, Dict, List, Any
import datetime


class Site2(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)	## value is generated by database
	name: Optional[str] = Field(default=None, index=True)
	description: Optional[str] = None
	img_path: Optional[str] = None
	file_path: Optional[str] = None
	last_updated: Optional[str] = datetime.datetime.utcnow()
	enabled: bool = Field(default=True, index=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)	## value is generated by database
    Username: Optional[str] = Field(default=None, index=True)
    Email: Optional[str] = Field(default=None, index=True)
    #scopes: Optional[List[str]] = Field(default=list())
    #userdata: Optional[Dict[str, str]] = Field(default=dict())
    Hashed_Password: str
    ##UserData: <Data class>
    enabled: bool = Field(default=True, index=True,description="Can be used to disable the accounts of chronically online dingi")
    
class BaseUser(SQLModel):
    Username: str = Field(index=True)
    Email: Optional[str] = Field(index=True)

class CreateUser(BaseUser):
    Password: str


class ArtPost(SQLModel, table=True):
    #async def __init__(self):
    id: Optional[int] = Field(default=None, primary_key=True)	## value is generated by database
    title: str = Field(index=True)
    author: str = Field(index=True)
    description: Optional[str] = None
    image_path: Optional[str] = None
    last_updated: Optional[str] = Field(default=datetime.datetime.utcnow(), index=True)
    enabled: Optional[bool] = Field(default=True, index=True)


class ArtPost2(SQLModel, table=True):
    #async def __init__(self):
    id: Optional[int] = Field(default=None, primary_key=True)	## value is generated by database
    title: str = Field(index=True)
    author: str = Field(index=True)
    description: Optional[str] = None
    image_path: Optional[str] = None
    last_updated: Optional[str] = Field(default=datetime.datetime.utcnow(), index=True)
    enabled: Optional[bool] = Field(default=True, index=True)

class ArtPost3(SQLModel, table=True):
    #async def __init__(self):
    id: Optional[int] = Field(default=None, primary_key=True)	## value is generated by database
    title: str = Field(index=True)
    author: str = Field(index=True)
    description: Optional[str] = None
    image_path: Optional[str] = None
    image_name: Optional[str] = Field(index=True)
    mime_type: Optional[str] = Field()
    last_updated: Optional[str] = Field(default=datetime.datetime.utcnow(), index=True)
    enabled: Optional[bool] = Field(default=True, index=True)

__table_args__ = {'extend_existing': True}

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///Data/SQL_Model/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
	SQLModel.metadata.create_all(engine)
