document.addEventListener("DOMContentLoaded", () => {
    const colors = ["red", "green"];
    let currentColorIndex = 0;
    const cells = document.querySelectorAll(".cell");
    cells.forEach(cell => {
        cell.addEventListener("click", () => {
            if (!cell.classList.contains("clicked")) {
                cell.classList.add("clicked");
                cell.style.backgroundColor = colors[currentColorIndex];
                currentColorIndex = (currentColorIndex + 1) % colors.length;
            }
            
        });     
    });
});