import { createApp } from 'vue';
import App from './components/App.vue';
import { initApp } from './commons';

window.init = function(csrfTokenParam, themesPath) {
    const target = '#global-container';
    const teleportTarget = '#airflow-code-editor-modals';
    // CodeMirror
    window.CodeMirror.modeURL = '/static/code_editor/mode/%N/%N.js';
    // Init app
    jQuery(target).appendTo(jQuery('body'));
    const app = createApp(App);
    window.app = initApp(app, target, teleportTarget, csrfTokenParam, themesPath);
}
