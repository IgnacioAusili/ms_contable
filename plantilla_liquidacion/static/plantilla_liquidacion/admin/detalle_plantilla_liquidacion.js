(function () {
    "use strict";

    const SELECTOR = 'select[id$="-concepto"]';

    function actualizarDetalles(select) {
        const fila = select.closest("tr");
        if (!fila) return;

        const spanUnidad = fila.querySelector(".unidad-display");
        const spanCategoria = fila.querySelector(".categoria-display");
        const spanTipo = fila.querySelector(".tipo-display");
        const spanGrupo = fila.querySelector(".grupo-display");

        if (!spanUnidad || !spanCategoria || !spanTipo || !spanGrupo) return;

        const celdaOriginal = fila.querySelector(".original");
        let parrafoIdentificador = celdaOriginal?.querySelector("p");

        const conceptoId = select.value;

        if (!conceptoId) {
            spanTipo.textContent = "-";
            spanGrupo.textContent = "-";
            spanUnidad.textContent = "-";
            spanCategoria.textContent = "-";

            if (parrafoIdentificador) {
                parrafoIdentificador.textContent = "";
            }

            return;
        }

        // URL relativa al change_form actual:
        // /admin/app/liquidacionempleado/<pk>/change/  ->  ../../concepto-detalles/<id>/
        // /admin/app/liquidacionempleado/add/          ->  ../concepto-detalles/<id>/
        const base = window.location.pathname.includes("/add/")
            ? "../concepto-detalles/"
            : "../../concepto-detalles/";

        fetch(base + conceptoId + "/", { credentials: "same-origin" })
            .then((r) => r.json())
            .then((data) => {
                spanUnidad.textContent = data.unidad || "no_encontrado";
                spanCategoria.textContent = data.categoria || "no_encontrado";
                spanTipo.textContent = data.tipo || "no_encontrado";
                spanGrupo.textContent = data.grupo || "-";

                // Identificador mostrado por Django en .original
                if (celdaOriginal) {
                    if (!parrafoIdentificador) {
                        parrafoIdentificador = document.createElement("p");
                        celdaOriginal.prepend(parrafoIdentificador);
                    }

                    parrafoIdentificador.textContent =
                        data.identificador
                            ? `identificador: ${data.identificador}`
                            : "";

                    fila.classList.toggle("has_original", Boolean(data.identificador));
                }
            })
            .catch(() => {
                spanUnidad.textContent = "-";
                spanCategoria.textContent = "-";
                spanTipo.textContent = "-";
                spanGrupo.textContent = "-";

                if (parrafoIdentificador) {
                    parrafoIdentificador.textContent = "";
                }
            });
    }

    function ajustarAlturaTextarea(textarea) {
        textarea.style.height = "auto";

        const maxHeight = parseFloat(
            getComputedStyle(textarea).maxHeight
        );

        textarea.style.height = `${Math.min(
            textarea.scrollHeight,
            maxHeight
        )}px`;
    }

    function inlineTablaWrapper() {
        const group = document.getElementById("detalles-group");
        if (!group) return;

        const table = group.querySelector("table");
        if (!table) return;

        const wrapper = document.createElement("div");
        wrapper.className = "detalles-table-wrapper";

        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.body.addEventListener("change", function (e) {
            if (e.target.matches(SELECTOR)) {
                actualizarDetalles(e.target);
            }
        });

        document.body.addEventListener("input", function (e) {
            if (e.target.matches("#detalles-group .field-formula_base textarea")) {
                ajustarAlturaTextarea(e.target);
            }
        });

        document.querySelectorAll(
            "#detalles-group .field-formula_base textarea"
        ).forEach(ajustarAlturaTextarea);

        inlineTablaWrapper();

        const dialogo = document.getElementById("modal-ayuda-liquidacion");
        const abrirAyuda = document.getElementById("abrir-ayuda");
        const cerrarAyuda = document.getElementById("cerrar-ayuda");

        if (dialogo && abrirAyuda) {
            abrirAyuda.addEventListener("click", function () {
                dialogo.showModal();
            });
        }

        if (dialogo && cerrarAyuda) {
            cerrarAyuda.addEventListener("click", function () {
                dialogo.close();
            });
        }
    });
})();
