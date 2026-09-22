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
        if (!spanUnidad) return;
        if (!spanCategoria) return;

        const conceptoId = select.value;
        if (!conceptoId) {
            spanUnidad.textContent = "";
            spanCategoria.textContent = "";
            return;
        }

        // URL relativa al change_form actual:
        // /admin/app/liquidacionempleado/<pk>/change/  ->  ../../concepto-unidad/<id>/
        // /admin/app/liquidacionempleado/add/          ->  ../concepto-unidad/<id>/
        const base = window.location.pathname.includes("/add/")
            ? "../concepto-detalles/"
            : "../../concepto-detalles/";

        fetch(base + conceptoId + "/", { credentials: "same-origin" })
            .then((r) => r.json())
            .then((data) => {
                spanUnidad.textContent = data.unidad || "no_encontrado";
                spanCategoria.textContent = data.categoria || "no_encontrado";
            })
            .catch(() => {
                spanUnidad.textContent = "";
                spanCategoria.textContent = "";
            });
    }

    document.addEventListener("DOMContentLoaded", function () {
        // Delegación de eventos: funciona con filas agregadas dinámicamente
        document.body.addEventListener("change", function (e) {
            if (e.target.matches(SELECTOR)) {
                actualizarDetalles(e.target);
            }
        });
    });
})();
