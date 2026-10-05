document.addEventListener("click", function (event) {
    if (!(event.target instanceof Element)) {
        return;
    }

    const trigger = event.target.closest("[data-help-target]");
    if (trigger) {
        const dialog = document.getElementById(trigger.dataset.helpTarget);
        if (dialog && typeof dialog.showModal === "function") {
            dialog.showModal();
        }
        return;
    }

    const closeButton = event.target.closest("[data-help-close]");
    if (closeButton) {
        closeButton.closest("dialog")?.close();
        return;
    }

    const dialog = event.target.closest("dialog.help-dialog");
    if (dialog && event.target === dialog) {
        const bounds = dialog.getBoundingClientRect();
        const clickedOutside =
            event.clientX < bounds.left ||
            event.clientX > bounds.right ||
            event.clientY < bounds.top ||
            event.clientY > bounds.bottom;

        if (clickedOutside) {
            dialog.close();
        }
    }
});
