document.addEventListener('DOMContentLoaded', (event) => {
    let materialASupply = [230, 270, 320, 380];
    let shift = 0;

    updateMaterialASupplyTable();

    document.getElementById('shift-right-button').addEventListener('click', () => shiftMaterialSupplyRight());
    document.getElementById('shift-left-button').addEventListener('click', () => shiftMaterialSupplyLeft());

    document.querySelectorAll('#superman-plus-fct .selectable').forEach(cell => {
        cell.addEventListener('click', function() {
            this.classList.toggle('selected');
        });
    });

    document.getElementById('create-allocation-button').addEventListener('click', function() {
        let selectedCells = document.querySelectorAll('#superman-plus-fct .selected');
        let protected = Array.from(selectedCells).map(cell => {
            let row = cell.parentElement.rowIndex;
            let col = cell.cellIndex;
            let week = document.querySelector("#superman-plus-fct th:nth-child(" + (col + 1) + ")").textContent;
            let category = cell.parentElement.children[0].textContent;
            return [week, category, parseInt(cell.textContent)];
        });

        fetch('/create-allocation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ materialAsupply: createShiftedArr(), protected: protected })
        })
        .then(response => response.text())
        .then(data => {
            document.getElementById('table-container').innerHTML = data;
        })
        .catch(error => console.error('Error:', error));
    });

    function updateMaterialASupplyTable() {
        let supplyRow = document.querySelector("#material-a-supply tr:nth-child(2)");
        Array.from(supplyRow.children).forEach((cell, index) => {
            let arr = createShiftedArr();
            cell.textContent = arr[index] || 0;
        });
    }

    function createShiftedArr() {
        let arr = [];
        for (let i = 0; i < materialASupply.length; i++) {
            if (i < shift) {
                arr[i] = 0;
            } else {
                arr[i] = materialASupply[i - shift];
            }
        }
        return arr;
    }

    function shiftMaterialSupplyRight() {
        if (shift < materialASupply.length) {
            shift++;
            updateMaterialASupplyTable();
        }
    }

    function shiftMaterialSupplyLeft() {
        if (shift > 0) {
            shift--;
            updateMaterialASupplyTable();
        }
    }

});
