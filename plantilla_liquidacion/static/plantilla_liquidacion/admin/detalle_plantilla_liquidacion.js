(function () {
    "use strict";

    // Ajustá "detalleliquidacion" al related_name / prefijo de tu formset.
    // Podés verlo en el HTML: los ids son "id_<prefijo>-0-concepto".
    const SELECTOR = 'select[id$="-concepto"]';

    function actualizarDetalles(select) {
        const fila = select.closest("tr");
        if (!fila) return;
        const spanUnidad = fila.querySelector(".unidad-display");
        const spanCategoria = fila.querySelector(".categoria-display");
        const spanTipo = fila.querySelector(".tipo-display");
        if (!spanUnidad || !spanCategoria || !spanTipo) return;

        const conceptoId = select.value;
        if (!conceptoId) {
            spanUnidad.textContent = "";
            spanCategoria.textContent = "";
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
            })
            .catch(() => {
                spanUnidad.textContent = "";
                spanCategoria.textContent = "";
                spanTipo.textContent = "";
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

    document.addEventListener("DOMContentLoaded", function () {
        // Delegación de eventos: funciona con filas agregadas dinámicamente
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

        // Ayuda
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
