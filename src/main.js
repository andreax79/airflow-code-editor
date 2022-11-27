import { createApp } from 'vue';
import App from './components/App.vue';
import { initApp } from './commons';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import 'vue-simple-context-menu/dist/vue-simple-context-menu.css';

window.init = function(csrfTokenParam, themesPath) {
    const target = '#global-container';
    const teleportTarget = '#airflow-code-editor-modals';
    // CodeMirror
    window.CodeMirror.modeURL = '/static/code_editor/mode/%N/%N.js';
    // Init app
    jQuery(target).appendTo(jQuery('body'));
    const app = createApp(App);
    app.component('vue-simple-context-menu', VueSimpleContextMenu);
    window.app = initApp(app, target, teleportTarget, csrfTokenParam, themesPath);
}
