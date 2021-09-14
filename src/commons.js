import { BootstrapDialog } from './bootstrap-dialog';
import axios from 'axios';

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

export function showError(message) {
    BootstrapDialog.alert({
        title: 'Error',
        type: BootstrapDialog.TYPE_DANGER,
        message: message,
    });
}

export function showWarning(message) {
    BootstrapDialog.alert({
        title: 'Error',
        type: BootstrapDialog.TYPE_WARNING,
        message: message,
    });
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

export function getIcon(type, path) {
    if (type == 'tree') {
        return 'fa-folder';
    } else {
        let extension = (path.substring(path.lastIndexOf('.') + 1) || '').toLowerCase();
        if ([ 'zip', 'tar', 'tgz', 'tbz2', 'txz', 'z', 'gz', 'xz', 'bz', 'bz2', '7z', 'lz' ].indexOf(extension) != -1) {
            return 'fa-file-archive-o';
        } else if ([ 'jpg', 'jpeg', 'png', 'svg', 'git', 'bmp', 'ief', 'tif', 'tiff', 'ico' ].indexOf(extension) != -1) {
            return 'fa-file-image-o';
        } else if ([ 'py' ].indexOf(extension) != -1) {
            return 'fa-file-text-o';
        }
        return 'fa-file-o';
    }
}

export function TreeEntry(data, isGit, path) {
    let self = this;
    if (data) {
        self.mode = data.mode;
        self.isGit = isGit;
        self.type = data.leaf ? 'blob' : 'tree';
        if (self.isGit) {
            self.object = data.id;
        } else {
            self.object = (path || '') + '/' + data.id;
        }
        self.mtime = data.mtime ? data.mtime.replace('T', ' ') : '';
        self.size = data.size;
        self.name = data.label || data.id;
        self.isSymbolicLink = (self.mode & 120000) == 120000; // S_IFLNK
        self.icon = getIcon(self.type, self.name);
        // href
        if (self.isGit) { // git blob
            self.href = prepareHref('files/~git/' + self.object + '/' + self.name);
        } else { // local file/dir
            if (self.type == 'tree') {
                self.href = '#files' + encodeURI(self.object);
            } else {
                self.href = '#edit' + encodeURI(self.object);
            }
        }
        // download href
        if (self.type == 'tree') { // tree
            self.downloadHref = '#';
        } else if (self.isGit) { // git blob
            self.downloadHref = prepareHref('files/~git/' + self.object + '/' + self.name);
        } else { // local file
            self.downloadHref = prepareHref('files/' + self.object);
        }
        // size - https://en.wikipedia.org/wiki/Kilobyte
        if (isNaN(self.size)) {
            self.formattedSize = "";
        } else if (self.type == 'tree') { // tree - number of files in the folder
            if (self.size == 1) {
                self.formattedSize = self.size + ' item';
            } else {
                self.formattedSize = self.size + ' items';
            }
        } else if (self.size < 10**3) {
            self.formattedSize = self.size.toString() + " B";
        } else if (self.size < 10**6) {
            self.formattedSize = (self.size / 10**3).toFixed(2) + " kB";
        } else if (self.size < 10**9) {
            self.formattedSize = (self.size / 10**6).toFixed(2) + " MB";
        } else {
            self.formattedSize = (self.size / 10**9).toFixed(2) + " GB";
        }
    }
}


export function Stack() {
    let self = this;

    self.stack = [ { name: 'root', object: undefined } ],

    self.updateStack = function(path, type) {
        // path: absolute path (local file) or ref/path (git)
        // type: last item type (tree or blob)
        let stack = [];
        let fullPath = null;
        if (path == '/' || !path) {
            path = '';
        }
        path.split('/').forEach(function(part, index) {
            if (index === 0 && !part) {
                stack.push({ name: 'root', object: undefined });
                fullPath = '';
            } else {
                if (fullPath === null) {
                    fullPath = part;
                    part = 'root';
                } else {
                    fullPath += '/' + part;
                }
                if (part[0] == '~') {
                    part = part.substring(1);
                }
                stack.push({
                    name: part,
                    object: fullPath,
                    uri: encodeURI((fullPath !== undefined && fullPath.startsWith('/')) ? ('#files' + fullPath) : null),
                    type: 'tree'
                });
            }
        });
        if (type == 'blob') {
            stack[stack.length - 1].type = 'blob';
        }
        self.stack = stack;
    }

    self.last = function() {
        // Return last stack element
        return self.stack[self.stack.length - 1];
    }

    self.parent = function() {
        // Return stack - 2 element
        return self.stack.length > 1 ? self.stack[self.stack.length - 2] : undefined;
    }

    self.isGit = function() {
        // Return true if last is a git ref
        return (self.last().object !== undefined && !self.last().object.startsWith('/'));
    }

    self.pop = function() {
        return self.stack.pop();
    }

    self.push = function(item) {
        return self.stack.push(item);
    }

    self.slice = function(index) {
        self.stack = self.stack.slice(0, index);
    }

};

function refreshCsrfToken() {
    // Refresh CSRF Token
    axios.get(prepareHref('ping'))
         .then((response) => {
              csrfToken = response.data.value;
              axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
              setTimeout(refreshCsrfToken, CSRF_REFRESH);
         })
         .catch((error) => setTimeout(refreshCsrfToken, CSRF_REFRESH));
}

export function initCsrfToken(csrfTokenParam) {
    csrfToken = csrfTokenParam;
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    setTimeout(refreshCsrfToken, CSRF_REFRESH);
}

export function git(args, callback) {
    const payload = { args: [].concat.apply([], args) };  // flat the array
    axios.post(prepareHref('repo'), payload)
         .then((response) => {
            window.rrr = response;
            const messageStartIndex = response.data.length - parseInt(response.headers['x-git-stderr-length']);
            const rcode = parseInt(response.headers['x-git-return-code']);
            const output = response.data.substring(0, messageStartIndex);
            const message = response.data.substring(messageStartIndex);
            if (rcode === 0) {
                if (callback) {
                    callback(output);
                }
                // Return code is 0 but there is stderr output: this is a warning message
                if (message.length > 0) {
                    showWarning(message);
                }
            } else {
                showError(message);
            }
         })
         .catch((error) => {
            console.log(error);
            showError(error.response ? error.response.data.message : error);
         });
}
