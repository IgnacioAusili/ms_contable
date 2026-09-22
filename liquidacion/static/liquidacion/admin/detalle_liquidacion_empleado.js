(function () {
    "use strict";

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

            const formulaBase = row.querySelector(
                `[name="${prefix}-${formIndex}-formula_base"]`,
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

            if (formulaBase) {
                formulaBase.value = detalle.formula_base;
                ajustarAlturaTextarea(formulaBase);
            }

            managementForm.value = formIndex + 1;
        }
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
