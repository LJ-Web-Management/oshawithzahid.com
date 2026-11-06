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
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Header shadow once the page scrolls
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Fade-in on scroll
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -60px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  // Guide category filters
  var filters = document.querySelectorAll(".filter");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var cat = btn.getAttribute("data-filter");
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      document.querySelectorAll("[data-category]").forEach(function (card) {
        card.hidden = cat !== "all" && card.getAttribute("data-category") !== cat;
      });
    });
  });

  // Table of contents: highlight the section in view
  var tocLinks = document.querySelectorAll(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var tocIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
          var link = byId[entry.target.id];
          if (link) link.classList.add("is-active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(byId).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) tocIo.observe(el);
    });
  }

  // Contact form: send through FormSubmit without leaving the page.
  // Without JS the form still posts to FormSubmit and shows its thank-you page.
  var contactForm = document.getElementById("contactForm");
  if (contactForm && window.fetch && window.FormData) {
    var status = contactForm.querySelector(".form-status");
    var submitBtn = contactForm.querySelector('button[type="submit"]');
    var btnHtml = submitBtn.innerHTML;
    var to = contactForm.getAttribute("data-email");

    var escapeHtml = function (s) {
      return String(s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    };

    var showStatus = function (kind, html) {
      status.className = "form-status is-" + kind;
      status.innerHTML = html;
      status.hidden = false;
    };

    // Fallback link that pre-fills the visitor's email app, so a failed send never loses their message
    var mailtoFallback = function (data) {
      var body = "Name: " + (data.Name || "") + "\nEmail: " + (data.email || "") +
        "\nCourse of interest: " + (data["Course of Interest"] || "") + "\n\n" + (data.Message || "");
      return "mailto:" + to + "?subject=" + encodeURIComponent("Question from oshawithzahid.com") +
        "&body=" + encodeURIComponent(body);
    };

    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = {};
      new FormData(contactForm).forEach(function (value, key) { data[key] = value; });
      if (data._honey) return; // bot filled the hidden field
      data._replyto = data.email;

      submitBtn.disabled = true;
      submitBtn.textContent = "Sending...";
      status.hidden = true;

      fetch(contactForm.getAttribute("data-ajax-action"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (res) { return res.json(); })
        .then(function (json) {
          if (String(json.success) !== "true") throw new Error(json.message || "Send failed");
          contactForm.reset();
          showStatus("success", "<p><strong>Thanks, your message was sent.</strong> Zahid will reply to " +
            escapeHtml(data.email) + " soon.</p>");
        })
        .catch(function () {
          showStatus("error", '<p>Sorry, your message didn\'t go through. Please <a href="' +
            escapeHtml(mailtoFallback(data)) + '">email it to Zahid instead</a> (your message is already filled in), or write to ' +
            '<a href="mailto:' + to + '">' + to + "</a>.</p>");
        })
        .then(function () {
          submitBtn.disabled = false;
          submitBtn.innerHTML = btnHtml;
        });
    });
  }

  // Footer year
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
});
