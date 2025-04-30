import axios from 'axios';
import { createApp } from 'vue';
import App from './components/App.vue';
import { initApp, git_async } from './commons';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import Notifications from '@kyvg/vue3-notification';
import 'vue-simple-context-menu/dist/vue-simple-context-menu.css';
import shlex from 'shlex';

window.init = function(tokenParam) {
    const target = '#global-container';
    const teleportTarget = '#airflow-code-editor-modals';
    // Init app
    document.body.appendChild(document.querySelector(target));
    const app = createApp(App);
    app.use(Notifications);
    app.component('vue-simple-context-menu', VueSimpleContextMenu);
    window.app = initApp(app, target, teleportTarget, tokenParam);
}

window.show = async function(path) {
    window.app.open(path);
}

window.search = async function(query) {
    window.app.show({ id: "search", path: query, query: query });
}

window.git = async function(args) {
    let gitArgs = shlex.split(args);
    let result = await git_async(gitArgs);
    if (result) {
        console.log(result);
    }
    return result;
}
