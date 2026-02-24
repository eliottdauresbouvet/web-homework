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
        cell.addEventListener("mouseover", () => {
            if (!cell.classList.contains("clicked")) {
                cell.classList.add("hovered");

            }    
        });
        cell.addEventListener("mouseout", () => {
            if (!cell.classList.contains("clicked")) {
                cell.classList.remove("hovered");

            }    
        });    
    });

    const resetButton = document.getElementById("reset");
    resetButton.addEventListener("click", () => {
        cells.forEach(cell => {
            cell.classList.remove("clicked");
            cell.classList.remove("hovered");
            cell.style.backgroundColor = "";
        })
    });

});