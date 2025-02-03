import axios from 'axios';
import { createApp } from 'vue';
import App from './components/App.vue';
import { initApp, prepareHref, splitPath } from './commons';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import Notifications from '@kyvg/vue3-notification';
import 'vue-simple-context-menu/dist/vue-simple-context-menu.css';

window.init = function(csrfTokenParam, themesPath) {
    const target = '#global-container';
    const teleportTarget = '#airflow-code-editor-modals';
    // Init app
    document.body.appendChild(document.querySelector(target));
    const app = createApp(App);
    app.use(Notifications);
    app.component('vue-simple-context-menu', VueSimpleContextMenu);
    window.app = initApp(app, target, teleportTarget, csrfTokenParam, themesPath);
}

window.show = async function(path) {
    window.app.open(path);
}

window.search = async function(query) {
    window.app.show({ id: "search", path: query, query: query });
}
