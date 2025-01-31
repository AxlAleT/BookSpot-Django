document.addEventListener("DOMContentLoaded", function() {
    const menuItems = document.querySelectorAll(".menu li");
    const sections = document.querySelectorAll(".section");
    const selectionButtons = document.querySelectorAll(".selection-button");
    const views = document.querySelectorAll(".view");
    const searchInput = document.getElementById("search-input");

    menuItems.forEach(item => {
        item.addEventListener("click", function() {
            sections.forEach(section => {
                section.classList.remove("active");
            });
            const sectionId = this.getAttribute("data-section");
            const sectionToShow = document.getElementById(sectionId);
            if (sectionToShow) {
                sectionToShow.classList.add("active");
            }
        });
    });

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

    window.mostrarFormularioAgregar = function() {
        document.getElementById("add-book-form").style.display = "block";
    }

    document.getElementById("form-agregar-libro").addEventListener("submit", function(event) {
        event.preventDefault();
        const titulo = document.getElementById("titulo").value;
        const precio = document.getElementById("precio").value;
        const cantidad = document.getElementById("cantidad").value;

        fetch("/api/inventario/agregar_libro/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ titulo, precio, cantidad })
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

    function actualizarInventario() {
        fetch("/api/inventario/obtener_libros/?numero=0")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("inventory-table-body");
            tableBody.innerHTML = "";

            data.forEach(libro => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${libro.id}</td>
                    <td>${libro.titulo}</td>
                    <td>${libro.precio}</td>
                    <td>${libro.available_quantity}</td>
                    <td>
                        <button class="btn edit" data-id="${libro.id}">Editar</button>
                        <button class="btn delete" data-id="${libro.id}">Eliminar</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            const editButtons = document.querySelectorAll(".btn.edit");
            const deleteButtons = document.querySelectorAll(".btn.delete");

            editButtons.forEach(button => {
                button.addEventListener("click", function() {
                    const libroId = this.getAttribute("data-id");
                    const libro = data.find(libro => libro.id === parseInt(libroId));
                    if (libro) {
                        abrirFormularioEditar(libro);
                    }
                });
            });

            deleteButtons.forEach(button => {
                button.addEventListener("click", function() {
                    const libroId = this.getAttribute("data-id");
                    eliminarLibro(libroId);
                });
            });
        })
        .catch(error => {
            console.error("Error al obtener el inventario:", error);
        });
    }

    function abrirFormularioEditar(libro) {
        const modal = document.getElementById("edit-book-modal");
        modal.style.display = "block";

        document.getElementById("edit-id").value = libro.id;
        document.getElementById("edit-titulo").value = libro.titulo;
        document.getElementById("edit-precio").value = libro.precio;
        document.getElementById("edit-cantidad").value = libro.available_quantity;

        document.getElementById("form-editar-libro").addEventListener("submit", function(event) {
            event.preventDefault();

            const id = document.getElementById("edit-id").value;
            const titulo = document.getElementById("edit-titulo").value;
            const precio = document.getElementById("edit-precio").value;
            const cantidad = document.getElementById("edit-cantidad").value;

            fetch(`/api/inventario/editar_libro/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ titulo, precio, available_quantity: cantidad })
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

        const closeButton = document.getElementById("close-edit-modal");
        closeButton.addEventListener("click", function() {
            modal.style.display = "none";
        });
    }

    function eliminarLibro(id) {
        if (confirm("¿Estás seguro de que quieres eliminar este libro?")) {
            fetch(`/api/inventario/eliminar_libro/${id}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("Libro eliminado exitosamente.");
                    actualizarInventario();
                }
            })
            .catch(error => {
                alert("Error: " + error);
            });
        }
    }

    // Función para crear un gráfico de ventas
    function crearGraficoVentas() {
        const ctx = document.getElementById('ventas-chart').getContext('2d');
        fetch("/api/ventas/obtener_datos/")
            .then(response => response.json())
            .then(data => {
                const labels = data.map(item => item.fecha);
                const ventas = data.map(item => item.total);

                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Ventas',
                            data: ventas,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error("Error al obtener datos de ventas:", error);
            });
    }

    // Función para crear un gráfico de movimientos
    function crearGraficoMovimientos() {
        const ctx = document.getElementById('movimientos-chart').getContext('2d');
        fetch("/api/movimientos/obtener_datos/")
            .then(response => response.json())
            .then(data => {
                const labels = data.map(item => item.fecha);
                const movimientos = data.map(item => item.total);

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Movimientos',
                            data: movimientos,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error("Error al obtener datos de movimientos:", error);
            });
    }

    // Función para agregar un nuevo rol
    document.getElementById("form-agregar-rol").addEventListener("submit", function(event) {
        event.preventDefault();

        const nombreRol = document.getElementById("nombre-rol").value;
        const permisosSeleccionados = Array.from(document.querySelectorAll('input[name="permisos[]"]:checked')).map(el => el.value);

        fetch("/api/roles/agregar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ nombre: nombreRol, permisos: permisosSeleccionados })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Rol agregado exitosamente.");
                // Limpiar el formulario
                document.getElementById("form-agregar-rol").reset();
                // Actualizar la lista de roles
                actualizarRoles();
            }
        })
        .catch(error => {
            alert("Error: " + error);
        });
    });

    // Función para obtener y mostrar la lista de roles
    function actualizarRoles() {
        fetch("/api/roles")
        .then(response => response.json())
        .then(data => {
            const rolesList = document.getElementById("roles-list");
            rolesList.innerHTML = ""; // Limpiar la lista actual

            data.forEach(rol => {
                const rolElement = document.createElement("li");
                rolElement.textContent = rol.nombre;
                rolesList.appendChild(rolElement);
            });
        })
        .catch(error => {
            console.error("Error al obtener la lista de roles:", error);
        });
    }

    // Inicializar la lista de roles al cargar la página
    actualizarRoles();

    crearGraficoVentas();
    crearGraficoMovimientos();

    searchInput.addEventListener("input", function() {
        const searchTerm = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll("#inventory-table-body tr");

        rows.forEach(row => {
            const title = row.querySelector("td:nth-child(2)").textContent.toLowerCase();
            if (title.includes(searchTerm)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });

});
