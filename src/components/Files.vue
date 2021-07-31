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
        <div class="tree-view-tree-content list-group"
             @dragenter.stop.prevent="isDragEnter = true"
             @dragover.stop.prevent="() => {}"
             @dragleave.stop.prevent="isDragEnter = false"
             @drop.stop.prevent="handleDrop"
             v-show="!isEditorOpen">
            <div v-for="item in items" class="list-group-item">
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
            </div>
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
import { TreeEntry, prepareHref, showError, git } from "../commons";
import EditorSettings from './EditorSettings.vue';

export default {
    components: {
        settings: EditorSettings
    },
    props: [ 'stack', 'config', 'isGit' ],
    data() {
        return {
            editorPath: null, // path of the file open in editor
            items: [], // tree items (blobs/trees)
            editor: null, // CodeMirror instance
            isEditorOpen: false, // is editor open
            isPython: false, // is editor open on a python file
            readOnly: false,
            isDragEnter: false,
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
        normalize(path) {
            if (path[0] != '/') {
                path = '/' + path;
            }
            return path.split(/[/]+/).join('/');
        },
        basename(path) {
            return path.substring(path.lastIndexOf('/') + 1);
        },
        isNew(filename) {
            return /✧$/.test(filename);
        },
        editorLoad(path) {
            // Load a file into the editor
            const self = this;
            jQuery.get(prepareHref('files' + path))
                  .done((data) => {
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
                  .fail((jqXHR, textStatus, errorThrown) => {
                      self.editor.setValue('');
                      self.editor.refresh();
                      self.editorPath = path;
                      self.editor.openNotification('file not found', { duration: 5000 })
                  });
        },
        editorSave(path) {
            // Save editor content
            const self = this;
            let data = {
                data: self.editor.getValue()
            };

            jQuery.post(prepareHref('files' + path), data, (res) => {
                if (res.error) {
                    showError(res.error.message || 'Error saving file');
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
        editorSaveAs(path) {
            // Show 'Save as...' dialog
            const self = this;
            if (self.isNew(path)) {
                path = path.replace('✧', '');
            }
            BootstrapDialog.show({
                title: 'Save File',
                message: 'File name <input type="text" class="form-control" value="' + path + '" />',
                buttons: [{
                    label: 'Save',
                    action(dialogRef) {
                        const newPath = self.normalize(dialogRef.getModalBody().find('input').val().trim());
                        dialogRef.close();
                        self.editorSave(newPath);
                    }
                },{
                    label: 'Cancel',
                    action(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
        },
        editorFormat() {
            // Format code
            const self = this;
            let data = {
                data: self.editor.getValue()
            };
            jQuery.post(prepareHref('format'), data, (res) => {
                if (res.error) {
                    showError(res.error.message);
                } else {
                    self.editor.setValue(res.data);
                    self.editor.refresh();
                }
            });
        },
        setOption(option, value) {
            // Set editor option
            const self = this;
            if (self.editor) {
                self.editor.setOption(option, value);
            }
            // Store settings in localStorage
            if (option == 'keyMap') {
                option = 'mode';
            }
            localStorage.setItem('airflow_code_editor_' + option, value);
        },
        setTheme(theme) {
            // Set editor theme
            const self = this;
            if (theme == 'default') {
                self.setOption('theme', theme);
            } else {
                let link = document.createElement('link');
                link.onload = () => self.setOption('theme', theme);
                let baseUrl = jQuery('link[rel=stylesheet]').filter((i, e) => e.href.match(/gitweb.css/) !== null)[0].href.split('/gitweb.css')[0];
                link.rel = 'stylesheet';
                link.type = 'text/css';
                link.href = baseUrl + '/theme/' + theme + '.css';
                document.getElementsByTagName('head')[0].appendChild(link);
            }
        },
        updateLocation() {
            // Update href hash
            const self = this;
            if (!self.isGit) {
                document.location.hash = self.normalize('files' + (self.stack.last().object || '/'));
            }
        },
        click(item) {
            // File/directory action
            const self = this;
            if (item.name == '..') {
                self.stack.pop();
            } else {
                self.stack.push(item);
            }
            // Update href hash
            self.updateLocation();
            return false;
        },
        breadcrumbClicked(index, item) {
            // Breadcrumb action
            const self = this;
            self.stack.slice(index + 1);
            // Update href hash
            self.updateLocation();
            return false;
        },
        moveAction(item) {
            // Delete a file
            const self = this;
            BootstrapDialog.show({
                title: 'Move/Rename File',
                message: 'Destination <input type="text" class="form-control" value="' + item.object + '" />',
                buttons: [{
                    label: 'Ok',
                    action(dialogRef) {
                        let target = dialogRef.getModalBody().find('input').val().trim();
                        git([ 'mv-local', item.object, target ], function(data) {
                            self.refresh();
                        });
                        dialogRef.close();
                    }
                },{
                    label: 'Cancel',
                    action(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
            return false;
        },
        deleteAction(item) {
            // Delete a file
            const self = this;
            BootstrapDialog.show({
                title: 'Confirm Delete',
                message: 'Are you sure you want to delete ' + item.name + ' ?',
                buttons: [{
                    label: 'Delete',
                    cssClass: 'btn-danger',
                    action(dialogRef) {
                        git([ 'rm-local', item.object ], function(data) {
                            self.refresh();
                        });
                        dialogRef.close();
                    }
                },{
                    label: 'Cancel',
                    action(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
            return false;
        },
        saveAction() {
            // Save button action
            const self = this;
            if (self.isNew(self.editorPath)) {
                self.editorSaveAs(self.editorPath);
            } else {
                self.editorSave(self.editorPath);
            }
        },
        saveAsAction() {
            // Save as button action
            const self = this;
            self.editorSaveAs(self.editorPath);
        },
        revertAction() {
            // Revert button action
            const self = this;
            if (! self.isNew(self.editorPath)) {
                self.editorLoad(self.editorPath);
            }
        },
        findAction() {
            // Find button action
            const self = this;
            self.editor.execCommand('find');
        },
        replaceAction() {
            // Replace button action
            const self = this;
            self.editor.execCommand('replace');
        },
        formatAction() {
            // Format button action
            const self = this;
            self.editorFormat();
        },
        settingsAction() {
            // Settings button action
            const self = this;
            jQuery(this.$el.querySelector('.settings-modal')).modal({ backdrop: false, show: true });
        },
        newAction() {
            // New file button action
            const self = this;
            let item = { name: '✧', type: 'blob', object: (self.stack.last().object || '') + '/✧' };
            self.stack.push(item);
        },
        showBlob() {
            // Show file in editor
            const self = this;
            self.isEditorOpen = true;
            self.readOnly = self.isGit;
            let last = self.stack.last();
            if (self.isGit){ // Git hash
                self.editorPath = self.normalize('/~git/' + last.object + '/'+ last.name);
            } else { // File path
                self.editorPath = last.object;
            }
            // Create CodeMirror instance and set the mode
            let info;
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
        refresh() {
            // Update tree view
            const self = this;
            this.isEditorOpen = false;
            let path = null;
            let last = this.stack.last();
            if (self.isGit) { // git
                path = self.normalize('tree/git/' + last.object);
            } else { // local
                path = self.normalize('tree/files' + (last.object || ''));
                // Update url hash
                document.location.hash = self.normalize('files' + (last.object || ''));
            }
            // Get tree items
            jQuery.get(prepareHref(path), { long: true })
                  .done((data) => {
                        let blobs = []; // files
                        let trees = []; // directories
                        data.value.forEach((part) => {
                            let item = new TreeEntry(part, self.isGit, last.object);
                            if (item.type == 'tree') {
                                trees.push(item);
                            } else {
                                blobs.push(item);
                            }
                        });
                        // Sort files and directories
                        const compare = (a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase());
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
        },
        handleDrop($event) {
            this.isDragEnter = false;
            this.preprocessFiles($event.dataTransfer.files);
        },
        preprocessFiles(files) {
            // Upload files
            const self = this;
            if (!self.isGit) {
                files.forEach((file) => {
                    file.text().then((text) => {
                        // Prepare filename
                        const filename = self.normalize((self.stack.last().object || '') + '/' + self.basename(file.name));
                        // Prepare payload
                        const payload = {
                            data: text,
                            type: file.type
                        };
                        // Upload file
                        jQuery.post(prepareHref('files' + filename), payload, (res) => {
                            console.log(res);
                            self.refresh();
                        });
                    });
                });
            }
        },
    },
    watch: {
        'config.theme': function(val, preVal) {
            this.setTheme(val);
        },
        'config.mode': function(val, preVal) {
            this.setOption('keyMap', val);
        },
        'stack.stack': function(val, preVal) {
            const self = this;
            if (self.stack.last().type == 'blob') {
                self.showBlob();
            } else {
                self.refresh();
            }
        }
    },
    mounted() {
        const self = this;
        self.editor = CodeMirror.fromTextArea(self.$el.querySelector('textarea'), self.codeMirrorOptions);
        self.editor.save = () => self.saveAction(); // save file command
        // window._editor = self.editor;
    }
}
</script>
