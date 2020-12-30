"use strict"

function TreeEntry(line) {
    var self = this;
    var match = line.match(/^(\d+) (\w+) ([^ #]+)#?(\S+)?\s+(\S*)\t(\S+)/);
    if (match !== undefined) {
        self.mode = parseInt(match[1]);
        self.type = match[2];
        self.object = match[3];
        self.mtime = match[4] ? match[4].replace('T', ' ') : '';
        self.size = parseInt(match[5]);
        self.name = match[6];
        self.local = self.object[0] == '/';
        self.isSymbolicLink = (self.mode & 120000) == 120000; // S_IFLNK
        // href
        if (self.local) { // local file/dir
            if (self.type == 'tree') {
                self.href = '#files' + encodeURI(self.object);
            } else {
                self.href = '#edit' + encodeURI(self.object);
            }
        } else { // git blob
            self.href = '/code_editor/files/~git/' + self.object + '/' + self.name;
        }
        // download href
        if (self.type == 'tree') { // tree
            self.downloadHref = '#';
        } else if (self.local) {  // local file
            self.downloadHref = '/code_editor/files' + self.object;
        } else { // git blob
            self.downloadHref = '/code_editor/files/~git/' + self.object + '/' + self.name;
        }
        // size - https://en.wikipedia.org/wiki/Kilobyte
        if (isNaN(self.size)) {
            self.formatedSize = "";
        } else if (self.size < 10**3) {
            self.formatedSize = self.size.toString() + " B";
        } else if (self.size < 10**6) {
            self.formatedSize = (self.size / 10**3).toFixed(2) + " kB";
        } else if (self.size < 10**9) {
            self.formatedSize = (self.size / 10**6).toFixed(2) + " MB";
        } else {
            self.formatedSize = (self.size / 10**9).toFixed(2) + " GB";
        }
    }
}

Vue.component('tree-view', {
    props: [ 'stack' ],
    data: function () {
        return {
            editorPath: null, // path of the file open in editor
            items: [], // tree items (blobs/trees)
            editor: null, // CodeMirror instance
            isEditorOpen: false, // is editor open
            isPython: false, // is editor open on a python file
            theme: localStorage.getItem('airflow_code_editor_theme') || 'default', // editor theme
            mode: localStorage.getItem('airflow_code_editor_mode') || 'default',  // edit mode (default, vim, etc...)
            themes: themes  // themes list from "themes.js"
        }
    },
    methods: {
        normalize: function(path) {
            if (path[0] != '/') {
                path = '/' + path;
            }
            return path.split(/[/]+/).join('/');
        },
        isNew: function(filename) {
            return /✧$/.test(filename);
        },
        editorLoad: function(path) {
            // Load a file into the editor
            var self = this;
            jQuery.get('/code_editor/files' + path, function(res) {
                // Replace tabs with spaces
                if (self.editor.getMode().name == 'python') {
                    res = res.replace(/\t/g, '    ');
                }
                self.editor.setValue(res);
                self.editor.refresh();
                self.editorPath = path;
                // Update url hash
                if (! path.startsWith('/~git/')) {
                    document.location.hash = 'edit' + path;
                }
            }, 'text');
        },
        editorSave: function(path) {
            // Save editor content
            var self = this;
            var data = {
                data: self.editor.getValue()
            };

            jQuery.post("/code_editor/files" + path, data, function(res) {
                if (res.error) {
                    webui.showError(res.error.message || 'Error saving file');
                } else {
                    // Update editor path and the breadcrumb
                    self.editorPath = path;
                    self.stack.updateStack(path, 'blob');
                    self.editor.openNotification('saved', { duration: 5000 })
                    // Update url hash
                    document.location.hash = 'edit' + path;
                }
            });
        },
        editorSaveAs: function(path) {
            // Show 'Save as...' dialog
            var self = this;
            if (self.isNew(path)) {
                path = path.replace('✧', '');
            }
            BootstrapDialog.show({
                title: 'Save File',
                message: 'File name <input type="text" class="form-control" value="' + path + '" />',
                buttons: [{
                    label: 'Save',
                    action: function(dialogRef) {
                        var newPath = self.normalize(dialogRef.getModalBody().find('input').val().trim());
                        dialogRef.close();
                        self.editorSave(newPath);
                    }
                },{
                    label: 'Cancel',
                    action: function(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
        },
        editorFormat: function() {
            // Format code
            var self = this;
            var data = {
                data: self.editor.getValue()
            };
            jQuery.post("/code_editor/format", data, function(res) {
                if (res.error) {
                    webui.showError(res.error.message);
                } else {
                    self.editor.setValue(res.data);
                    self.editor.refresh();
                }
            });
        },
        setOption: function(option, value) {
            // Set editor option
            var self = this;
            if (self.editor) {
                self.editor.setOption(option, value);
            }
            // Store settings in localStorage
            if (option == 'keyMap') {
                option = 'mode';
            }
            localStorage.setItem('airflow_code_editor_' + option, value);
        },
        setTheme: function(theme) {
            // Set editor theme
            var self = this;
            if (theme == 'default') {
                self.setOption('theme', theme);
            } else {
                var link = document.createElement('link');
                link.onload = function() { self.setOption('theme', theme); };
                var baseUrl = jQuery('link[rel=stylesheet]').filter(function(i, e) { return e.href.match(/gitweb.css/) !== null; })[0].href.split('/gitweb.css')[0];
                link.rel = 'stylesheet';
                link.type = 'text/css';
                link.href = baseUrl + '/theme/' + theme + '.css';
                document.getElementsByTagName('head')[0].appendChild(link);
            }
        },
        updateLocation: function() {
            // Update href hash
            var self = this;
            if (!self.stack.isGit()) {
                document.location.hash = 'files' + (self.stack.last().object || '/');
            }
        },
        click: function(item) {
            // File/directory action
            var self = this;
            if (item.name == '..') {
                self.stack.pop();
            } else {
                self.stack.push(item);
            }
            // Update href hash
            self.updateLocation();
            return false;
        },
        breadcrumbClicked: function(index, item) {
            // Breadcrumb action
            var self = this;
            self.stack.slice(index + 1);
            // Update href hash
            self.updateLocation();
            return false;
        },
        saveAction: function() {
            // Save button action
            var self = this;
            if (self.isNew(self.editorPath)) {
                self.editorSaveAs(self.editorPath);
            } else {
                self.editorSave(self.editorPath);
            }
        },
        saveAsAction: function() {
            // Save as button action
            var self = this;
            self.editorSaveAs(self.editorPath);
        },
        revertAction: function() {
            // Revert button action
            var self = this;
            if (! self.isNew(self.editorPath)) {
                self.editorLoad(self.editorPath);
            }
        },
        findAction: function() {
            // Find button action
            var self = this;
            self.editor.execCommand('find');
        },
        replaceAction: function() {
            // Replace button action
            var self = this;
            self.editor.execCommand('replace');
        },
        formatAction: function() {
            // Format button action
            var self = this;
            self.editorFormat();
        },
        settingsAction: function() {
            // Settings button action
            var self = this;
            jQuery(this.$el.querySelector('.settings-modal')).modal({ backdrop: false, show: true });
        },
        showBlob: function() {
            // Show editor
            var self = this;
            self.isEditorOpen = true;
            var last = self.stack.last();
            if (last.object.startsWith('/')) { // File path
                self.editorPath = last.object;
            } else { // Git hash
                self.editorPath = '/~git/' + last.object + '/'+ last.name;
            }
            // Create CodeMirror instance and set the mode
            var info;
            if (self.isNew(last.name)) {
                info = { 'mode': 'python' };
            } else {
                info = CodeMirror.findModeByFileName(last.name);
            }
            self.editor.setOption('mode', info && info.mode);
            self.isPython = info && info.mode == 'python';
            self.setTheme(self.theme);
            self.setOption('keyMap', self.mode);
            if (info) {
                CodeMirror.autoLoadMode(self.editor, info.mode);
            }
            if (self.isNew(last.name)) {
                // New file
                self.editor.setValue('');
                self.editor.refresh();
            } else {
                // Load the file
                self.editorLoad(self.editorPath);
            }
        },
        showTree: function() {
            // Show tree
            var self = this;
            this.isEditorOpen = false;
            var last = this.stack.last();
            var cmd = self.stack.isGit() ? 'ls-tree' : 'ls-local';
            // Update url hash
            if (cmd == 'ls-local') {
                document.location.hash = 'files' + (last.object || '/');
            }
            webui.git([ cmd, "-l", last.object ], function(data) {
                var blobs = [];
                var trees = [];
                if (self.stack.parent() || (last.object !== undefined && last.object.startsWith('/')) ) {
                    trees.push({ type: 'tree', name: '..', isSymbolicLink: false });
                }
                webui.splitLines(data).forEach(function(line) {
                    var item = new TreeEntry(line);
                    if (item.type == 'tree') {
                        trees.push(item);
                    } else {
                        blobs.push(item);
                    }
                });
                var compare = function(a, b) {
                    return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
                }
                blobs.sort(compare);
                trees.sort(compare);
                self.items = trees.concat(blobs);
            });
        }
    },
    watch: {
        'theme': function(val, preVal) {
            this.setTheme(val);
        },
        'mode': function(val, preVal) {
            this.setOption('keyMap', val);
        },
        'stack.stack': function(val, preVal) {
            var self = this;
            if (self.stack.last().type == 'blob') {
                self.showBlob();
            } else {
                self.showTree();
            }
        }
    },
    mounted: function() {
        this.editor = CodeMirror.fromTextArea(this.$el.querySelector('textarea'), webui.codeMirrorOptions);
    },
    template: jQuery('#tree-view').html()
});


Vue.component('sidebar-section', {
    props: [ 'title', 'section', 'icon', 'items', 'limit' ],
    data: function () {
        return {
            ref: webui.sharedState.object,
            sharedState: webui.sharedState
        }
    },
    methods: {
        selectItem: function(item) {
            var self = this;
            self.sharedState.section = item.id;
            self.sharedState.object = item.object || null;
            if (item.id == "mounts") {
                self.sharedState.stack.updateStack(item.object, 'tree');
            } else if (item.id == "workspace") {
                self.sharedState.workspaceView.update([ 'stage' ]);
            } else { // remote-branches/local-branches/tags
                self.sharedState.historyView.update(item);
            }
        },
        click: function(item) {
            var self = this;
            if (item.object || item.id == "mounts" || item.id == "workspace") { // object is not mandatory for files/workspace
                self.selectItem(item);
            }
            return false;
        },
        clickMore: function() {
            var self = this;
            jQuery(this.$el.querySelector('.modal.fade')).modal({ backdrop: false, show: true });
        }
    },
    template: jQuery('#sidebar-section-template').html()
});

Vue.component('refs', {
    props: [ 'section', 'title', 'items' ],
    data: function () {
        return {
            ref: webui.sharedState.object,
            sharedState: webui.sharedState
        }
    },
    methods: {
        selectRef: function(object) {
            var self = this;
            self.sharedState.section = self.section;
            self.sharedState.object = object;
            self.sharedState.historyView.update({ id: self.section, object: object });
        }
    },
    watch: {
        ref: function(val, preVal) {
            var self = this;
            self.selectRef(val);
        }
    },
    template: jQuery('#refs-template').html()
});

Vue.component('sidebar', {
    data: function () {
        return {
            items: { // sidebar elements for each section
                'mounts': [],
                'local-branches': [],
                'remote-branches': [],
                'tags': [],
                'workspace': []
            },
            sections: [ // sidebar sections (title, id, git command)
                [ "Files", "mounts", [ "mounts" ]],
                [ "Local Branches", "local-branches", [ "branch" ]],
                [ "Remote Branches", "remote-branches", [ "branch", "--remotes" ]],
                [ "Tags", "tags", [ "tag" ]],
            ],
            sharedState: webui.sharedState
        }
    },
    methods: {
        fetchSection: function(title, section, gitCommand) {
            var self = this;
            return new Promise(function(resolve, reject) {
                webui.git(gitCommand, function(data) {
                    var refs = webui.splitLines(data);
                    var items = [];
                    if (refs.length > 0) {
                        // Prepare items
                        items = refs.map(function(ref) {
                            var item = {
                                id: section,
                                object: null,
                                name: null,
                                class: null
                            }
                            item.name = ref.trim().split(' ->')[0]; // Strip "->> ..."
                            if (item.name[2] == '(' && item.name[item.name.length - 1] == ')') { // "(detached from ...)"
                                item.name = item.name.substring(item.name.lastIndexOf(' ') + 1, item.name.length - 1)
                            }
                            if (item.name[0] == '*') { // Current branch
                                item.name = item.name.substring(1).trim(); // remove "* "
                                item.class = "branch-current";
                            }
                            if (section == 'mounts') {
                                item.object = '/~' + item.name;
                            } else {
                                item.object = item.name;
                            }
                            return item;
                        });
                        // Sort
                        items = items.sort(function(a, b) {
                            if (section != 'local-branches' && section != 'mounts') {
                                return -a.object.localeCompare(b.object);
                            } else {
                                return a.object.localeCompare(b.object);
                            }
                        });
                    }
                    self.items[section] = items;
                    resolve(section);
                });
            });
        },
        initViews: function() {
            var self = this;
            return new Promise(function(resolve, reject) {
                self.sharedState.historyView = new webui.HistoryView();
                self.sharedState.workspaceView = new webui.WorkspaceView();
                resolve(true);
            });
        },
        fetchSections: function() {
            var self = this;
            return Promise.all(self.sections.map(function (args) {
                return self.fetchSection(args[0], args[1], args[2]);
            }));
        },
        parseLocationHash: function() {
            var self = this;
            return new Promise(function(resolve, reject) {
                var match = /#?([a-z-]+)(\/(.*))?/.exec(document.location.hash);
                var section = match !== null ? match[1] : 'files';
                var object = match !== null ? match[3] : null;

                if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                    self.sharedState.section = section;
                    self.sharedState.object = object;
                    self.sharedState.historyView.update({ id: section, object: object });

                } else if (section == 'workspace') {
                    self.sharedState.section = section;
                    self.sharedState.object = null;
                    self.sharedState.workspaceView.update([ 'stage' ]);

                } else if (section == 'edit') {
                    self.sharedState.section = 'mounts';
                    self.sharedState.stack.updateStack(object, 'blob');

                } else { // files
                    self.sharedState.section = 'mounts';
                    self.sharedState.stack.updateStack(object, 'tree');
                }
                jQuery('#global-container').show();
                resolve(true);
            });
        }
    },
    created: function() {
    },
    mounted: function() {
        var self = this;
        self.initViews()
            .then(self.fetchSections)
            .then(self.parseLocationHash);
    },
    template: jQuery('#sidebar-template').html()
});
