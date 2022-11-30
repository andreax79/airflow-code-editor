import { createApp, ref } from 'vue';
import axios from 'axios';
import VueUniversalModal from 'vue-universal-modal';

export const CSRF_REFRESH = 1000 * 60 * 10;
export const COLORS = [
    "#ffab1d", "#fd8c25", "#f36e4a", "#fc6148", "#d75ab6", "#b25ade", "#6575ff", "#7b77e9", "#4ea8ec", "#00d0f5", "#4eb94e", "#51af23", "#8b9f1c", "#d0b02f", "#d0853a", "#a4a4a4",
    "#ffc51f", "#fe982c", "#fd7854", "#ff705f", "#e467c3", "#bd65e9", "#7183ff", "#8985f7", "#55b6ff", "#10dcff", "#51cd51", "#5cba2e", "#9eb22f", "#debe3d", "#e19344", "#b8b8b8",
    "#ffd03b", "#ffae38", "#ff8a6a", "#ff7e7e", "#ef72ce", "#c56df1", "#8091ff", "#918dff", "#69caff", "#3ee1ff", "#72da72", "#71cf43", "#abbf3c", "#e6c645", "#eda04e", "#c5c5c5",
    "#ffd84c", "#ffb946", "#ff987c", "#ff8f8f", "#fb7eda", "#ce76fa", "#90a0ff", "#9c98ff", "#74cbff", "#64e7ff", "#7ce47c", "#85e357", "#b8cc49", "#edcd4c", "#f9ad58", "#d0d0d0",
    "#ffe651", "#ffbf51", "#ffa48b", "#ff9d9e", "#ff8de1", "#d583ff", "#97a9ff", "#a7a4ff", "#82d3ff", "#76eaff", "#85ed85", "#8deb5f", "#c2d653", "#f5d862", "#fcb75c", "#d7d7d7",
    "#fff456", "#ffc66d", "#ffb39e", "#ffabad", "#ff9de5", "#da90ff", "#9fb2ff", "#b2afff", "#8ddaff", "#8bedff", "#99f299", "#97f569", "#cde153", "#fbe276", "#ffc160", "#e1e1e1",
    "#fff970", "#ffd587", "#ffc2b2", "#ffb9bd", "#ffa5e7", "#de9cff", "#afbeff", "#bbb8ff", "#9fd4ff", "#9aefff", "#b3f7b3", "#a0fe72", "#dbef6c", "#fcee98", "#ffca69", "#eaeaea",
    "#763700", "#9f241e", "#982c0e", "#a81300", "#80035f", "#650d90", "#082fca", "#3531a3", "#1d4892", "#006f84", "#036b03", "#236600", "#445200", "#544509", "#702408", "#343434",
    "#9a5000", "#b33a20", "#b02f0f", "#c8210a", "#950f74", "#7b23a7", "#263dd4", "#4642b4", "#1d5cac", "#00849c", "#0e760e", "#287800", "#495600", "#6c5809", "#8d3a13", "#4e4e4e",
    "#c36806", "#c85120", "#bf3624", "#df2512", "#aa2288", "#933bbf", "#444cde", "#5753c5", "#1d71c6", "#0099bf", "#188018", "#2e8c00", "#607100", "#907609", "#ab511f", "#686868",
    "#e47b07", "#e36920", "#d34e2a", "#ec3b24", "#ba3d99", "#9d45c9", "#4f5aec", "#615dcf", "#3286cf", "#00abca", "#279227", "#3a980c", "#6c7f00", "#ab8b0a", "#b56427", "#757575",
    "#ff911a", "#fc8120", "#e7623e", "#fa5236", "#ca4da9", "#a74fd3", "#5a68ff", "#6d69db", "#489bd9", "#00bcde", "#36a436", "#47a519", "#798d0a", "#c1a120", "#bf7730", "#8e8e8e"]

var csrfToken = null;
var vueApp = null;
var themesPath = null;

export function showError(message) {
    if (vueApp) {
        vueApp.showError(message);
    }
}

export function showWarning(message) {
    if (vueApp) {
        vueApp.showWarning(message);
    }
}

export function normalize(path) {
    if (path[0] != '/') {
        path = '/' + path;
    }
    return path.split(/[/]+/).join('/');
}

export function basename(path) {
    return path.substring(path.lastIndexOf('/') + 1);
}

export function prepareHref(path) {
    // Return the full path of the URL
    return document.location.pathname + path;
}

export function splitPath(path) {
    // Split path into head, tail
    if (!path) {
        return ['', ''];
    } else {
        if (path[0] == '/') {
            path = path.substring(1);
        }
        let head = path.substring(0, path.indexOf('/'));
        let tail = path.substring(path.indexOf('/') + 1);
        if (!head) {
            head = tail;
            tail = '';
        }
        return [head, tail];
    }
}

async function refreshCsrfToken() {
    // Refresh CSRF Token
    try {
        const response = await axios.get(prepareHref('ping'));
        csrfToken = response.data.value;
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
        setTimeout(refreshCsrfToken, CSRF_REFRESH);
    } catch(error) {
        setTimeout(refreshCsrfToken, CSRF_REFRESH);
    }
}

export function initCsrfToken(csrfTokenParam) {
    csrfToken = csrfTokenParam;
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    setTimeout(refreshCsrfToken, CSRF_REFRESH);
}

export async function git_async(args) {
    const payload = { args: [].concat.apply([], args.filter(x => x != null)) };  // flat the array
    try {
        const response = await axios.post(prepareHref('repo'), payload);
        if (response.data.returncode != 0) {
            showError(response.data.error.message);
            return null;
        }
        // Return code is 0 but there is stderr output: this is a warning message
        if (response.data.error) {
            showWarning(response.data.error.message);
        }
        return response.data.data
    } catch(error) {
        console.log(error);
        showError(error.response ? error.response.data.message : error);
        return null;
    }
}

export function importTheme(theme) {
    // Import an editor theme
    return new Promise((resolve, reject) => {
        let link = document.createElement('link');
        link.onload = () => resolve(true);
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = themesPath + '/' + theme + '.css';
        document.getElementsByTagName('head')[0].appendChild(link);
    });
}

export function initApp(app, target, teleportTarget, csrfTokenParam, themesPathParam) {
    themesPath = themesPathParam;
    // CSRF Token setup
    initCsrfToken(csrfTokenParam);
    // Add VueUniversalModal
    app.use(VueUniversalModal, {
        teleportTarget: teleportTarget
    });
    // Mount app
    vueApp = app.mount(target);
    return vueApp;
}
