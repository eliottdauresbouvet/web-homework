async function loadUsers() {
    const res = await fetch("/api/users");
    const users = await res.json();

    const select = document.getElementById("usernameSelect");
    select.innerHTML = "";

    users.forEach(user => {
        const option = document.createElement("option");
        option.value = user.id;
        option.textContent = user.name;
        select.appendChild(option);
    });
}

document.getElementById("usernameBtn").onclick = () => {
    const userId = document.getElementById("usernameSelect").value;
    if (!userId) return;

    localStorage.setItem("user_id", userId);
    window.location.href = "/rooms";
};

loadUsers();
