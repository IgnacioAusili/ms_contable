(function () {
    "use strict";

    // Ajustá "detalleliquidacion" al related_name / prefijo de tu formset.
    // Podés verlo en el HTML: los ids son "id_<prefijo>-0-concepto".
    const SELECTOR = 'select[id$="-concepto"]';

    function actualizarUnidad(select) {
        const fila = select.closest("tr");
        if (!fila) return;
        const span = fila.querySelector(".unidad-display");
        if (!span) return;

        const conceptoId = select.value;
        if (!conceptoId) {
            span.textContent = "";
            return;
        }

        // URL relativa al change_form actual:
        // /admin/app/liquidacionempleado/<pk>/change/  ->  ../../concepto-unidad/<id>/
        // /admin/app/liquidacionempleado/add/          ->  ../concepto-unidad/<id>/
        const base = window.location.pathname.includes("/add/")
            ? "../concepto-unidad/"
            : "../../concepto-unidad/";

        fetch(base + conceptoId + "/", { credentials: "same-origin" })
            .then((r) => r.json())
            .then((data) => {
                span.textContent = data.unidad || "no_encontrado";
            })
            .catch(() => {
                span.textContent = "";
            });
    }

    document.addEventListener("DOMContentLoaded", function () {
        // Delegación de eventos: funciona con filas agregadas dinámicamente
        document.body.addEventListener("change", function (e) {
            if (e.target.matches(SELECTOR)) {
                actualizarUnidad(e.target);
            }
        });
    });
})();
