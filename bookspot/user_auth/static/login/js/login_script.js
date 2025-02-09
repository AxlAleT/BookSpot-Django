document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.login-form');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(loginForm);
        const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(formData)
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();
            if (data.usuario && data.usuario.grupo) {
                const groupRoutes = {
                    'Almacenista': '/inventory/inventory.html',
                    'Vendedor': '/sales/sales.html',
                    // Add more groups here
                };

                const redirectUrl = groupRoutes[data.usuario.grupo] || '/dashboard.html'; // Default route
                window.location.href = redirectUrl;
            } else {
                throw new Error('Datos de usuario no válidos');
            }
        } catch (error) {
            console.error('Error al iniciar sesión:', error);
            alert(`Error al iniciar sesión: ${error.message}`);
        }
    });
});
