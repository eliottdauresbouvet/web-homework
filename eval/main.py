from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from fastapi import FastAPI, Depends
from typing import Annotated


DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic comes here
    # Create the database and tables if they don't exist
    SQLModel.metadata.create_all(engine)

    yield
    # shutdown logic comes here
    # none so far

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class Enrollment(SQLModel, table = True):
    user_id : int = Field(foreign_key="user.id", primary_key = True)
    group_id : int = Field(foreign_key="group.id", primary_key = True)

class UserCreate(SQLModel):
    name : str

class User(SQLModel, table = True):
    id : int | None = Field(default=None, primary_key=True)
    name : str

    groups : list["Group"] = Relationship(back_populates="users", link_model=Enrollment)
    messages: list["Message"] = Relationship(back_populates="user")

class GroupCreate(SQLModel):
    name : str

class Group(SQLModel, table = True):
    id : int | None = Field(default=None, primary_key=True)
    name : str
    users : list["User"] = Relationship(back_populates="groups", link_model=Enrollment)
    messages: list["Message"] = Relationship(back_populates="group")

class Message(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    content : str
    user_id : int = Field(foreign_key="user.id")
    group_id : int = Field(foreign_key="group.id")

    user: "User" = Relationship()
    group: "Group" = Relationship()

class MessageCreate(SQLModel):
    content : str
    user_id : int
    group_id : int


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message" : "Hello World"}

@app.post("/api/users/")
async def create_users(user : UserCreate, session : SessionDep):
    db_user = User(name=user.name)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return(db_user)

@app.post("/api/groups/")
async def create_groups(group : GroupCreate, session : SessionDep):
    db_group = Group(name=group.name)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return(db_group)

@app.post("/api/messages/")
async def create_messages(message : MessageCreate, session : SessionDep):
    db_message = Message(content=message.content, user_id=message.user_id, group_id=message.group_id)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return(db_message)


@app.get("/api/users")
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users




