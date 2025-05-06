document.addEventListener("DOMContentLoaded", () => {
    const API     = "http://127.0.0.1:8000/resenas/";
    const perPage = 10;
  
    let data = [], page = 1, editingId = null;
  
    // DOM refs
    const tabla            = document.querySelector("#tablaResenas tbody");
    const pagination       = document.getElementById("pagination");
    const formCrear        = document.getElementById("formResena");
    const formEditar       = document.getElementById("formEditar");
    const modal            = document.getElementById("modalEditar");
    const cerrarModalBtn   = document.getElementById("cerrarModal");
  
    const usuarioInput     = document.getElementById("usuarioId");
    const restauranteInput = document.getElementById("restauranteId");
    const ordenInput       = document.getElementById("ordenId");
    const calificacionInput= document.getElementById("calificacion");
    const comentarioInput  = document.getElementById("comentario");
    const fechaInput       = document.getElementById("fecha");
  
    const filtroResta      = document.getElementById("filtroRestaurante");
    const filtroCalif      = document.getElementById("filtroCalificacion");
  
    const editarCalifInput = document.getElementById("editarCalificacion");
    const editarComentario = document.getElementById("editarComentario");
    const editarFechaInput = document.getElementById("editarFecha");
  
    // Listeners
    formCrear.addEventListener("submit", crearResena);
    formEditar.addEventListener("submit", guardarEdicion);
    cerrarModalBtn.addEventListener("click", ()=> modal.style.display = "none");
    filtroResta.addEventListener("input", aplicarFiltros);
    filtroCalif.addEventListener("input", aplicarFiltros);
  
    // Fetch inicial
    fetchResenas();
  
    async function fetchResenas() {
      try {
        const res = await fetch(API);
        data = await res.json();
        actualizarPaginacion();
        mostrarPagina(page);
      } catch {
        tabla.innerHTML = `<tr><td colspan="7">Error cargando reseñas.</td></tr>`;
      }
    }
  
    async function crearResena(e) {
      e.preventDefault();
      const payload = {
        usuario_id:     usuarioInput.value,
        restaurante_id: restauranteInput.value,
        orden_id:       ordenInput.value || null,
        calificacion:   parseInt(calificacionInput.value,10),
        comentario:     comentarioInput.value,
        fecha:          new Date(fechaInput.value).toISOString()
      };
      const res = await fetch(API, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(()=>null);
        return alert("Error al crear:\n" + JSON.stringify(err?.detail||err||res.status));
      }
      formCrear.reset();
      page = 1;
      await fetchResenas();
    }
  
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="7">No hay reseñas.</td></tr>`;
        return;
      }
      arr.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${r.usuario_id}</td>
          <td>${r.restaurante_id}</td>
          <td>${r.orden_id||""}</td>
          <td>${r.calificacion}</td>
          <td>${r.comentario}</td>
          <td>${new Date(r.fecha).toLocaleDateString()}</td>
          <td>
            <button class="editar btn btn-sm btn-outline-primary" data-id="${r._id}">Editar</button>
            <button class="eliminar btn btn-sm btn-outline-danger"  data-id="${r._id}">Eliminar</button>
          </td>
        `;
        tabla.appendChild(tr);
      });
  
      // Borrar
      tabla.querySelectorAll(".eliminar").forEach(btn =>
        btn.addEventListener("click", async () => {
          if (!confirm("Eliminar reseña?")) return;
          await fetch(API + btn.dataset.id, { method: "DELETE" });
          data = data.filter(x => x._id !== btn.dataset.id);
          actualizarPaginacion();
          mostrarPagina(page);
        })
      );
  
      // Editar
      tabla.querySelectorAll(".editar").forEach(btn =>
        btn.addEventListener("click", () => {
          editingId = btn.dataset.id;
          const r = data.find(x => x._id === editingId);
          if (!r) return;
          editarCalifInput.value    = r.calificacion;
          editarComentario.value    = r.comentario;
          editarFechaInput.value    = new Date(r.fecha).toISOString().substr(0,10);
          modal.style.display        = "block";
        })
      );
    }
  
    async function guardarEdicion(e) {
        e.preventDefault();
    
        // 1) Busca la reseña completa en nuestro array para recuperar los IDs
        const original = data.find(x => x._id === editingId);
        if (!original) {
          return alert("Reseña no encontrada");
        }
    
        // 2) Construye el payload incluyendo los IDs originales
        const payload = {
          usuario_id:     original.usuario_id,
          restaurante_id: original.restaurante_id,
          // el campo orden_id es opcional, envíalo si existía
          orden_id:       original.orden_id || null,
          calificacion:   parseInt(editarCalifInput.value, 10),
          comentario:     editarComentario.value.trim(),
          fecha:          new Date(editarFechaInput.value).toISOString()
        };
    
        try {
          const res = await fetch(API + editingId, {
            method:  "PUT",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload)
          });
          if (!res.ok) {
            const err = await res.json().catch(() => null);
            return alert("Error al editar:\n" + JSON.stringify(err?.detail || err || res.status, null, 2));
          }
          modal.style.display = "none";
          await fetchResenas();
        } catch (err) {
          console.error("Excepción al editar reseña:", err);
          alert("Error de red al editar reseña:\n" + err.message);
        }
      }
    
  
    function aplicarFiltros() {
      const fR = filtroResta.value.toLowerCase();
      const fC = filtroCalif.value.toLowerCase();
      Array.from(tabla.rows).forEach(row => {
        const rId = row.cells[1].textContent.toLowerCase();
        const cal = row.cells[3].textContent.toLowerCase();
        row.style.display = rId.includes(fR) && cal.includes(fC) ? "" : "none";
      });
    }
  
    function mostrarPagina(n) {
      const start = (n-1)*perPage;
      renderTable(data.slice(start, start+perPage));
    }
  
    function actualizarPaginacion() {
      pagination.innerHTML = "";
      const total = Math.ceil(data.length/perPage)||1;
      for (let i=1; i<=total; i++) {
        const b = document.createElement("button");
        b.textContent = i;
        b.className = "btn btn-outline-secondary me-1"+(i===page?" active":"");
        b.addEventListener("click", ()=>{
          page = i;
          mostrarPagina(i);
          pagination.querySelectorAll("button").forEach(x=>x.classList.remove("active"));
          b.classList.add("active");
        });
        pagination.appendChild(b);
      }
    }
  });
  