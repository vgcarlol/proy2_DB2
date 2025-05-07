document.addEventListener("DOMContentLoaded", () => {
    const API_RES = "http://127.0.0.1:8000/resenas/";
    const API_USU = "http://127.0.0.1:8000/usuarios/";
    const API_REST= "http://127.0.0.1:8000/restaurantes/";
    const perPage = 10;
  
    let data = [], page = 1, editingId = null;
  
    // refs DOM
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
  
    // listeners
    formCrear.addEventListener("submit", crearResena);
    formEditar.addEventListener("submit", guardarEdicion);
    cerrarModalBtn.addEventListener("click", ()=> modal.style.display = "none");
    filtroResta.addEventListener("input", aplicarFiltros);
    filtroCalif.addEventListener("input", aplicarFiltros);
  
    // arranca poblando selects y tabla
    fetchUsuarios();
    fetchRestaurantes();
    fetchResenas();
  
    // trae usuarios y llena el <select>
    async function fetchUsuarios() {
      try {
        let r = await fetch(API_USU);
        let arr = await r.json();
        usuarioInput.innerHTML = `<option value="">-- Seleccionar --</option>` +
          arr.map(u => `<option value="${u._id}">${u.nombre}</option>`).join("");
      } catch(err) {
        console.error("Error cargando usuarios:", err);
        usuarioInput.innerHTML = `<option value="">(error)</option>`;
      }
    }
  
    // trae restaurantes y llena el <select>
    async function fetchRestaurantes() {
      try {
        let r = await fetch(API_REST);
        let arr = await r.json();
        restauranteInput.innerHTML = `<option value="">-- Seleccionar --</option>` +
          arr.map(r => `<option value="${r._id}">${r.nombre}</option>`).join("");
      } catch(err) {
        console.error("Error cargando restaurantes:", err);
        restauranteInput.innerHTML = `<option value="">(error)</option>`;
      }
    }
  
    // traer todas las reseñas
    async function fetchResenas() {
      try {
        let r = await fetch(API_RES);
        data = await r.json();
        actualizarPaginacion();
        mostrarPagina(page);
      } catch {
        tabla.innerHTML = `<tr><td colspan="7">Error cargando reseñas.</td></tr>`;
      }
    }
  
    // crear nueva reseña
    async function crearResena(e) {
      e.preventDefault();
      const payload = {
        usuario_id:     usuarioInput.value,
        restaurante_id: restauranteInput.value,
        orden_id:       ordenInput.value || null,
        calificacion:   parseInt(calificacionInput.value,10),
        comentario:     comentarioInput.value.trim(),
        fecha:          new Date(fechaInput.value).toISOString()
      };
      let res = await fetch(API_RES, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        let err = await res.json().catch(()=>null);
        return alert("Error al crear:\n"+ JSON.stringify(err?.detail||err||res.status, null,2));
      }
      formCrear.reset();
      page = 1;
      await fetchResenas();
    }
  
    // render de tabla + eventos
    function renderTable(arr) {
      tabla.innerHTML = "";
      if (!arr.length) {
        tabla.innerHTML = `<tr><td colspan="7">No hay reseñas.</td></tr>`;
        return;
      }
      arr.forEach(r => {
        let tr = document.createElement("tr");
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
          </td>`;
        tabla.appendChild(tr);
      });
      // borrar
      tabla.querySelectorAll(".eliminar").forEach(b=>
        b.addEventListener("click", async ()=>{
          if (!confirm("Eliminar reseña?")) return;
          await fetch(API_RES + b.dataset.id, {method:"DELETE"});
          data = data.filter(x=> x._id!==b.dataset.id);
          actualizarPaginacion();
          mostrarPagina(page);
        })
      );
      // editar
      tabla.querySelectorAll(".editar").forEach(b=>
        b.addEventListener("click", ()=>{
          editingId = b.dataset.id;
          let orig = data.find(x=> x._id===editingId);
          if (!orig) return alert("Reseña no encontrada");
          editarCalifInput.value    = orig.calificacion;
          editarComentario.value    = orig.comentario;
          editarFechaInput.value    = new Date(orig.fecha).toISOString().slice(0,10);
          modal.style.display = "block";
        })
      );
    }
  
    // guardar cambios
    async function guardarEdicion(e) {
      e.preventDefault();
      let orig = data.find(x=> x._id===editingId);
      if (!orig) return alert("Reseña no encontrada");
      const payload = {
        usuario_id:     orig.usuario_id,
        restaurante_id: orig.restaurante_id,
        orden_id:       orig.orden_id||null,
        calificacion:   parseInt(editarCalifInput.value,10),
        comentario:     editarComentario.value.trim(),
        fecha:          new Date(editarFechaInput.value).toISOString()
      };
      let res = await fetch(API_RES + editingId, {
        method:"PUT", headers:{"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        let err = await res.json().catch(()=>null);
        return alert("Error al editar:\n"+JSON.stringify(err?.detail||err||res.status,null,2));
      }
      modal.style.display = "none";
      await fetchResenas();
    }
  
    // filtros y paginación
    function aplicarFiltros() {
      let fR = filtroResta.value.toLowerCase(),
          fC = filtroCalif.value.toLowerCase();
      Array.from(tabla.rows).forEach(r=>{
        let tR = r.cells[1].textContent.toLowerCase(),
            tC = r.cells[3].textContent.toLowerCase();
        r.style.display = tR.includes(fR)&&tC.includes(fC) ? "" : "none";
      });
    }
    function mostrarPagina(n) {
      let start = (n-1)*perPage;
      renderTable(data.slice(start,start+perPage));
    }
    function actualizarPaginacion() {
      pagination.innerHTML="";
      let total = Math.ceil(data.length/perPage)||1;
      for(let i=1;i<=total;i++){
        let b=document.createElement("button");
        b.textContent=i;
        b.className="btn btn-outline-secondary me-1"+(i===page?" active":"");
        b.onclick=()=>{
          page=i; mostrarPagina(i);
          pagination.querySelectorAll("button").forEach(x=>x.classList.remove("active"));
          b.classList.add("active");
        };
        pagination.appendChild(b);
      }
    }
  });
  