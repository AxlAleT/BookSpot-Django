document.addEventListener("DOMContentLoaded", function() {
    const selectionButtons = document.querySelectorAll(".selection-button");
    const views = document.querySelectorAll(".view");
    const searchInput = document.getElementById("search-input");
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function toggleActiveClass(elements, activeElement) {
        elements.forEach(element => element.classList.remove("active"));
        activeElement.classList.add("active");
    }

    function toggleDisplay(element, displayStyle) {
        element.style.display = displayStyle;
    }

    // Toggle active view when selection buttons are clicked
    selectionButtons.forEach(button => {
        button.addEventListener("click", function() {
            toggleActiveClass(selectionButtons, this);
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
            toggleActiveClass(menuItems, this);
        });
    });

    // Show/Hide add book form
    window.mostrarFormularioAgregar = function() {
        toggleDisplay(document.getElementById("add-book-form"), "block");
    };

    window.cerrarFormularioAgregar = function() {
        toggleDisplay(document.getElementById("add-book-form"), "none");
    };

    window.cerrarFormularioEditar = function() {
        toggleDisplay(document.getElementById("edit-book-modal"), "none");
    };

    // Handle submission of the add-book form
    document.getElementById("form-agregar-libro").addEventListener("submit", function(event) {
        event.preventDefault();
        const titulo = document.getElementById("titulo").value;
        const precio = document.getElementById("precio").value;
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
                toggleDisplay(document.getElementById("add-book-form"), "none");
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

            data.forEach(libro => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${libro.id}</td>
                    <td>${libro.titulo}</td>
                    <td>${libro.precio}</td>
                    <td>${libro.cantidad_disponible}</td>
                    <td>
                        <div class="btn-group" role="group" aria-label="Basic example">
                            <button class="btn edit" data-id="${libro.id}">Editar</button>
                            <button class="btn delete" data-id="${libro.id}">Eliminar</button>
                        </div>
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
        toggleDisplay(modal, "block");

        document.getElementById("edit-id").value = libro.id;
        document.getElementById("edit-titulo").value = libro.titulo;
        document.getElementById("edit-precio").value = libro.precio;
        document.getElementById("edit-cantidad").value = libro.cantidad_disponible;

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
                    toggleDisplay(modal, "none");
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
    searchInput.addEventListener("input", actualizarInventario);

    // Initial load of inventory data
    actualizarInventario();
});
