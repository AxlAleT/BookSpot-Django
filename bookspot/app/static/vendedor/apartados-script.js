document.addEventListener('DOMContentLoaded', () => {
    const formSections = document.querySelectorAll('.form-section');
    const buttons = {
        'btn-crear': 'section-crear',
        'btn-concretar': 'section-concretar',
        'btn-cancelar': 'section-cancelar',
        'btn-modificar': 'section-modificar'
    };

    Object.keys(buttons).forEach(buttonId => {
        document.getElementById(buttonId).addEventListener('click', () => {
            formSections.forEach(section => section.style.display = 'none');
            document.getElementById(buttons[buttonId]).style.display = 'block';
        });
    });

    document.getElementById('form-crear-apartado').addEventListener('submit', async (event) => {
        event.preventDefault();

        const data = {
            fecha_limite: document.getElementById('fecha_limite').value,
            monto: parseFloat(document.getElementById('monto').value),
            nombre_acreedor: document.getElementById('nombre_acreedor').value,
            items: document.getElementById('items').value.split('\n').map(item => {
                const [id_libro, cantidad, precio] = item.split(',');
                return { id_libro: parseInt(id_libro), cantidad: parseInt(cantidad), precio_apartado: parseFloat(precio) };
            })
        };

        try {
            const response = await fetch('/crear_apartado/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Apartado creado exitosamente.');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    document.getElementById('form-concretar-venta').addEventListener('submit', async (event) => {
        event.preventDefault();

        const data = {
            id_apartado: parseInt(document.getElementById('id_apartado').value)
        };

        try {
            const response = await fetch('/concretar_venta_apartado/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Venta concretada exitosamente.');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    document.getElementById('form-cancelar-apartado').addEventListener('submit', async (event) => {
        event.preventDefault();

        const data = {
            id_apartado: parseInt(document.getElementById('id_apartado_cancelar').value)
        };

        try {
            const response = await fetch('/cancelar_apartado/', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Apartado cancelado exitosamente.');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    document.getElementById('form-modificar-apartado').addEventListener('submit', async (event) => {
        event.preventDefault();

        const data = {
            id_apartado: parseInt(document.getElementById('id_apartado_modificar').value),
            fecha_limite: document.getElementById('fecha_limite_modificar').value,
            monto: parseFloat(document.getElementById('monto_modificar').value),
            nombre_acreedor: document.getElementById('nombre_acreedor_modificar').value,
            detalles: document.getElementById('detalles').value.split('\n').map(item => {
                const [id_libro, cantidad, precio] = item.split(',');
                return { id_libro: parseInt(id_libro), cantidad: parseInt(cantidad), precio_apartado: parseFloat(precio) };
            })
        };

        try {
            const response = await fetch('/modificar_apartado/', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert('Apartado modificado exitosamente.');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Inicialmente mostrar solo el primer formulario
    formSections.forEach(section => section.style.display = 'none');
    document.getElementById('section-crear').style.display = 'block';
});
