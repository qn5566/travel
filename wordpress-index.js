/* Taiwan Explorer WordPress JavaScript */
    document.addEventListener("DOMContentLoaded", function () {
      var phone = document.querySelector(".hero-phone");
      if (!phone || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      phone.classList.add("is-breathing");
    });
