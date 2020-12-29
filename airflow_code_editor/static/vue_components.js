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
        updateStack: function(path) {
            var stack = [];
            var fullPath = null;
            if (path == '/') {
                path = '';
            }
            path.split('/').forEach(function(part, index) {
                if (index === 0) {
                    stack.push({ name: 'root', object: undefined });
                    fullPath = '';
                } else {
                    fullPath += '/' + part;
                    if (part[0] == '~') {
                        part = part.substring(1);
                    }
                    stack.push({
                        name: part,
                        object: fullPath,
                        uri: encodeURI((fullPath !== undefined && fullPath.startsWith('/')) ? ('#files' + fullPath) : fullPath)
                    });
                }
            });
            this.stack = stack;
        },
        normalize: function(path) {
            if (path[0] != '/') {
                path = '/' + path;
            }
            return path.split(/[/]+/).join('/');
        },
        isNew: function(filename) {
            return /✧$/.test(filename);
        },
        isGit: function(treeRef) {
            // Return true if treeRef is git ref
            return (treeRef !== undefined && !treeRef.startsWith('/'));
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
                    self.updateStack(path);
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
            var last = self.stack[self.stack.length - 1];
            if (!self.isGit(last.object)) {
                document.location.hash = 'files' + (last.object || '/');
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
            self.stack = self.stack.slice(0, index + 1);
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
            var object = self.stack[self.stack.length - 1].object;
            var filename = self.stack[self.stack.length - 1].name;
            if (object.startsWith('/')) { // File path
                self.editorPath = object;
            } else { // Git hash
                self.editorPath = '/~git/' + object + '/'+ filename;
            }
            // Create CodeMirror instance and set the mode
            var info;
            if (self.isNew(filename)) {
                info = { 'mode': 'python' };
            } else {
                info = CodeMirror.findModeByFileName(filename);
            }
            self.editor.setOption('mode', info && info.mode);
            self.isPython = info && info.mode == 'python';
            self.setTheme(self.theme);
            self.setOption('keyMap', self.mode);
            if (info) {
                CodeMirror.autoLoadMode(self.editor, info.mode);
            }
            if (self.isNew(filename)) {
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
            var treeRef = this.stack[this.stack.length - 1].object;
            var parentTreeRef = this.stack.length > 1 ? this.stack[this.stack.length - 2].object : undefined;
            var cmd = self.isGit(treeRef) ? 'ls-tree' : 'ls-local';
            // Update url hash
            if (cmd == 'ls-local') {
                document.location.hash = 'files' + (treeRef || '/');
            }
            webui.git([ cmd, "-l", treeRef ], function(data) {
                var blobs = [];
                var trees = [];
                if (parentTreeRef || (treeRef !== undefined && treeRef.startsWith('/')) ) {
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
        'stack': function(val, preVal) {
            var self = this;
            if (self.stack[self.stack.length - 1].type == 'blob') {
                self.showBlob();
            } else {
                self.showTree();
            }
        }
    },
    created: function() {
        // this.updateStack('/');
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
            ref: webui.sharedState.refName,
            sharedState: webui.sharedState
        }
    },
    methods: {
        selectItem: function(item) {
            var self = this;
            self.sharedState.section = item.id;
            self.sharedState.refName = item.refName || null;
            if (item.id == "mounts") {
                self.sharedState.section = item.id;
                if (item.refName) {
                    self.sharedState.stack = [
                    { name: 'root', object: undefined },
                    { name: item.refName, object: '/~' + item.refName }
                ];
                } else {
                    self.sharedState.stack = [
                        { name: 'root', object: undefined }
                    ];
                }
            } else if (item.id == "workspace") {
                self.sharedState.workspaceView.update([ "stage" ]);
            } else { // remote-branches/local-branches/tags
                self.sharedState.historyView.update(item);
            }
        },
        click: function(item) {
            var self = this;
            if (item.refName || item.id == "mounts" || item.id == "workspace") { // refName is not mandatory for files/workspace
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
            ref: webui.sharedState.refName,
            sharedState: webui.sharedState
        }
    },
    methods: {
        selectRef: function(refName) {
            var self = this;
            self.sharedState.section = self.section;
            self.sharedState.refName = refName;
            self.sharedState.historyView.update({ id: self.section, refName: refName });
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
        fetchSection: function(title, id, gitCommand) {
            var self = this;
            return new Promise(function(resolve, reject) {
                webui.git(gitCommand, function(data) {
                    var refs = webui.splitLines(data);
                    if (id == "remote-branches") {
                        refs = refs.map(function(ref) {
                            var end = ref.lastIndexOf(" -> ");
                            if (end == -1) {
                                return ref.substr(2);
                            } else {
                                return ref.substring(2, end);
                            }
                        });
                    }
                    var items = [];
                    if (refs.length > 0) {
                        refs = refs.sort(function(a, b) {
                            if (id != "local-branches") {
                                return -a.localeCompare(b);
                            } else if (a[0] == "*") {
                                return -1;
                            } else if (b[0] == "*") {
                                return 1;
                            } else {
                                return a.localeCompare(b);
                            }
                        });

                        if (id == "mounts") {
                            refs = refs.reverse();
                        }
                        for (var i = 0; i < refs.length; ++i) {
                            var ref = refs[i];
                            if (ref[2] == '(' && ref[ref.length - 1] == ')') {
                                // This is a '(detached from XXXXXX)'
                                var newref = ref.substring(ref.lastIndexOf(' ') + 1, ref.length - 1)
                                if (ref[0] == '*') {
                                    ref = '* ' + newref;
                                } else {
                                    ref = '  ' + newref;
                                }
                            }
                            var item = { id: id, refName: ref };
                            if (id == "local-branches") {
                                item.refName = ref.substr(2);
                                if (ref[0] == "*") {
                                    item.class = "branch-current";
                                }
                            }
                            items.push(item);
                        }
                    }
                    self.items[id] = items;
                    resolve(id);
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
                var refName = match !== null ? match[3] : null;

                if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                    self.sharedState.section = section;
                    self.sharedState.refName = refName;
                    self.sharedState.historyView.update({ id: section, refName: refName });

                } else if (section == 'workspace') {
                    self.sharedState.section = section;
                    self.sharedState.refName = null;
                    self.sharedState.workspaceView.update([ "stage" ]);

                } else { // files/edit
                    self.sharedState.section = 'mounts';
                    if (refName) {
                        var name = refName;
                        if (name[0] == '~') {
                            name = name.substring(1);
                        }
                        self.sharedState.stack = [
                            { name: 'root', object: undefined },
                            { name: name, object: '/' + refName, type: section == 'edit' ? 'blob' : 'tree' }
                        ];
                    } else {
                        self.sharedState.stack = [
                            { name: 'root', object: undefined }
                        ];
                    }
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
