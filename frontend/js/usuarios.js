document.addEventListener("DOMContentLoaded", () => {
    // Referencias al DOM
    const tabla         = document.querySelector("#tablaUsuarios tbody");
    const paginationDiv = document.getElementById("pagination");
    const formCrear     = document.getElementById("formUsuario");
    const formEditar    = document.getElementById("formEditar");
    const modal         = document.getElementById("modalEditar");
    const cerrarModal   = document.getElementById("cerrarModal");
  
    const nombreInput     = document.getElementById("nombre");
    const emailInput      = document.getElementById("email");
    const contraInput     = document.getElementById("contrasena");
    const direccionInput  = document.getElementById("direccion");
    const telefonoInput   = document.getElementById("telefono");
  
    const editarNombreInput    = document.getElementById("editarNombre");
    const editarEmailInput     = document.getElementById("editarEmail");
    const editarContraInput    = document.getElementById("editarContrasena");
    const editarDireccionInput = document.getElementById("editarDireccion");
    const editarTelefonoInput  = document.getElementById("editarTelefono");
  
    const filtroNombre = document.getElementById("filtroNombre");
    const filtroEmail  = document.getElementById("filtroEmail");
  
    // Estado
    const API_URL      = "http://127.0.0.1:8000/usuarios/";
    const itemsPerPage = 10;
    let currentPage    = 1;
    let dataGlobal     = [];
    let editingId      = null;
  
    // Listeners
    filtroNombre?.addEventListener("input", aplicarFiltros);
    filtroEmail?.addEventListener("input", aplicarFiltros);
    cerrarModal?.addEventListener("click", () => {
      modal.style.display = "none";
      editingId = null;
    });
    formCrear?.addEventListener("submit", crearUsuario);
    formEditar?.addEventListener("submit", guardarEdicion);
  
    // --- Funciones ---
    async function fetchUsuarios() {
      try {
        const res = await fetch(API_URL);
        dataGlobal = await res.json();
        actualizarPaginacion();
        mostrarPagina(currentPage);
      } catch {
        tabla.innerHTML = `<tr><td colspan="5">Error cargando usuarios.</td></tr>`;
      }
    }
  
    async function crearUsuario(e) {
      e.preventDefault();
      // <-- Aquí el cambio: usamos "contraseña" con tilde
      const payload = {
        nombre:      nombreInput.value,
        email:       emailInput.value,
        "contraseña": contraInput.value,
        direccion:   direccionInput.value,
        telefono:    telefonoInput.value
      };
  
      const res = await fetch(API_URL, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      const body = await res.json();
      if (!res.ok) {
        alert("Error al crear usuario:\n" +
          (body.detail 
            ? JSON.stringify(body.detail, null, 2) 
            : JSON.stringify(body)));
        return;
      }
      formCrear.reset();
      currentPage = 1;
      await fetchUsuarios();
    }
  
    async function guardarEdicion(e) {
      e.preventDefault();
      if (!editingId) return;
      const payload = {
        nombre:      editarNombreInput.value,
        email:       editarEmailInput.value,
        "contraseña": editarContraInput.value || undefined,
        direccion:   editarDireccionInput.value,
        telefono:    editarTelefonoInput.value
      };
      const res = await fetch(API_URL + editingId, {
        method:  "PUT",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        alert("Error al editar usuario");
        return;
      }
      modal.style.display = "none";
      await fetchUsuarios();
    }
  
    function aplicarFiltros() {
      const n = filtroNombre.value.toLowerCase();
      const e = filtroEmail.value.toLowerCase();
      Array.from(tabla.rows).forEach(fila => {
        const nombre = fila.cells[0]?.textContent.toLowerCase() || "";
        const email  = fila.cells[1]?.textContent.toLowerCase() || "";
        fila.style.display = (nombre.includes(n) && email.includes(e)) ? "" : "none";
      });
    }
  
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="5">No hay usuarios.</td></tr>`;
        return;
      }
      arr.forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${u.nombre}</td>
          <td>${u.email}</td>
          <td>${u.direccion}</td>
          <td>${u.telefono}</td>
          <td>
            <button class="editar btn btn-sm btn-outline-primary" data-id="${u._id}">Editar</button>
            <button class="eliminar btn btn-sm btn-outline-danger"  data-id="${u._id}">Eliminar</button>
          </td>
        `;
        tabla.appendChild(tr);
      });
  
      // Borrar
      tabla.querySelectorAll(".eliminar").forEach(btn =>
        btn.addEventListener("click", async () => {
          if (!confirm("¿Eliminar este usuario?")) return;
          await fetch(API_URL + btn.dataset.id, { method: "DELETE" });
          dataGlobal = dataGlobal.filter(x => x._id !== btn.dataset.id);
          actualizarPaginacion();
          mostrarPagina(currentPage);
        })
      );
  
      // Editar
      tabla.querySelectorAll(".editar").forEach(btn =>
        btn.addEventListener("click", () => {
          editingId = btn.dataset.id;
          const u = dataGlobal.find(x => x._id === editingId);
          if (!u) return;
          editarNombreInput.value    = u.nombre;
          editarEmailInput.value     = u.email;
          editarContraInput.value    = "";
          editarDireccionInput.value = u.direccion;
          editarTelefonoInput.value  = u.telefono;
          modal.style.display        = "block";
        })
      );
    }
  
    function mostrarPagina(p) {
      const start = (p - 1) * itemsPerPage;
      renderTable(dataGlobal.slice(start, start + itemsPerPage));
    }
  
    function actualizarPaginacion() {
      paginationDiv.innerHTML = "";
      const total = Math.ceil(dataGlobal.length / itemsPerPage) || 1;
      for (let i = 1; i <= total; i++) {
        const btn = document.createElement("button");
        btn.textContent = i;
        btn.className = "btn btn-outline-secondary me-1" + (i === currentPage ? " active" : "");
        btn.addEventListener("click", () => {
          currentPage = i;
          mostrarPagina(i);
          document.querySelectorAll("#pagination button").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
        });
        paginationDiv.appendChild(btn);
      }
    }
  
    // Carga inicial
    fetchUsuarios();
  });
  