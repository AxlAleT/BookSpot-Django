document.addEventListener('DOMContentLoaded', () => {
    const productTableBody = document.getElementById('product-table-body');
    const completeSaleButton = document.getElementById('complete-sale');
    const productCodeInput = document.getElementById('product-code');
    const paymentMethodSelect = document.getElementById('payment-method');

    let products = [];

    function renderProducts() {
        productTableBody.innerHTML = '';
        products.forEach((product, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.titulo}</td>
                <td>${product.id_libro}</td>
                <td>${product.precio.toFixed(2)}</td>
                <td><input type="number" value="${product.cantidad}" min="1" class="form-control quantity-input" data-index="${index}"></td>
                <td>
                    <button class="btn btn-danger btn-sm delete-button" data-index="${index}">Eliminar</button>
                </td>
            `;
            productTableBody.appendChild(row);
        });
    }

    async function fetchProductData(id_libro, cantidad) {
        try {
            const response = await fetch('http://127.0.0.1:5000/ventas/get_libro/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ items: [{ id_libro, cantidad }], metodo_pago: paymentMethodSelect.value})
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error: ${response.status} ${response.statusText}. ${errorText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching product data:', error);
            throw error;
        }
    }

    productCodeInput.addEventListener('keypress', async (event) => {
        if (event.key === 'Enter') {
            const id_libro = parseInt(productCodeInput.value);
            const cantidad = 1; // Default quantity for a new product

            try {
                const productData = await fetchProductData(id_libro, cantidad);
                if (productData) {
                    products.push({ ...productData, cantidad });
                    renderProducts();
                    productCodeInput.value = ''; // Clear the input
                } else {
                    alert('Producto no encontrado o no hay suficiente stock');
                }
            } catch (error) {
                alert(`Error al obtener datos del producto: ${error.message}`);
            }
        }
    });

    productTableBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-button')) {
            const index = event.target.getAttribute('data-index');
            products.splice(index, 1);
            renderProducts();
        }
    });

    productTableBody.addEventListener('input', async (event) => {
        if (event.target.classList.contains('quantity-input')) {
            const index = parseInt(event.target.getAttribute('data-index'));
            const newQuantity = parseInt(event.target.value);
            const id_libro = products[index].id_libro;

            if (newQuantity > 0) {
                try {
                    await fetchProductData(id_libro, newQuantity);
                    products[index].cantidad = newQuantity;
                } catch (error) {
                    console.error('Error fetching product data:', error);
                    alert(`Error al actualizar la cantidad: ${error.message}`);
                    event.target.value = products[index].cantidad;
                }
            } else {
                event.target.value = products[index].cantidad;
            }
        }
    });

    completeSaleButton.addEventListener('click', async () => {
        try {
            const items = products.map(product => ({
                id_libro: product.id_libro,
                cantidad: product.cantidad
            }));
            const metodo_pago = paymentMethodSelect.value;

            const response = await fetch('http://127.0.0.1:5000/ventas/completar/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ items, metodo_pago })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error: ${response.status} ${response.statusText}. ${errorText}`);
            }

            products.length = 0;
            renderProducts();
            alert('Venta completada exitosamente!');
        } catch (error) {
            console.error('Error al completar la venta:', error);
            alert(`Error al completar la venta: ${error.message}`);
        }
    });

    renderProducts();
});
