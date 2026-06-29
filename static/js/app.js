// HTMX configuration
document.addEventListener("DOMContentLoaded", function () {
  htmx.config.defaultSwapStyle = "outerHTML";

  // CSRF token injection for HTMX
  document.body.addEventListener("htmx:configRequest", function (event) {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfToken) {
      event.detail.headers["X-CSRFToken"] = csrfToken.value;
    }
  });

  // Global HTMX error handler
  document.body.addEventListener("htmx:responseError", function (event) {
    console.error("HTMX request failed:", event.detail);
    showToast("An error occurred. Please try again.", "error");
  });
});

function showToast(message, type = "info") {
  const container = document.getElementById("flash-messages") || createToastContainer();
  const colors = {
    info: "bg-blue-50 border-blue-200 text-blue-800",
    success: "bg-green-50 border-green-200 text-green-800",
    error: "bg-red-50 border-red-200 text-red-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
  };
  const toast = document.createElement("div");
  toast.className = `flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg max-w-sm border ${colors[type] || colors.info}`;
  toast.innerHTML = `<p class="text-sm font-medium flex-1">${message}</p>
    <button onclick="this.parentElement.remove()" class="opacity-60 hover:opacity-100 text-current">×</button>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function createToastContainer() {
  const el = document.createElement("div");
  el.id = "flash-messages";
  el.className = "fixed top-4 right-4 z-50 space-y-2";
  document.body.appendChild(el);
  return el;
}
