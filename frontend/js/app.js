document.addEventListener("DOMContentLoaded", function() {
    const tabla = document.querySelector("#tablaRestaurantes tbody");
    const paginationDiv = document.getElementById("pagination");
    const form = document.querySelector("#formRestaurante");

    const nombreInput = document.querySelector("#nombre");
    const direccionInput = document.querySelector("#direccion");
    const telefonoInput = document.querySelector("#telefono");

    const API_URL = 'http://127.0.0.1:8000/restaurantes/';
    const itemsPerPage = 10;
    let currentPage = 1;
    let dataGlobal = [];

    let editingId = null;

    // Modal
    const modal = document.getElementById("modalEditar");
    const cerrarModal = document.getElementById("cerrarModal");
    const formEditar = document.getElementById("formEditar");
    const editarNombre = document.getElementById("editarNombre");
    const editarDireccion = document.getElementById("editarDireccion");
    const editarTelefono = document.getElementById("editarTelefono");

    function renderTable(data) {
        tabla.innerHTML = "";
        if (data.length === 0) {
            tabla.innerHTML = "<tr><td colspan='4'>No hay restaurantes disponibles.</td></tr>";
            return;
        }
        data.forEach(restaurante => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${restaurante.nombre || 'Sin nombre'}</td>
                <td>${restaurante.direccion || 'Sin dirección'}</td>
                <td>${restaurante.telefono || 'Sin teléfono'}</td>
                <td>
                    <button class="editar" data-id="${restaurante._id}">Editar</button>
                    <button class="eliminar" data-id="${restaurante._id}">Eliminar</button>
                </td>
            `;
            tabla.appendChild(fila);
        });

        // Eventos de eliminar
        tabla.querySelectorAll(".eliminar").forEach(btn => {
            btn.addEventListener("click", function() {
                const id = this.dataset.id;
                if (confirm("¿Seguro que quieres eliminar este restaurante?")) {
                    fetch(API_URL + id, { method: 'DELETE' })
                    .then(response => {
                        if (!response.ok) throw new Error('Error al eliminar');
                        dataGlobal = dataGlobal.filter(r => r._id !== id);
                        showPage(currentPage);
                        updatePagination();
                    })
                    .catch(error => console.error(error));
                }
            });
        });

        // Eventos de editar
        tabla.querySelectorAll(".editar").forEach(btn => {
            btn.addEventListener("click", function() {
                const id = this.dataset.id;
                const restaurante = dataGlobal.find(r => r._id === id);
                if (restaurante) {
                    editarNombre.value = restaurante.nombre;
                    editarDireccion.value = restaurante.direccion;
                    editarTelefono.value = restaurante.telefono;
                    editingId = id;
                    modal.style.display = "block";
                }
            });
        });
    }

    function showPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedItems = dataGlobal.slice(start, end);
        renderTable(paginatedItems);
    }

    function updatePagination() {
        paginationDiv.innerHTML = "";
        const totalPages = Math.ceil(dataGlobal.length / itemsPerPage);

        for (let i = 1; i <= totalPages; i++) {
            const button = document.createElement('button');
            button.textContent = i;
            if (i === currentPage) button.classList.add('active');

            button.addEventListener('click', function() {
                currentPage = i;
                showPage(currentPage);
                document.querySelectorAll('.pagination button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
            paginationDiv.appendChild(button);
        }
    }

    function fetchRestaurantes() {
        fetch(API_URL)
            .then(response => {
                if (!response.ok) {
                    throw new Error('No se pudo obtener la lista de restaurantes');
                }
                return response.json();
            })
            .then(data => {
                dataGlobal = data;
                showPage(currentPage);
                updatePagination();
            })
            .catch(error => {
                console.error('Error:', error);
                tabla.innerHTML = "<tr><td colspan='4'>Error cargando los datos.</td></tr>";
            });
    }

    // Evento para agregar restaurante
    form.addEventListener("submit", function(e) {
        e.preventDefault();
        const nombre = nombreInput.value;
        const direccion = direccionInput.value;
        const telefono = telefonoInput.value;

        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, direccion, telefono })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al crear restaurante');
            return response.json();
        })
        .then(data => {
            console.log("Restaurante agregado:", data);
            form.reset();
            fetchRestaurantes();
        })
        .catch(error => console.error("Error:", error));
    });

    // Subir cambios desde el popup
    formEditar.addEventListener("submit", function(e) {
        e.preventDefault();
        const nombre = editarNombre.value;
        const direccion = editarDireccion.value;
        const telefono = editarTelefono.value;

        if (editingId) {
            fetch(API_URL + editingId, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, direccion, telefono })
            })
            .then(response => {
                if (!response.ok) throw new Error('Error al actualizar');
                return response.json();
            })
            .then(data => {
                console.log("Restaurante actualizado:", data);
                modal.style.display = "none";
                editingId = null;
                fetchRestaurantes();
            })
            .catch(error => console.error("Error:", error));
        }
    });

    cerrarModal.addEventListener("click", function() {
        modal.style.display = "none";
    });

    // Cargar al inicio
    fetchRestaurantes();
});
