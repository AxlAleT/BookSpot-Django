document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.login-form');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Collect form data
        const correoElectronico = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            // Send data to the server
            const response = await fetch('/api/login/', {  // Updated endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ correo_electronico: correoElectronico, password: password })
            });

            if (response.ok) {
                const data = await response.json(); // Parse the JSON response
                let redirectTo = ''; // Initialize the redirect variable

                // Determine the redirect based on the grupo name
                switch (data.usuario.grupo) {  // Use grupo name instead of id_grupo
                    case 'admin':
                        redirectTo = '/admin/dashboard/';  // Updated redirect URL
                        break;
                    case 'vendedor':
                        redirectTo = '/ventas/dashboard/';  // Updated redirect URL
                        break;
                    case 'almacenista':
                        redirectTo = '/almacen/dashboard/';  // Updated redirect URL
                        break;
                    default:
                        console.error('Grupo de usuario no reconocido:', data.usuario.grupo);
                        throw new Error('Grupo de usuario no reconocido');
                }

                // Redirect the user to the appropriate page
                window.location.href = redirectTo;
            } else {
                // Handle errors
                if (response.headers.get("content-length") !== "0") {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al iniciar sesión');
                } else {
                    throw new Error('Error al iniciar sesión sin mensaje de error específico');
                }
            }
        } catch (error) {
            console.error('Error al iniciar sesión:', error);
            alert(`Error al iniciar sesión: ${error.message}`);
        }
    });
});