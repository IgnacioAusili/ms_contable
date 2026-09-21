(function () {
    "use strict";

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

    async function aplicarPlantilla(plantillaId, urlTemplate) {
        if (!plantillaId) {
            return;
        }

        const url = urlTemplate.replace(
            "/0/",
            `/${plantillaId}/`,
        );

        const response = await fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        });

        if (!response.ok) {
            throw new Error(
                "No se pudieron obtener los detalles de la plantilla."
            );
        }

        const data = await response.json();

        const managementForm = document.querySelector(
            'input[name$="-TOTAL_FORMS"]',
        );

        if (!managementForm) {
            throw new Error(
                "No se encontró el management form del formset."
            );
        }

        const prefix = managementForm.name.replace(
            "-TOTAL_FORMS",
            "",
        );

        const emptyForm = document.querySelector(
            `#${prefix}-empty`,
        );

        if (!emptyForm) {
            throw new Error(
                "No se encontró el formulario vacío del formset."
            );
        }

        for (const detalle of data.detalles) {
            const formIndex = Number(managementForm.value);

            const row = emptyForm.cloneNode(true);

            row.removeAttribute("id");
            row.classList.remove("empty-form");
            row.classList.add("form-row");

            row.innerHTML = row.innerHTML.replaceAll(
                "__prefix__",
                formIndex,
            );

            emptyForm.parentNode.insertBefore(
                row,
                emptyForm,
            );

            const concepto = row.querySelector(
                `[name="${prefix}-${formIndex}-concepto"]`,
            );

            const unidades = row.querySelector(
                `[name="${prefix}-${formIndex}-unidades"]`,
            );

            const expresionBase = row.querySelector(
                `[name="${prefix}-${formIndex}-expresion_base"]`,
            );

            if (concepto) {
                concepto.value = detalle.concepto;

                // Esto reutiliza la lógica existente que obtiene
                // y muestra la unidad.
                concepto.dispatchEvent(
                    new Event("change", {
                        bubbles: true,
                    }),
                );
            }

            if (unidades) {
                unidades.value = detalle.unidades;
            }

            if (expresionBase) {
                expresionBase.value = detalle.expresion_base;
            }

            managementForm.value = formIndex + 1;
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        // Delegación de eventos: funciona con filas agregadas dinámicamente
        document.body.addEventListener("change", function (e) {
            if (e.target.matches(SELECTOR)) {
                actualizarUnidad(e.target);
            }
        });

        const aplicarPlantillaButton =
            document.getElementById("aplicar-plantilla");

        if (aplicarPlantillaButton) {
            aplicarPlantillaButton.addEventListener(
                "click",
                async function () {
                    const plantillaId =
                        document.getElementById(
                            "plantilla-select",
                        ).value;

                    try {
                        await aplicarPlantilla(
                            plantillaId,
                            aplicarPlantillaButton.dataset.urlTemplate,
                        );
                    } catch (error) {
                        console.error(
                            "Error al aplicar la plantilla:",
                            error,
                        );
                    }
                },
            );
        }
    });
})();
