1. Description
Ce projet est une application web simple inspirée de WhatsApp.
Elle permet à des utilisateurs prédéfinis de rejoindre des salons (rooms), de s’y abonner, d’y entrer et d’échanger des messages en temps réel.

Le backend est développé avec FastAPI, la base de données utilise SQLite, et la communication temps réel se fait via WebSockets.
Le frontend est réalisé en HTML / CSS / JavaScript.

2. Fonctionnalités principales :

-Choix d’un utilisateur existant au lancement (pas d’inscription)

-Affichage de toutes les rooms disponibles

-Abonnement / désabonnement à une room

-Entrée dans une room à laquelle on est abonné

-Consultation des messages du salon

-Envoi de messages en temps réel via WebSocket

-Mise à jour automatique de la liste des messages

3. Structure du projet
Code

main.py
database.db
templates/
    username.html.j2
    rooms.html.j2
    chat.html.j2
static/
    css/
        style.css
    js/
        rooms.js
        chat.js

4. Lancement

4.1. (Optionnel) Réinitialiser la base

rm *.db

4.2. Lancer le serveur FastAPI

fastapi dev

Le serveur démarre sur :

http://localhost:8000

5. Création des utilisateurs et des rooms

Dans un autre terminal, avec httpie

Créer des utilisateurs

http POST http://localhost:8000/users name=alice
http POST http://localhost:8000/users name=bob

Créer des rooms

http POST http://localhost:8000/rooms name=social
http POST http://localhost:8000/rooms name=sports
http POST http://localhost:8000/rooms name=bde

6. Fonctionnement de l’interface

6.1. Page /username

L’utilisateur choisit un nom parmi ceux existants.
Le user_id est stocké dans localStorage.

6.2. Page /rooms

Affiche toutes les rooms :

Subscribe → s’abonner

Unsubscribe → se désabonner

Entrer → accéder au chat

Les boutons sont affichés dynamiquement selon l’état d’abonnement.

6.3. Page /chat/{room_id}

L’utilisateur peut :
-voir les messages du salon
-envoyer un message
-recevoir les messages en temps réel via WebSocket

7. API — Routes principales

Utilisateurs

POST /users — créer un utilisateur
GET /users — liste des utilisateurs

Rooms

POST /rooms — créer une room
GET /rooms — liste des rooms

Abonnements

GET /groups_users/{user_id} — rooms auxquelles un user est abonné
POST /subscribe — s’abonner
POST /unsubscribe — se désabonner

Messages

GET /messages/{room_id} — messages d’une room
WebSocket /ws/{room_id} — envoi / réception en temps réel
