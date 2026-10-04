(() => {
    const savedTheme = localStorage.getItem("theme");
    const darkPreference = window.matchMedia?.("(prefers-color-scheme: dark)");
    const lightPreference = window.matchMedia?.("(prefers-color-scheme: light)");
    const systemTheme = darkPreference?.matches
        ? "dark"
        : lightPreference?.matches
            ? "light"
            : "dark";

    document.documentElement.dataset.theme =
        savedTheme === "light" || savedTheme === "dark" ? savedTheme : systemTheme;

    document.addEventListener("click", (event) => {
        const button = event.target instanceof Element && event.target.closest(".theme-toggle");
        if (!button) return;

        event.stopImmediatePropagation();
        const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        document.documentElement.dataset.theme = theme;
        localStorage.setItem("theme", theme);
    }, true);
})();
