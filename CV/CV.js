document.addEventListener("DOMContentLoaded", () => {
    const img = document.getElementById("photo");
    img.addEventListener("mouseenter", () => {
        img.classList.add("grand");
    });
    img.addEventListener("mouseleave", () => {
        img.classList.remove("grand");
    });
});