document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            var closeBtn = alert.querySelector(".btn-close");
            if (closeBtn) closeBtn.click();
        }, 5000);
    });

    var themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            var current = document.documentElement.getAttribute("data-bs-theme") || "light";
            var next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-bs-theme", next);
            localStorage.setItem("statuspage-theme", next);
        });
    }
});
