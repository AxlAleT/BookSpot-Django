async function logout() {
  if (confirm("¿Desea cerrar sesión?")) {
      const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        try {
            const response = await fetch('/api/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

        } catch (error) {
            console.error('Error al iniciar sesión:', error);
            alert(`Error al iniciar sesión: ${error.message}`);
        }
        window.location.href = "/";
  }
}