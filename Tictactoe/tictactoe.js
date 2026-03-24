document.addEventListener("DOMContentLoaded", () => {

    const colors = ["red", "green"];
    let currentColorIndex = 0;
    const cells = document.querySelectorAll(".cell");
    cells.forEach(cell => {
        cell.addEventListener("click", () => {
            if (!cell.classList.contains("clicked")) {
                cell.classList.add("clicked");
                cell.style.backgroundColor = colors[currentColorIndex];
                cell.classList.add(colors[currentColorIndex]);
                currentColorIndex = (currentColorIndex + 1) % colors.length;
                checkWin(cells)
                
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
            cell.classList.remove("green");
            cell.classList.remove("red");
            cell.style.backgroundColor = "";
        })
    });
});


            

function inclus(a,b) {
    return a.every(x=>b.includes(x));
}

function listContainsClass(cells, className) {
    const list = [];
    cells.forEach((cell, index) => {
        if (cell.classList.contains(className)) {
            list.push(index);
        }
    })
    return list;
}

function checkWin(cells) {
    const Combinations = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]];
            Combinations.forEach(combination => {
                if (inclus(combination, listContainsClass(cells, "red") )) { 
                    console.log("Red wins !");
            
                };
                if (inclus(combination, listContainsClass(cells, "green") )) { 
                    console.log("Green wins !");
                };
            });

}