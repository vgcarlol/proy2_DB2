document.addEventListener("DOMContentLoaded", () => {
    const API      = "http://127.0.0.1:8000/menu/";
    const perPage  = 10;
    let data       = [], page = 1, editingId = null;
  
    // DOM refs
    const tabla            = document.querySelector("#tablaArticulos tbody");
    const pagination       = document.getElementById("pagination");
    const formCrear        = document.getElementById("formArticulo");
    const formEditar       = document.getElementById("formEditar");
    const modal            = document.getElementById("modalEditar");
    const cerrarModalBtn   = document.getElementById("cerrarModal");
  
    const restInput        = document.getElementById("restauranteId");
    const nombreInput      = document.getElementById("nombre");
    const categoriaInput   = document.getElementById("categoria");
    const precioInput      = document.getElementById("precio");
    const descripcionInput = document.getElementById("descripcion");
  
    const filtroRest       = document.getElementById("filtroRestaurante");
    const filtroCat        = document.getElementById("filtroCategoria");
  
    const editarNombre     = document.getElementById("editarNombre");
    const editarCategoria  = document.getElementById("editarCategoria");
    const editarPrecio     = document.getElementById("editarPrecio");
    const editarDescripcion= document.getElementById("editarDescripcion");
  
    // Listeners
    formCrear.addEventListener("submit", crearArticulo);
    formEditar.addEventListener("submit", guardarEdicion);
    cerrarModalBtn.addEventListener("click", ()=> modal.style.display = "none");
    filtroRest.addEventListener("input", aplicarFiltros);
    filtroCat.addEventListener("input", aplicarFiltros);
  
    // Carga inicial
    fetchArticulos();
  
    async function fetchArticulos() {
      try {
        const res = await fetch(API);
        data = await res.json();
        actualizarPaginacion();
        mostrarPagina(page);
      } catch {
        tabla.innerHTML = `<tr><td colspan="6">Error cargando artículos.</td></tr>`;
      }
    }
  
    async function crearArticulo(e) {
      e.preventDefault();
      const payload = {
        restaurante_id: restInput.value,
        nombre:         nombreInput.value,
        descripcion:    descripcionInput.value,
        precio:         parseFloat(precioInput.value),
        categoria:      categoriaInput.value
      };
      const res = await fetch(API, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(()=>null);
        return alert("Error al crear:\n"+JSON.stringify(err?.detail||err||res.status));
      }
      formCrear.reset();
      page = 1;
      await fetchArticulos();
    }
  
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="6">No hay artículos.</td></tr>`;
        return;
      }
      arr.forEach(a => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${a.restaurante_id}</td>
          <td>${a.nombre}</td>
          <td>${a.categoria}</td>
          <td>Q${a.precio.toFixed(2)}</td>
          <td>${a.descripcion}</td>
          <td>
            <button class="editar btn btn-sm btn-outline-primary" data-id="${a._id}">Editar</button>
            <button class="eliminar btn btn-sm btn-outline-danger"  data-id="${a._id}">Eliminar</button>
          </td>`;
        tabla.appendChild(tr);
      });
  
      // Borrar
      tabla.querySelectorAll(".eliminar").forEach(btn =>
        btn.addEventListener("click", async () => {
          if (!confirm("Eliminar artículo?")) return;
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
          const a = data.find(x => x._id === editingId);
          if (!a) return;
          editarNombre.value      = a.nombre;
          editarCategoria.value   = a.categoria;
          editarPrecio.value      = a.precio;
          editarDescripcion.value = a.descripcion;
          modal.style.display     = "block";
        })
      );
    }
  
    async function guardarEdicion(e) {
      e.preventDefault();
      const payload = {
        nombre:      editarNombre.value,
        descripcion: editarDescripcion.value,
        precio:      parseFloat(editarPrecio.value),
        categoria:   editarCategoria.value
      };
      const res = await fetch(API + editingId, {
        method:  "PUT",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(()=>null);
        return alert("Error al editar:\n"+JSON.stringify(err?.detail||err||res.status));
      }
      modal.style.display = "none";
      await fetchArticulos();
    }
  
    function aplicarFiltros() {
      const r = filtroRest.value.toLowerCase();
      const c = filtroCat.value.toLowerCase();
      Array.from(tabla.rows).forEach(row => {
        const rr = row.cells[0].textContent.toLowerCase();
        const cc = row.cells[2].textContent.toLowerCase();
        row.style.display = rr.includes(r) && cc.includes(c) ? "" : "none";
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
          page = i; mostrarPagina(i);
          pagination.querySelectorAll("button").forEach(x=>x.classList.remove("active"));
          b.classList.add("active");
        });
        pagination.appendChild(b);
      }
    }
  });
  