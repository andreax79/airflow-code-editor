(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("./gitweb"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../gitweb"], mod);
  else // Plain browser env
    mod(webui);
})(function(webui) {
    "use strict";

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
            if (self.type == 'tree') { // tree
                self.formatedSize = self.size;
            } else if (isNaN(self.size)) {
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


    function Stack() {
        var self = this;

        self.stack = [ { name: 'root', object: undefined } ],

        self.updateStack = function(path, type) {
            // path: absolute path (local file) or ref/path (git)
            // type: last item type (tree or blob)
            var stack = [];
            var fullPath = null;
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


    function EditorConfig() {
        // Editor configuration
        var self = this;
        self.theme = localStorage.getItem('airflow_code_editor_theme') || 'default'; // editor theme
        self.mode = localStorage.getItem('airflow_code_editor_mode') || 'default';  // edit mode (default, vim, etc...)
        self.themes = themes;  // themes list from "themes.js"
        self.codeMirrorOptions = { // code mirror options
            lineNumbers: true,
            foldGutter: true,
            tabSize: 4,
            indentUnit: 4,
            indentWithTabs: false,
            gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
            extraKeys: {
                "Alt-F": "findPersistent",
                "Tab": "indentMore"
            }
        };
    }


    Vue.component('tree-view', {
        props: [ 'stack', 'config' ],
        data: function () {
            return {
                editorPath: null, // path of the file open in editor
                items: [], // tree items (blobs/trees)
                editor: null, // CodeMirror instance
                isEditorOpen: false, // is editor open
                isPython: false, // is editor open on a python file
                readOnly: false
            }
        },
        computed: {
            isGit: function () {
                var self = this;
                return self.stack.isGit();
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
                jQuery.get('/code_editor/files' + path)
                      .done(function(data) {
                          // Replace tabs with spaces
                          if (self.editor.getMode().name == 'python') {
                              data = data.replace(/\t/g, '    ');
                          }
                          self.editor.setValue(data);
                          self.editor.refresh();
                          self.editorPath = path;
                          // Update url hash
                          if (! path.startsWith('/~git/')) {
                              document.location.hash = 'edit' + path;
                          }
                      })
                      .fail(function(jqXHR, textStatus, errorThrown) {
                          self.editor.setValue('');
                          self.editor.refresh();
                          self.editorPath = path;
                          self.editor.openNotification('file not found', { duration: 5000 })
                      });
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
                        if (path != self.editorPath) {
                            self.editorPath = path;
                            self.stack.updateStack(path, 'blob');
                        }
                        self.editor.openNotification('file saved', { duration: 5000 })
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
            moveAction: function(item) {
                // Delete a file
                var self = this;
                BootstrapDialog.show({
                    title: 'Move/Rename File',
                    message: 'Destination <input type="text" class="form-control" value="' + item.object + '" />',
                    buttons: [{
                        label: 'Ok',
                        action: function(dialogRef) {
                            var target = dialogRef.getModalBody().find('input').val().trim();
                            console.log(target);
                            webui.git([ 'mv-local', item.object, target ], function(data) {
                                self.refresh();
                            });
                            dialogRef.close();
                        }
                    },{
                        label: 'Cancel',
                        action: function(dialogRef) {
                            dialogRef.close();
                        }
                    }]
                });
                return false;
            },
            deleteAction: function(item) {
                // Delete a file
                var self = this;
                BootstrapDialog.show({
                    title: 'Confirm Delete',
                    message: 'Are you sure you want to delete ' + item.name + ' ?',
                    buttons: [{
                        label: 'Delete',
                        cssClass: 'btn-danger',
                        action: function(dialogRef) {
                            webui.git([ 'rm-local', item.object ], function(data) {
                                self.refresh();
                            });
                            dialogRef.close();
                        }
                    },{
                        label: 'Cancel',
                        action: function(dialogRef) {
                            dialogRef.close();
                        }
                    }]
                });
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
            newAction: function() {
                // New file button action
                var self = this;
                var item = { name: '✧', type: 'blob', object: (self.stack.last().object || '') + '/✧' };
                self.stack.push(item);
            },
            showBlob: function() {
                // Show file in editor
                var self = this;
                self.isEditorOpen = true;
                self.readOnly = self.stack.isGit();
                var last = self.stack.last();
                if (self.stack.isGit()){ // Git hash
                    self.editorPath = '/~git/' + last.object + '/'+ last.name;
                } else { // File path
                    self.editorPath = last.object;
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
                self.setTheme(self.config.theme);
                self.setOption('keyMap', self.config.mode);
                self.setOption('readOnly', self.readOnly);
                if (info) {
                    CodeMirror.autoLoadMode(self.editor, info.mode);
                }
                if (self.isNew(last.name)) {
                    // New file
                    self.editor.setValue('');
                    setTimeout(function(){
                        self.editor.refresh();
                    }, 100);
                } else {
                    // Load the file
                    self.editorLoad(self.editorPath);
                }
            },
            refresh: function() {
                // Update tree view
                var self = this;
                this.isEditorOpen = false;
                var last = this.stack.last();
                var cmd = self.stack.isGit() ? 'ls-tree' : 'ls-local';
                // Update url hash
                if (cmd == 'ls-local') {
                    document.location.hash = 'files' + (last.object || '/');
                }
                webui.git([ cmd, "-l", last.object ], function(data) {
                    var blobs = []; // files
                    var trees = []; // directories
                    webui.splitLines(data).forEach(function(line) {
                        var item = new TreeEntry(line);
                        if (item.type == 'tree') {
                            trees.push(item);
                        } else {
                            blobs.push(item);
                        }
                    });
                    // Sort files and directories
                    var compare = function(a, b) {
                        return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
                    }
                    blobs.sort(compare);
                    trees.sort(compare);
                    // Add link to parent directory on top
                    if (self.stack.parent() || (last.object !== undefined && last.object.startsWith('/')) ) {
                        trees.unshift({ type: 'tree', name: '..', isSymbolicLink: false });
                    }
                    self.items = trees.concat(blobs);
                });
            }
        },
        watch: {
            'config.theme': function(val, preVal) {
                this.setTheme(val);
            },
            'config.mode': function(val, preVal) {
                this.setOption('keyMap', val);
            },
            'stack.stack': function(val, preVal) {
                var self = this;
                if (self.stack.last().type == 'blob') {
                    self.showBlob();
                } else {
                    self.refresh();
                }
            }
        },
        mounted: function() {
            var self = this;
            self.editor = CodeMirror.fromTextArea(self.$el.querySelector('textarea'), self.config.codeMirrorOptions);
            self.editor.save = function() { self.saveAction(); }; // save file command
            // window._editor = self.editor;
        },
        template: jQuery('#tree-view').html()
    });


    Vue.component('sidebar-section', {
        props: [ 'title', 'section', 'icon', 'items', 'limit', 'stack', 'historyView', 'workspaceView', 'current' ],
        computed: {
            cssClass: function () {
                var self = this;
                return {
                    'active': (self.section == 'workspace' && self.current.section == 'workspace') || (self.section == 'mounts' && self.current.section == 'mounts' && !self.current.object),
                    'clickable': (self.section == 'workspace' || self.section == 'mounts')
                }
            }
        },
        methods: {
            selectItem: function(item) {
                var self = this;
                self.current.section = item.id;
                self.current.object = item.object || null;
                if (item.id == "mounts") {
                    self.stack.updateStack(item.object, 'tree');
                } else if (item.id == "workspace") {
                    self.workspaceView.update([ 'stage' ]);
                } else { // remote-branches/local-branches/tags
                    self.historyView.update(item);
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
        props: [ 'section', 'title', 'items', 'historyView', 'current' ],
        data: function () {
            var self = this;
            return {
                ref: self.current.object,
            }
        },
        methods: {
            selectRef: function(object) {
                // Change current section/ref
                var self = this;
                self.current.section = self.section;
                self.current.object = object;
                self.historyView.update({ id: self.section, name: object });
            }
        },
        watch: {
            'current.object': function(val, preVal) {
                // Update ref when the current object is changed outside this component
                var self = this;
                self.ref = self.current.object;
            }
        },
        template: jQuery('#refs-template').html()
    });


    Vue.component('sidebar', {
        props: [ 'stack', 'current', 'historyView', 'workspaceView' ],
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
            }
        },
        methods: {
            fetchSection: function(title, section, gitCommand) {
                // Fetch a single sidebar section
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
            fetchSections: function() {
                // Fetch sidebar sections
                var self = this;
                return Promise.all(self.sections.map(function (args) {
                    return self.fetchSection(args[0], args[1], args[2]);
                }));
            },
            parseURIFragment: function() {
                // Change the active section according to the uri fragment (hash)
                var self = this;
                return new Promise(function(resolve, reject) {
                    var match = /#?([a-z-]+)(\/(.*))?/.exec(document.location.hash);
                    var section = match !== null ? match[1] : 'files';
                    var object = match !== null ? match[3] : null;

                    if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                        self.current.section = section;
                        self.current.object = object;
                        self.historyView.update({ id: section, name: object });

                    } else if (section == 'workspace') {
                        self.current.section = section;
                        self.current.object = null;
                        self.workspaceView.update([ 'stage' ]);

                    } else if (section == 'edit' && object) {
                        self.current.section = 'mounts';
                        self.current.object = '/' + object.split('/')[0];
                        self.stack.updateStack('/' + object, 'blob');

                    } else { // files
                        self.current.section = 'mounts';
                        if (object) {
                            self.current.object = '/' + object.split('/')[0];
                            self.stack.updateStack('/' + object, 'tree');
                        } else {
                            self.current.object = null;
                            self.stack.updateStack('/', 'tree');
                        }
                    }
                    resolve(true);
                });
            },
            showContainer: function() {
                // Show global container
                var self = this;
                jQuery('#global-container').show();
                return(Promise.resolve(true));
            },
        },
        mounted: function() {
            // Init
            var self = this;
            self.fetchSections()
                .then(self.parseURIFragment)
                .then(self.showContainer);
        },
        template: jQuery('#sidebar-template').html()
    });


    webui.init = function(csrfToken) {
        // Init
        CodeMirror.modeURL = '/static/code_editor/mode/%N/%N.js';
        // Disable animation
        BootstrapDialog.configDefaultOptions({ animate: false });
        // CSRF Token setup
        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
        // Append global container to body
        jQuery('#global-container').appendTo(jQuery("body"));
        // Init app
        webui.app = new Vue({
            el: '#global-container',
            data:{
                current: {
                    section: null, // current sidebar section (mounts, werkspace, ...)
                    object: null, // current sidebar object
                },
                stack: new Stack(), // files stack
                historyStack: new Stack(), // history view files stack
                editorConfig: new EditorConfig(), // editor config
                historyView: null,
                workspaceView: null,
            },
            methods: {
                initViews: function() {
                    // Init views
                    var self = this;
                    return new Promise(function(resolve, reject) {
                        self.historyView = new webui.HistoryView(self.historyStack);
                        self.workspaceView = new webui.WorkspaceView();
                        resolve(true);
                    });
                },
            },
            mounted: function() {
                // Init
                var self = this;
                self.initViews();
            }

        });
    }

});
