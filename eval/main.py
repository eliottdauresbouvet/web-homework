from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from fastapi import FastAPI, Depends
from typing import Annotated
from Pydantic import BaseModel


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
    return [
        {
            "id": user.id,
            "name": user.name
        }
        for user in users
    ]

@app.get("/api/groups")
def get_groups(session: SessionDep):
    groups = session.exec(select(Group)).all()
    return [
        {
            "id": group.id,
            "name": group.name
        }
        for group in groups
    ]

class EnrollmentCreate(SQLModel):
    user_id : int
    group_id : int

@app.post("/api/subscribe")
def subscribe(enrollment : EnrollmentCreate, session: SessionDep):
    if (
        not(session.get(User, enrollment.user_id) == None)
        and not(session.get(Group, enrollment.group_id) == None) 
        and (session.get(Enrollment, (enrollment.user_id, enrollment.group_id)) == None)
    ):
        db_enrollment = Enrollment(user_id=enrollment.user_id, group_id=enrollment.group_id)
        session.add(db_enrollment)
        session.commit()
        return {"message" : "L'utilisateur a été inscrit au groupe avec succès"}
    else: 
        return {"message" : "L'utilisateur ou le groupe n'existe pas, ou l'utilisateur est déjà inscrit au groupe"}

@app.post("/api/unsubscribe")
def unsubscribe(enrollment : EnrollmentCreate, session: SessionDep):
    db_enrollment = session.get(Enrollment, (enrollment.user_id, enrollment.group_id))
    db_user = session.get(User, enrollment.user_id)
    db_group = session.get(Group, enrollment.group_id)
    if (
        db_user is not None
        and db_group is not None 
        and db_enrollment is not None
    ):
        session.delete(db_enrollment)
        session.commit()
        return {"message" : "L'utilisateur a été désinscrit du groupe avec succès"}
    else: 
        return {"message" : "L'utilisateur ou le groupe n'existe pas, ou l'utilisateur n'est pas inscrit au groupe"}

@app.get("/api/groups_users/{user_id}")
def get_groups_users(user_id : int, session : SessionDep):
    user = session.get(User, user_id)
    if user is not None:
        return [
            {
                "id": group.id,
                "name": group.name
            }
            for group in user.groups
        ]
    else:
        return {"message" : "L'utilisateur n'existe pas"}

@app.post("/api/messages/group/{group_id}")
def create_message_group(group_id : int, message : MessageCreate, session : SessionDep):
    db_group = session.get(Group, group_id)
    db_user = session.get(User, message.user_id)
    if db_group is not None and db_user is not None and db_user in db_group.users:
        db_message = Message(content=message.content, user_id=message.user_id, group_id=group_id)
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return(db_message)
    else:
        return {"message" : "Le groupe ou l'utilisateur n'existe pas, ou l'utilisateur n'est pas inscrit au groupe"}

@app.get("/api/messages/group/{group_id}")
def get_messages_group(group_id : int, session : SessionDep):
    db_group = session.get(Group, group_id)
    if db_group is not None:
        return [
            {
                "id": message.id,
                "content": message.content,
                "user_id": message.user_id
            }
            for message in db_group.messages
        ]
    else:
        return {"message" : "Le groupe n'existe pas"}




         



