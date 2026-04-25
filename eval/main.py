from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from fastapi import FastAPI, Depends
from typing import Annotated
from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# =============================================
# CONFIGURATION DE LA BASE DE DONNÉES
# =============================================

# L'adresse du fichier de base de données SQLite (un simple fichier local)
DATABASE_URL = "sqlite:///database.db"

# On crée le "moteur" qui va gérer la connexion à la base de données
engine = create_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Au démarrage de l'application : on crée les tables si elles n'existent pas encore
    SQLModel.metadata.create_all(engine)
    yield
    # À l'arrêt de l'application : rien à faire pour l'instant

# Fonction qui ouvre une session (connexion) vers la base de données
def get_session():
    with Session(engine) as session:
        yield session

# Raccourci pour injecter automatiquement la session dans les routes
SessionDep = Annotated[Session, Depends(get_session)]


# =============================================
# MODÈLES (= les tables de la base de données)
# =============================================

# Table de liaison entre un utilisateur et un groupe (pour l'inscription)
class Enrollment(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    group_id: int = Field(foreign_key="group.id", primary_key=True)

# Modèle utilisé uniquement pour créer un utilisateur (sans l'id)
class UserCreate(SQLModel):
    name: str

# Table "user" : représente un utilisateur
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Un utilisateur peut appartenir à plusieurs groupes
    groups: list["Group"] = Relationship(back_populates="users", link_model=Enrollment)
    # Un utilisateur peut envoyer plusieurs messages
    messages: list["Message"] = Relationship(back_populates="user")

# Modèle utilisé uniquement pour créer un groupe (sans l'id)
class GroupCreate(SQLModel):
    name: str

# Table "group" : représente un salon de discussion
class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Un groupe contient plusieurs utilisateurs
    users: list["User"] = Relationship(back_populates="groups", link_model=Enrollment)
    # Un groupe contient plusieurs messages
    messages: list["Message"] = Relationship(back_populates="group")

# Table "message" : représente un message envoyé dans un groupe
class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str         # Le texte du message
    user_id: int = Field(foreign_key="user.id")   # Qui l'a envoyé
    group_id: int = Field(foreign_key="group.id") # Dans quel groupe

    user: "User" = Relationship()
    group: "Group" = Relationship()

# Modèle pour créer un message via l'API
class MessageCreate(SQLModel):
    content: str
    user_id: int
    group_id: int


# =============================================
# CRÉATION DE L'APPLICATION FASTAPI
# =============================================

app = FastAPI(lifespan=lifespan)


# =============================================
# ROUTES API 
# =============================================

# Page d'accueil basique, juste pour tester
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Créer un nouvel utilisateur
@app.post("/api/users/")
async def create_users(user: UserCreate, session: SessionDep):
    db_user = User(name=user.name)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Créer un nouveau groupe (salon de discussion)
@app.post("/api/groups/")
async def create_groups(group: GroupCreate, session: SessionDep):
    db_group = Group(name=group.name)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group

# Créer un message (route générique, sans vérification d'appartenance au groupe)
@app.post("/api/messages/")
async def create_messages(message: MessageCreate, session: SessionDep):
    db_message = Message(content=message.content, user_id=message.user_id, group_id=message.group_id)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message

# Récupérer la liste de tous les utilisateurs
@app.get("/api/users")
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return [{"id": user.id, "name": user.name} for user in users]

# Récupérer la liste de tous les groupes
@app.get("/api/groups")
def get_groups(session: SessionDep):
    groups = session.exec(select(Group)).all()
    return [{"id": group.id, "name": group.name} for group in groups]


# =============================================
# INSCRIPTION / DÉSINSCRIPTION À UN GROUPE
# =============================================

class EnrollmentCreate(SQLModel):
    user_id: int
    group_id: int

# Inscrire un utilisateur dans un groupe
@app.post("/api/subscribe")
def subscribe(enrollment: EnrollmentCreate, session: SessionDep):
    # On vérifie que l'utilisateur et le groupe existent, et que l'inscription n'existe pas déjà
    if (
        session.get(User, enrollment.user_id) is not None
        and session.get(Group, enrollment.group_id) is not None
        and session.get(Enrollment, (enrollment.user_id, enrollment.group_id)) is None
    ):
        db_enrollment = Enrollment(user_id=enrollment.user_id, group_id=enrollment.group_id)
        session.add(db_enrollment)
        session.commit()
        return {"message": "L'utilisateur a été inscrit au groupe avec succès"}
    else:
        return {"message": "L'utilisateur ou le groupe n'existe pas, ou l'utilisateur est déjà inscrit au groupe"}

# Désinscrire un utilisateur d'un groupe
@app.post("/api/unsubscribe")
def unsubscribe(enrollment: EnrollmentCreate, session: SessionDep):
    db_enrollment = session.get(Enrollment, (enrollment.user_id, enrollment.group_id))
    db_user = session.get(User, enrollment.user_id)
    db_group = session.get(Group, enrollment.group_id)
    if db_user is not None and db_group is not None and db_enrollment is not None:
        session.delete(db_enrollment)
        session.commit()
        return {"message": "L'utilisateur a été désinscrit du groupe avec succès"}
    else:
        return {"message": "L'utilisateur ou le groupe n'existe pas, ou l'utilisateur n'est pas inscrit au groupe"}

# Récupérer tous les groupes auxquels appartient un utilisateur
@app.get("/api/groups_users/{user_id}")
def get_groups_users(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if user is not None:
        return [{"id": group.id, "name": group.name} for group in user.groups]
    else:
        return {"message": "L'utilisateur n'existe pas"}


# =============================================
# MESSAGES DANS UN GROUPE
# =============================================

# Envoyer un message dans un groupe (avec vérification que l'utilisateur en est membre)
@app.post("/api/messages/group/{group_id}")
def create_message_group(group_id: int, message: MessageCreate, session: SessionDep):
    db_group = session.get(Group, group_id)
    db_user = session.get(User, message.user_id)
    if db_group is not None and db_user is not None and db_user in db_group.users:
        db_message = Message(content=message.content, user_id=message.user_id, group_id=group_id)
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return db_message
    else:
        return {"message": "Le groupe ou l'utilisateur n'existe pas, ou l'utilisateur n'est pas inscrit au groupe"}

# Récupérer tous les messages d'un groupe
@app.get("/api/messages/group/{group_id}")
def get_messages_group(group_id: int, session: SessionDep):
    db_group = session.get(Group, group_id)
    if db_group is not None:
        return [
            {"id": message.id, "content": message.content, "user_id": message.user_id}
            for message in db_group.messages
        ]
    else:
        return {"message": "Le groupe n'existe pas"}


# =============================================
# INTERFACE WEB (pages HTML)
# =============================================

# On configure le moteur de templates HTML (fichiers .html.j2)
templates = Jinja2Templates(directory="templates")

# On sert les fichiers statiques (CSS, JS, images...) depuis le dossier /static
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================================
# WEBSOCKET — CHAT EN TEMPS RÉEL
# =============================================

# Dictionnaire qui stocke les connexions actives, par groupe
connections : dict[int, list[WebSocket]] = {}

# Point de connexion WebSocket pour un groupe donné
@app.websocket("/ws/group/{group_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: int):
    await websocket.accept()  # On accepte la connexion

    # On ajoute ce client à la liste des connectés de ce groupe
    connections.setdefault(group_id, []).append(websocket)

    try:
        while True:
            # On attend un message de ce client
            data = await websocket.receive_text()
            print("Message reçu :", data)

            # On retransmet le message à TOUS les clients du même groupe
            for connection in connections[group_id]:
                await connection.send_text(data)

    except WebSocketDisconnect:
        # Si le client se déconnecte, on le retire de la liste
        connections[group_id].remove(websocket)


# =============================================
# PAGES WEB
# =============================================

# Page de chat pour un groupe spécifique
@app.get("/chat/{group_id}")
def get_chat(request: Request, group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    return templates.TemplateResponse("chat.html.j2", {
        "request": request,
        "group_id": group_id,
        "group_name": group.name
    })

# Page listant tous les salons disponibles
@app.get("/rooms")
def rooms_page(request: Request):
    return templates.TemplateResponse("rooms.html.j2", {"request": request})

# Page pour choisir son pseudo
@app.get("/username")
def username_page(request: Request):
    return templates.TemplateResponse("username.html.j2", {"request": request})