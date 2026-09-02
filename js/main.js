// Osha With Zahid: shared site behavior

document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav toggle
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    nav.querySelectorAll(".nav-links a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // FAQ accordion
  document.querySelectorAll(".accordion-trigger").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var panel = document.getElementById(btn.getAttribute("aria-controls"));

      document.querySelectorAll(".accordion-trigger").forEach(function (other) {
        if (other !== btn) {
          other.setAttribute("aria-expanded", "false");
          var otherPanel = document.getElementById(other.getAttribute("aria-controls"));
          if (otherPanel) otherPanel.style.maxHeight = null;
        }
      });

      btn.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (panel) panel.style.maxHeight = expanded ? null : panel.scrollHeight + "px";
    });
  });

  // Booking tabs (Calendly / Typeform)
  var tabButtons = document.querySelectorAll(".booking-tab-btn");
  var panels = document.querySelectorAll(".booking-panel");
  tabButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabButtons.forEach(function (b) { b.classList.remove("is-active"); });
      panels.forEach(function (p) { p.classList.remove("is-active"); });
      btn.classList.add("is-active");
      var target = document.getElementById(btn.getAttribute("data-target"));
      if (target) target.classList.add("is-active");
    });
  });

  // Footer year
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
});
