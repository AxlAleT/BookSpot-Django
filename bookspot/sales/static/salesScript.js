document.addEventListener('DOMContentLoaded', () => {
    let cart = []; // Almacena los items {id, titulo, precio, cantidad}
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function calcularTotal() {
    return cart.reduce((total, item) => {
        return total + (item.precio * item.cantidad);
    }, 0);
    }

    // Configurar eventos
    document.querySelector('#product-code + button').addEventListener('click', agregarProducto);
    document.querySelector('#complete-sale').addEventListener('click', completarVenta);

    // Delegación de eventos para inputs y botones dinámicos
    document.querySelector('#product-table-body').addEventListener('input', (e) => {
        if(e.target.classList.contains('quantity-input')) {
            const libroId = parseInt(e.target.closest('tr').dataset.libroId);
            const nuevaCantidad = parseInt(e.target.value);
            actualizarCantidad(libroId, nuevaCantidad);
            const total = calcularTotal();
            document.querySelector('.total-amount').textContent = `$${total.toFixed(2)}`;
        }
    });

    document.querySelector('#product-table-body').addEventListener('click', (e) => {
        if(e.target.closest('.btn-danger')) {
            const libroId = parseInt(e.target.closest('tr').dataset.libroId);
            eliminarProducto(libroId);
        }
    });

    async function agregarProducto() {
        const codeInput = document.getElementById('product-code');
        const libroId = codeInput.value.trim();

        if(!libroId) return;

        try {
            const response = await fetch(`api/buscar-libro/${libroId}/`);
            if(!response.ok) throw new Error('Libro no encontrado');

            const libro = await response.json();

            // Verificar si ya está en el carrito
            const existente = cart.find(item => item.id === libro.id);
            if(existente) {
                existente.cantidad++;
            } else {
                cart.push({
                    id: libro.id,
                    titulo: libro.titulo,
                    precio: libro.precio,
                    cantidad: 1,
                    stock: libro.stock
                });
            }

            renderizarTabla();
            codeInput.value = '';
        } catch (error) {
            alert(error.message);
        }
    }

    function actualizarCantidad(libroId, nuevaCantidad) {
        const item = cart.find(item => item.id === libroId);
        if(item) {
            if(nuevaCantidad < 1) nuevaCantidad = 1;
            if(nuevaCantidad > item.stock) {
                alert('No hay suficiente stock');
                nuevaCantidad = item.stock;
            }
            item.cantidad = nuevaCantidad;
            renderizarTabla();
        }
    }

    function eliminarProducto(libroId) {
        cart = cart.filter(item => item.id !== libroId);
        renderizarTabla();
    }

    function renderizarTabla() {
        const tbody = document.getElementById('product-table-body');
        tbody.innerHTML = '';

        cart.forEach(item => {
            const row = document.createElement('tr');
            row.dataset.libroId = item.id;
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.titulo}</td>
                <td>$${item.precio.toFixed(2)}</td>
                <td>
                    <input type="number" class="quantity-input" 
                           value="${item.cantidad}" min="1" max="${item.stock}"
                           style="width: 60px; text-align: center;">
                </td>
                <td>
                    <button class="btn btn-danger btn-sm">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        const total = calcularTotal();
        document.querySelector('.total-amount').textContent = `$${total.toFixed(2)}`;
    }

    async function completarVenta() {
        if(cart.length === 0) {
            alert('Agrega productos a la venta');
            return;
        }

        const metodoPago = document.getElementById('payment-method').value;
        const items = cart.map(item => ({
            libro_id: item.id,
            cantidad: item.cantidad
        }));

        try {
            const response = await fetch('api/crear-venta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    metodo_pago: metodoPago,
                    items: items
                })
            });

            const data = await response.json();

            if(!response.ok) throw new Error(data.error || 'Error en la venta');

            // Resetear carrito si fue exitoso
            cart = [];
            renderizarTabla();
            alert('Venta completada exitosamente!');

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
});