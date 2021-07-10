<template>
    <div class='tree-view'>
        <ol class="breadcrumb">
          <li v-for="(item, index) in stack.stack" :index="index" class="breadcrumb-item">
              <a v-if="index != stack.stack.length-1" :href="item.uri" v-on:click.prevent="breadcrumbClicked(index, item)">{{ item.name }}</a>
              <span class="active" v-if="index == stack.stack.length-1">{{ item.name }}</span>
          </li>
          <div class="breadcrumb-buttons">
              <button v-on:click="newAction()" v-if="!isEditorOpen && !isGit" type="button" class="btn btn-default btn-sm">New <i class="fa fa-plus-square" aria-hidden="true"></i></button>
          </div>
        </ol>
        <div class="tree-view-tree-content list-group" v-show="!isEditorOpen">
            <span v-for="item in items" class="list-group-item">
                <a class="name" v-on:click.prevent="click(item)" :href="item.href" :class="'tree-item-' + item.type + ' ' + (item.isSymbolicLink ? 'tree-item-symlink' : '')" >
                    <i :class="'fa ' + item.icon" aria-hidden="true"></i>
                    {{ item.name }}
                </a>
                <span class="mtime">{{ item.mtime }}</span>
                <span class="size">{{ item.formatedSize }}</span>&nbsp;
                <span class="buttons">
                    <a v-if="item.type == 'blob'" class="download" title="Download" :href="item.downloadHref"><i class="fa fa-download" aria-hidden="true"></i></a>
                    <a v-if="(!item.isGit) && (item.type == 'blob' || item.size == 0)" class="trash-o" title="Delete" target="_blank" v-on:click.prevent="deleteAction(item)" :href="item.href"><i class="fa fa-trash-o" aria-hidden="true"></i></a>
                    <a v-if="!item.isGit" class="i-cursor" title="Move/Rename" target="_blank" v-on:click.prevent="moveAction(item)" :href="item.href"><i class="fa fa-i-cursor" aria-hidden="true"></i></a>
                    <a v-if="!item.isGit" class="external-link" title="Open in a new window" target="_blank" :href="item.href"><i class="fa fa-external-link" aria-hidden="true"></i></a>
                </span>
            </span>
        </div>
        <div class="tree-view-blob-content" v-show="isEditorOpen">
            <div class="cm-fullscreen-container cm-flex-container">
                <div class="cm-toolbar cm-flex-child-fixed">
                </div>
                <div class="cm-body cm-flex-child-grow">
                    <textarea rows="30" cols="80" name="editor" style="display: none"></textarea>
                </div>
                <div class="cm-footer cm-flex-child-fixed">
                <button v-on:click="saveAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Save <i class="fa fa-save" aria-hidden="true"></i></button>
                <button v-on:click="saveAsAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Save as...</i></button>
                <button v-on:click="revertAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Revert <i class="fa fa-undo" aria-hidden="true"></i></button>
                <button v-on:click="findAction()" type="button" class="btn btn-default btn-sm">Find <i class="fa fa-search" aria-hidden="true"></i></button>
                <button v-on:click="replaceAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Replace <i class="fa fa-random" aria-hidden="true"></i></button>
                <button v-on:click="formatAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm" v-show="isPython">Format code <i class="fa fa-align-left" aria-hidden="true"></i></button>
                <button v-on:click="settingsAction()" type="button" class="btn btn-default btn-sm" style="float: right">Settings <i class="fa fa-cog" aria-hidden="true"></i></button>
                </div>
            </div>
        </div>
        <!-- Settings modal dialog -->
        <settings :config="config">
        </settings>
    </div>
</template>
<script>
import { BootstrapDialog } from '../bootstrap-dialog';
import { TreeEntry, prepareHref, splitPath, getIcon } from "../commons";
import EditorSettings from './EditorSettings.vue';

export default {
    components: {
        settings: EditorSettings
    },
    props: [ 'stack', 'config', 'isGit' ],
    data: function () {
        return {
            editorPath: null, // path of the file open in editor
            items: [], // tree items (blobs/trees)
            editor: null, // CodeMirror instance
            isEditorOpen: false, // is editor open
            isPython: false, // is editor open on a python file
            readOnly: false,
            codeMirrorOptions: { // code mirror options
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
            }
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
            jQuery.get(prepareHref('files' + path))
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
                          document.location.hash = self.normalize('edit' + path);
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

            jQuery.post(prepareHref('files' + path), data, function(res) {
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
                    document.location.hash = self.normalize('edit' + path);
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
            jQuery.post(prepareHref('format'), data, function(res) {
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
            if (!self.isGit) {
                document.location.hash = self.normalize('files' + (self.stack.last().object || '/'));
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
            self.readOnly = self.isGit;
            var last = self.stack.last();
            if (self.isGit){ // Git hash
                self.editorPath = self.normalize('/~git/' + last.object + '/'+ last.name);
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
            var path = null;
            var last = this.stack.last();
            if (self.isGit) { // git
                path = self.normalize('tree/git/' + last.object);
            } else { // local
                path = self.normalize('tree/files' + (last.object || ''));
                // Update url hash
                document.location.hash = self.normalize('files' + (last.object || ''));
            }
            // Get tree items
            jQuery.get(prepareHref(path), { long: true })
                  .done(function(data) {
                        var blobs = []; // files
                        var trees = []; // directories
                        data.value.forEach(function(part) {
                            var item = new TreeEntry(part, self.isGit, last.object);
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
                            trees.unshift({ type: 'tree', name: '..', isSymbolicLink: false, icon: 'fa-folder', href: '#' });
                        }
                        self.items = trees.concat(blobs);
                  })
                  .fail(function(jqXHR, textStatus, errorThrown) {
                  })
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
        self.editor = CodeMirror.fromTextArea(self.$el.querySelector('textarea'), self.codeMirrorOptions);
        self.editor.save = function() { self.saveAction(); }; // save file command
        // window._editor = self.editor;
    }
}
</script>
