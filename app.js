/* =========================================================================
   Cotizador de Viajes — interacciones de la interfaz.
   JavaScript mínimo y sin dependencias. Todo funciona con formularios HTML
   normales; esto solo mejora la experiencia.
   ========================================================================= */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {

    // 1) Mostrar u ocultar formularios en línea (botones "Agregar…").
    //    <button data-toggle="id-del-formulario">
    document.querySelectorAll("[data-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var destino = document.getElementById(btn.getAttribute("data-toggle"));
        if (!destino) return;
        var oculto = destino.hasAttribute("hidden");
        if (oculto) {
          destino.removeAttribute("hidden");
          var primer = destino.querySelector("input, select, textarea");
          if (primer) primer.focus();
        } else {
          destino.setAttribute("hidden", "");
        }
      });
    });

    // 2) Auto-enviar el formulario al cambiar un interruptor (incluir / por persona).
    //    <input type="checkbox" data-autosubmit>
    document.querySelectorAll("[data-autosubmit]").forEach(function (input) {
      input.addEventListener("change", function () {
        if (input.form) input.form.submit();
      });
    });

    // 3) Prellenar el tipo de cambio con el valor sugerido de la moneda elegida.
    //    El <select> tiene <option data-rate="0.055"> y el input id="tipoCambio".
    var selMoneda = document.getElementById("selMoneda");
    var inputTC = document.getElementById("tipoCambio");
    if (selMoneda && inputTC) {
      var sincronizar = function () {
        var op = selMoneda.options[selMoneda.selectedIndex];
        var rate = op ? op.getAttribute("data-rate") : null;
        if (rate) inputTC.value = rate;
      };
      selMoneda.addEventListener("change", sincronizar);
      if (!inputTC.value) sincronizar();
    }

    // 4) Confirmar antes de eliminar. <form data-confirm="mensaje">
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (!window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
      });
    });

    // 5) Botón de imprimir. <button data-print>
    document.querySelectorAll("[data-print]").forEach(function (btn) {
      btn.addEventListener("click", function () { window.print(); });
    });

  });
})();
