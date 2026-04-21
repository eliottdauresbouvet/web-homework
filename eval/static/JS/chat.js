// Récupère le groupId depuis une variable globale définie dans le HTML
const ws = new WebSocket(`ws://localhost:8000/ws/group/${groupId}`);

// Quand un message arrive du serveur
ws.onmessage = (event) => {
    const messagesDiv = document.getElementById("messages");
    const p = document.createElement("p");
    p.textContent = event.data;
    messagesDiv.appendChild(p);
};

// Quand on clique sur le bouton "Envoyer"
document.getElementById("sendBtn").onclick = () => {
    const input = document.getElementById("messageInput");
    ws.send(input.value);
    console.log("Message envoyé :", input.value);

    input.value = "";
};
