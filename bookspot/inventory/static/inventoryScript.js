document.addEventListener("DOMContentLoaded", function() {
    const selectionButtons = document.querySelectorAll(".selection-button");
    const views = document.querySelectorAll(".view");
    const searchInput = document.getElementById("search-input");
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Toggle active view when selection buttons are clicked
    selectionButtons.forEach(button => {
        button.addEventListener("click", function() {
            selectionButtons.forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");
            views.forEach(view => view.classList.remove("active"));
            const viewId = this.getAttribute("data-view");
            const viewToShow = document.getElementById(viewId);
            if (viewToShow) {
                viewToShow.classList.add("active");
            }
        });
    });

    // Toggle active menu item
    const menuItems = document.querySelectorAll(".menu li");
    menuItems.forEach(item => {
        item.addEventListener("click", function() {
            menuItems.forEach(i => i.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // Show/Hide add book form
    window.mostrarFormularioAgregar = function() {
        document.getElementById("add-book-form").style.display = "block";
    };

    window.cerrarFormularioAgregar = function() {
        document.getElementById("add-book-form").style.display = "none";
    };

    window.cerrarFormularioEditar = function() {
        document.getElementById("edit-book-modal").style.display = "none";
    };

    // Handle submission of the add-book form
    document.getElementById("form-agregar-libro").addEventListener("submit", function(event) {
        event.preventDefault();
        const titulo = document.getElementById("titulo").value;
        const precio = document.getElementById("precio").value;
        // Map the input "cantidad" to the API field "cantidad_disponible"
        const cantidad_disponible = document.getElementById("cantidad").value;

        fetch("/inventory/libros/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken

            },
            credentials: 'include',
            body: JSON.stringify({ titulo, precio, cantidad_disponible })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Libro agregado exitosamente.");
                actualizarInventario();
                document.getElementById("add-book-form").style.display = "none";
                document.getElementById("form-agregar-libro").reset();
            }
        })
        .catch(error => {
            alert("Error: " + error);
        });
    });

    // Fetch and update the inventory list (optionally using the search query)
    function actualizarInventario() {
        let url = "/inventory/libros/";
        const searchTerm = searchInput.value.trim();
        if (searchTerm !== "") {
            // The API supports searching using the 'search' query parameter
            url += `?search=${encodeURIComponent(searchTerm)}`;
        }
        fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error al obtener libros: " + data.error);
                return;
            }
            const tableBody = document.getElementById("inventory-table-body");
            tableBody.innerHTML = "";

            // Assuming the API returns an array of books (adjust if using pagination)
            data.forEach(libro => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${libro.id}</td>
                    <td>${libro.titulo}</td>
                    <td>${libro.precio}</td>
                    <td>${libro.cantidad_disponible}</td>
                    <td>
                        <button class="btn edit" data-id="${libro.id}">Editar</button>
                        <button class="btn delete" data-id="${libro.id}">Eliminar</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            agregarEventosBotones();
        })
        .catch(error => {
            console.error("Error al obtener el inventario:", error);
        });
    }

    // Attach events to the edit and delete buttons for each book
    function agregarEventosBotones() {
        const editButtons = document.querySelectorAll(".btn.edit");
        const deleteButtons = document.querySelectorAll(".btn.delete");

        editButtons.forEach(button => {
            button.addEventListener("click", function() {
                const libroId = this.getAttribute("data-id");
                // Retrieve details of the specific book using its ID
                fetch(`/inventory/libros/${libroId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert("Error al obtener detalles del libro: " + data.error);
                        return;
                    }
                    abrirFormularioEditar(data);
                })
                .catch(error => {
                    alert("Error: " + error);
                });
            });
        });

        deleteButtons.forEach(button => {
            button.addEventListener("click", function() {
                const libroId = this.getAttribute("data-id");
                eliminarLibro(libroId);
            });
        });
    }

    // Open and populate the edit modal with book details
    function abrirFormularioEditar(libro) {
        const modal = document.getElementById("edit-book-modal");
        modal.style.display = "block";

        document.getElementById("edit-id").value = libro.id;
        // Update input IDs to match API field names (no accented characters)
        document.getElementById("edit-titulo").value = libro.titulo;
        document.getElementById("edit-precio").value = libro.precio;
        document.getElementById("edit-cantidad").value = libro.cantidad_disponible;

        // When the edit form is submitted, send a PUT request to update the book
        document.getElementById("form-editar-libro").addEventListener("submit", function(event) {
            event.preventDefault();

            const id = document.getElementById("edit-id").value;
            const titulo = document.getElementById("edit-titulo").value;
            const precio = document.getElementById("edit-precio").value;
            const cantidad_disponible = document.getElementById("edit-cantidad").value;

            fetch(`/inventory/libros/${id}/`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                credentials: 'include',
                body: JSON.stringify({ titulo, precio, cantidad_disponible })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("Libro editado exitosamente.");
                    actualizarInventario();
                    modal.style.display = "none";
                    document.getElementById("form-editar-libro").reset();
                }
            })
            .catch(error => {
                alert("Error: " + error);
            });
        });
    }

    // Delete a book using its ID
    function eliminarLibro(id) {
        if (confirm("¿Estás seguro de que quieres eliminar este libro?")) {
            fetch(`/inventory/libros/${id}/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    alert("Libro eliminado exitosamente.");
                    actualizarInventario();
                } else {
                    return response.json().then(data => {
                        throw new Error(data.error || "Error al eliminar libro");
                    });
                }
            })
            .catch(error => {
                alert("Error: " + error);
            });
        }
    }

    // When the search input changes, refresh the inventory list
    searchInput.addEventListener("input", function() {
        actualizarInventario();
    });

    // Initial load of inventory data
    actualizarInventario();
});
