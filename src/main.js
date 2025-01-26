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
    if (!path.startsWith('/')) {
        path = '/' + path;
    }
    const response = await axios.head(prepareHref('tree/files' + path));
    const exists = response.headers['x-exists'] == 'true';
    const leaf = response.headers['x-leaf'] == 'true';
    const sectionAndName = splitPath(response.headers['x-id']);
    const section = sectionAndName[0];
    const name = '/' + (sectionAndName[1] || '').trim();
    if (leaf || !exists) {
        window.app.show({ id: section, path: name, type: 'blob' });
    } else {
        window.app.show({ id: section, path: name, type: 'tree' });
    }
}

window.search = async function(query) {
    window.app.show({ id: "search", path: query, query: query });
}
