document.addEventListener("DOMContentLoaded", () => {
    // Referencias
    const tabla        = document.querySelector("#tablaOrdenes tbody");
    const pagination   = document.getElementById("pagination");
    const formCrear    = document.getElementById("formOrden");
    const formEditar   = document.getElementById("formEditar");
    const modal        = document.getElementById("modalEditar");
    const cerrarModal  = document.getElementById("cerrarModal");
  
    const usuarioInput      = document.getElementById("usuarioId");
    const restauranteInput  = document.getElementById("restauranteId");
    const fechaInput        = document.getElementById("fecha");
    const estadoInput       = document.getElementById("estado");
    const totalInput        = document.getElementById("total");
    const pagoInput         = document.getElementById("metodoPago");
    const articulosInput    = document.getElementById("articulos");
  
    const filtroUsuario = document.getElementById("filtroUsuario");
    const filtroEstado  = document.getElementById("filtroEstado");
  
    const editarEstadoInput    = document.getElementById("editarEstado");
    const editarPagoInput      = document.getElementById("editarMetodoPago");
    const editarArticulosInput = document.getElementById("editarArticulos");
  
    // Estado
    const API = "http://127.0.0.1:8000/ordenes/";
    const perPage = 10;
    let data       = [];
    let page       = 1;
    let editingId  = null;
  
    // Listeners
    formCrear?.addEventListener("submit", crearOrden);
    formEditar?.addEventListener("submit", guardarEdicion);
    cerrarModal?.addEventListener("click", () => modal.style.display = "none");
    filtroUsuario?.addEventListener("input", aplicarFiltros);
    filtroEstado?.addEventListener("input", aplicarFiltros);
  
    // Funciones
    async function fetchOrdenes() {
      try {
        const res = await fetch(API);
        data = await res.json();
        actualizarPaginacion();
        mostrarPagina(page);
      } catch {
        tabla.innerHTML = `<tr><td colspan="7">Error cargando órdenes.</td></tr>`;
      }
    }
  
    async function crearOrden(e) {
      e.preventDefault();
      let articulos;
      try {
        articulos = JSON.parse(articulosInput.value || "[]");
      } catch {
        return alert("JSON inválido en artículos");
      }
      const payload = {
        usuario_id:     usuarioInput.value,
        restaurante_id: restauranteInput.value,
        fecha:          new Date(fechaInput.value).toISOString(),
        estado:         estadoInput.value,
        total:          parseFloat(totalInput.value),
        metodopago:     pagoInput.value || null,
        articulos
      };
      const res = await fetch(API, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        return alert("Error al crear:\n" + JSON.stringify(err.detail||err, null, 2));
      }
      formCrear.reset();
      page = 1;
      await fetchOrdenes();
    }
  
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="7">No hay órdenes.</td></tr>`;
        return;
      }
      arr.forEach(o => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${o.usuario_id}</td>
          <td>${o.restaurante_id}</td>
          <td>${new Date(o.fecha).toLocaleString()}</td>
          <td>${o.estado}</td>
          <td>${o.total.toFixed(2)}</td>
          <td>${o.metodopago||""}</td>
          <td>
            <button class="editar btn btn-sm btn-outline-primary" data-id="${o._id}">Editar</button>
            <button class="eliminar btn btn-sm btn-outline-danger"  data-id="${o._id}">Eliminar</button>
          </td>`;
        tabla.appendChild(tr);
      });
  
      // Borrar
      tabla.querySelectorAll(".eliminar").forEach(btn =>
        btn.addEventListener("click", async () => {
          if (!confirm("Eliminar orden?")) return;
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
          const o = data.find(x => x._id === editingId);
          if (!o) return;
          editarEstadoInput.value    = o.estado;
          editarPagoInput.value      = o.metodopago || "";
          editarArticulosInput.value = JSON.stringify(o.articulos, null, 0);
          modal.style.display        = "block";
        })
      );
    }
  
    async function guardarEdicion(e) {
      e.preventDefault();
      let articulos;
      try {
        articulos = JSON.parse(editarArticulosInput.value || "[]");
      } catch {
        return alert("JSON inválido en artículos");
      }
      const payload = {
        estado:     editarEstadoInput.value,
        metodopago: editarPagoInput.value || null,
        articulos
      };
      const res = await fetch(API + editingId, {
        method:  "PUT",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        return alert("Error al editar:\n" + JSON.stringify(err.detail||err, null,2));
      }
      modal.style.display = "none";
      await fetchOrdenes();
    }
  
    function aplicarFiltros() {
      const u = filtroUsuario.value.toLowerCase();
      const s = filtroEstado.value.toLowerCase();
      Array.from(tabla.rows).forEach(row => {
        const uu = row.cells[0].textContent.toLowerCase();
        const ss = row.cells[3].textContent.toLowerCase();
        row.style.display = uu.includes(u) && ss.includes(s) ? "" : "none";
      });
    }
  
    function mostrarPagina(n) {
      const start = (n-1)*perPage;
      renderTable(data.slice(start, start+perPage));
    }
  
    function actualizarPaginacion() {
      pagination.innerHTML = "";
      const total = Math.ceil(data.length/perPage)||1;
      for(let i=1;i<=total;i++){
        const b = document.createElement("button");
        b.textContent = i;
        b.className = "btn btn-outline-secondary me-1"+(i===page?" active":"");
        b.addEventListener("click", ()=>{
          page = i; mostrarPagina(i);
          pagination.querySelectorAll("button").forEach(x=>x.classList.remove("active"));
          b.classList.add("active");
        });
        pagination.appendChild(b);
      }
    }
  
    // Carga inicial
    fetchOrdenes();
  });
  