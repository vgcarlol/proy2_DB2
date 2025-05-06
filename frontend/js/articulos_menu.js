document.addEventListener("DOMContentLoaded", () => {
    const API_ARTIK = "http://127.0.0.1:8000/menu/";
    const API_REST  = "http://127.0.0.1:8000/restaurantes/";
    const perPage   = 10;
    let data        = [], page = 1, editingId = null;
  
    // refs DOM
    const tabla             = document.querySelector("#tablaArticulos tbody");
    const pagination        = document.getElementById("pagination");
    const formCrear         = document.getElementById("formArticulo");
    const formEditar        = document.getElementById("formEditar");
    const modal             = document.getElementById("modalEditar");
    const cerrarModalBtn    = document.getElementById("cerrarModal");
  
    const restSelect        = document.getElementById("restauranteSelect");
    const nombreInput       = document.getElementById("nombre");
    const categoriaInput    = document.getElementById("categoriaInput");
    const categoriasList    = document.getElementById("categoriasList");
    const precioInput       = document.getElementById("precio");
    const descripcionInput  = document.getElementById("descripcion");
  
    const filtroRest        = document.getElementById("filtroRestaurante");
    const filtroCat         = document.getElementById("filtroCategoria");
  
    const editarNombre      = document.getElementById("editarNombre");
    const editarCategoria   = document.getElementById("editarCategoria");
    const editarPrecio      = document.getElementById("editarPrecio");
    const editarDescripcion = document.getElementById("editarDescripcion");
  
    // listeners
    formCrear.addEventListener("submit", crearArticulo);
    formEditar.addEventListener("submit", guardarEdicion);
    cerrarModalBtn.addEventListener("click", () => modal.style.display = "none");
    filtroRest.addEventListener("input", aplicarFiltros);
    filtroCat.addEventListener("input", aplicarFiltros);
  
    // carga inicial
    fetchRestaurantes();
    fetchArticulos();
  
    // 1) cargar restaurantes
    async function fetchRestaurantes() {
      try {
        const res = await fetch(API_REST);
        const arr = await res.json();
        restSelect.innerHTML = `<option value="">-- Seleccionar --</option>`;
        arr.forEach(r => {
          restSelect.innerHTML += `<option value="${r._id}">${r.nombre}</option>`;
        });
      } catch (err) {
        console.error("Error cargando restaurantes:", err);
        restSelect.innerHTML = `<option value="">Error al cargar</option>`;
      }
    }
  
    // 2) cargar artículos y derivar categorías
    async function fetchArticulos() {
      try {
        const res = await fetch(API_ARTIK);
        data = await res.json();
  
        // derivar categorías únicas para el datalist
        const cats = [...new Set(data.map(a => a.categoria))];
        categoriasList.innerHTML = cats.map(c => `<option value="${c}">`).join("");
  
        actualizarPaginacion();
        mostrarPagina(page);
  
        // reaplicar filtros tras pintar
        aplicarFiltros();
  
      } catch (err) {
        console.error("Error cargando artículos:", err);
        tabla.innerHTML = `<tr><td colspan="6">Error cargando artículos.</td></tr>`;
      }
    }
  
    // crear
    async function crearArticulo(e) {
      e.preventDefault();
  
      const payload = {
        restaurante_id: restSelect.value,
        nombre:         nombreInput.value,
        descripcion:    descripcionInput.value,
        precio:         parseFloat(precioInput.value),
        categoria:      categoriaInput.value
      };
  
      console.log("Creando artículo con payload:", payload);
  
      try {
        const res = await fetch(API_ARTIK, {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(payload),
        });
        console.log("Respuesta POST:", res.status, await res.clone().text());
  
        if (!res.ok) {
          let errDetail;
          try { errDetail = await res.json(); }
          catch { errDetail = await res.text(); }
          console.error("Error en creación:", errDetail);
          return alert("Error al crear artículo:\n" + JSON.stringify(errDetail, null, 2));
        }
  
        // limpiar filtros para que no oculte la nueva fila
        filtroRest.value = "";
        filtroCat.value  = "";
  
        formCrear.reset();
  
        // recargar y saltar a la última página
        await fetchArticulos();
        page = Math.ceil(data.length / perPage);
        mostrarPagina(page);
  
      } catch (err) {
        console.error("Excepción al crear artículo:", err);
        alert("Error de red al crear artículo:\n" + err.message);
      }
    }
  
    // render tabla
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="6">No hay artículos.</td></tr>`;
        return;
      }
      arr.forEach(a => {
        tabla.innerHTML += `
          <tr>
            <td>${a.restaurante_id}</td>
            <td>${a.nombre}</td>
            <td>${a.categoria}</td>
            <td>Q${a.precio.toFixed(2)}</td>
            <td>${a.descripcion}</td>
            <td>
              <button class="editar btn btn-sm btn-outline-primary" data-id="${a._id}">Editar</button>
              <button class="eliminar btn btn-sm btn-outline-danger"  data-id="${a._id}">Eliminar</button>
            </td>
          </tr>`;
      });
  
      // borrar
      tabla.querySelectorAll(".eliminar").forEach(btn =>
        btn.addEventListener("click", async () => {
          if (!confirm("Eliminar artículo?")) return;
          await fetch(API_ARTIK + btn.dataset.id, { method: "DELETE" });
          data = data.filter(x => x._id !== btn.dataset.id);
          actualizarPaginacion();
          mostrarPagina(page);
          aplicarFiltros();
        })
      );
  
      // editar
      tabla.querySelectorAll(".editar").forEach(btn =>
        btn.addEventListener("click", () => {
          editingId = btn.dataset.id;
          const art = data.find(x => x._id === editingId);
          if (!art) return;
          editarNombre.value      = art.nombre;
          editarCategoria.value   = art.categoria;
          editarPrecio.value      = art.precio;
          editarDescripcion.value = art.descripcion;
          modal.style.display     = "block";
        })
      );
    }
  
    // guardar edición
    async function guardarEdicion(e) {
      e.preventDefault();
      const art = data.find(x => x._id === editingId);
      if (!art) return alert("Artículo no encontrado");
  
      const payload = {
        restaurante_id: art.restaurante_id,
        nombre:         editarNombre.value,
        descripcion:    editarDescripcion.value,
        precio:         parseFloat(editarPrecio.value),
        categoria:      editarCategoria.value
      };
  
      console.log("Editando artículo", editingId, "con payload:", payload);
  
      try {
        const res = await fetch(API_ARTIK + editingId, {
          method:  "PUT",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(payload),
        });
        console.log("Respuesta PUT:", res.status, await res.clone().text());
  
        if (!res.ok) {
          let errDetail;
          try { errDetail = await res.json(); }
          catch { errDetail = await res.text(); }
          console.error("Error al editar:", errDetail);
          return alert("Error al editar:\n" + JSON.stringify(errDetail, null, 2));
        }
  
        modal.style.display = "none";
        await fetchArticulos();
      } catch (err) {
        console.error("Excepción al editar artículo:", err);
        alert("Error de red al editar artículo:\n" + err.message);
      }
    }
  
    // filtros
    function aplicarFiltros() {
      const r = filtroRest.value.toLowerCase();
      const c = filtroCat.value.toLowerCase();
      Array.from(tabla.rows).forEach(row => {
        const rr = row.cells[0].textContent.toLowerCase();
        const cc = row.cells[2].textContent.toLowerCase();
        row.style.display = rr.includes(r) && cc.includes(c) ? "" : "none";
      });
    }
  
    // paginación
    function mostrarPagina(n) {
      const start = (n - 1) * perPage;
      renderTable(data.slice(start, start + perPage));
      aplicarFiltros();
    }
    function actualizarPaginacion() {
      pagination.innerHTML = "";
      const total = Math.ceil(data.length / perPage) || 1;
      for (let i = 1; i <= total; i++) {
        const b = document.createElement("button");
        b.textContent = i;
        b.className = "btn btn-outline-secondary me-1" + (i === page ? " active" : "");
        b.addEventListener("click", () => {
          page = i;
          mostrarPagina(i);
        });
        pagination.appendChild(b);
      }
    }
  });
  