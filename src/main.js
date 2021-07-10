import Vue from 'vue'
import App from './components/App.vue'
import { initCsrfToken } from "./commons";

window.init = function(csrfTokenParam) {
    // Init
    CodeMirror.modeURL = '/static/code_editor/mode/%N/%N.js';
    // CSRF Token setup
    initCsrfToken(csrfTokenParam)
    jQuery('#global-container').appendTo(jQuery("body"));
    // Init app
    window.app = new Vue({
      render: h => h(App),
    }).$mount('#global-container')
}
