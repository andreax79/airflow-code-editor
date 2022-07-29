import { createApp } from "vue";
import App from "./components/App.vue";
import { initCsrfToken } from "./commons";

window.init = function(csrfTokenParam) {
    // Init
    window.CodeMirror.modeURL = '/static/code_editor/mode/%N/%N.js';
    // CSRF Token setup
    initCsrfToken(csrfTokenParam)
    jQuery('#global-container').appendTo(jQuery("body"));
    // Init app
    window.app = createApp(App);
    window.app.mount('#global-container')
}
