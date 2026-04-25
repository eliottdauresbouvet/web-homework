async function loadRooms() {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        window.location.href = "/username";
        return;
    }

    // Récupérer toutes les rooms
    const allGroups = await (await fetch("/api/groups")).json();

    // Récupérer les rooms auxquelles le user est inscrit
    const userGroups = await (await fetch(`/api/groups_users/${userId}`)).json();
    const subscribedIds = userGroups.map(g => g.id);

    // Conteneur principal
    const container = document.getElementById("rooms");
    container.innerHTML = "";

    // Affichage de chaque room
    allGroups.forEach(group => {
        const div = document.createElement("div");
        div.className = "room-card";

        // Nom
        const name = document.createElement("div");
        name.className = "room-name";
        name.textContent = group.name;
        div.appendChild(name);

        // Conteneur des boutons
        const actions = document.createElement("div");
        actions.className = "room-actions";

        const isSubscribed = subscribedIds.includes(group.id);

        if (isSubscribed) {
            // UNSUBSCRIBE
            const unsubBtn = document.createElement("button");
            unsubBtn.textContent = "Unsubscribe";
            unsubBtn.className = "btn-unsub";
            unsubBtn.onclick = async () => {
                await fetch("/api/unsubscribe", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId, group_id: group.id })
                });
                loadRooms();
            };
            actions.appendChild(unsubBtn);

            // ENTER
            const enterBtn = document.createElement("button");
            enterBtn.textContent = "Entrer";
            enterBtn.className = "btn-enter";
            enterBtn.onclick = () => {
                window.location.href = `/chat/${group.id}`;
            };
            actions.appendChild(enterBtn);

        } else {
            // SUBSCRIBE
            const subBtn = document.createElement("button");
            subBtn.textContent = "Subscribe";
            subBtn.className = "btn-sub";
            subBtn.onclick = async () => {
                await fetch("/api/subscribe", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId, group_id: group.id })
                });
                loadRooms();
            };
            actions.appendChild(subBtn);
        }

        // Ajouter les boutons à la room
        div.appendChild(actions);

        // Ajouter la room à la page
        container.appendChild(div);
    });
}

loadRooms();
