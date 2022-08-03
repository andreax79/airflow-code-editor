<template>
    <div class="tree-view">
        <ol class="breadcrumb">
            <breadcrumb :stack="stack" :is-git="false"></breadcrumb>
        </ol>

        <div class="tree-view-blob-content">
            <div class="cm-fullscreen-container cm-flex-container">
                <div class="cm-toolbar cm-flex-child-fixed">
                </div>
                <div class="cm-body cm-flex-child-grow">
                    <textarea rows="30" cols="80" name="editor" style="display: none"></textarea>
                </div>
                <div class="cm-footer cm-flex-child-fixed">
                    <button v-on:click="saveAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Save <i class="fa fa-save" aria-hidden="true"></i></button>
                    <button v-on:click="saveAsAction()" v-if="!readOnly" type="button" class="btn btn-default btn-sm">Save as...</button>
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
import axios from 'axios';
import { defineComponent, markRaw } from 'vue';
import { BootstrapDialog } from '../bootstrap-dialog';
import { prepareHref, showError, git } from '../commons';
import EditorSettings from './EditorSettings.vue';
import Breadcrumb from './Breadcrumb.vue';

export default defineComponent({
    components: {
        'settings': EditorSettings,
        'breadcrumb': Breadcrumb,
    },
    props: [ 'stack', 'config', 'isGit' ],
    data() {
        return {
            editorPath: null, // path of the file open in editor
            editor: null, // CodeMirror instance
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
            },
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
            axios.get(prepareHref('files' + path))
                 .then((response) => {
                      let data = response.data;
                      // Replace tabs with spaces
                      if (self.editor.getMode().name == 'python') {
                          data = data.replace(/\t/g, '    ');
                      }
                      self.editor.setValue(data);
                      self.editorPath = path;
                      // Update url hash
                      if (! path.startsWith('/~git/')) {
                          document.location.hash = self.normalize('edit' + path);
                      }
                  })
                  .catch((error) => {
                      console.log(error);
                      self.editor.setValue('');
                      self.editorPath = path;
                      self.editor.openNotification('file not found', { duration: 5000 })
                  });
        },
        editorSave(path) {
            // Save editor content
            const self = this;
            const payload = self.editor.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };

            axios.post(prepareHref('files' + path), payload, options)
                 .then((response) => {
                    if (response.data.error) {
                        showError(response.data.error.message || 'Error saving file');
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
                 })
                 .catch((error) => showError(error.response ? error.response.data.message : error));
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
            const payload = self.editor.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            axios.post(prepareHref('format'), payload, options)
                 .then((response) => {
                    self.editor.setValue(response.data.data);
                 })
                 .catch((error) => showError(error.response ? error.response.data.message : error));
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
                let baseUrl = jQuery('link[rel=stylesheet]').filter((i, e) => e.href.match(/gitweb.css/) !== null)[0].href.split('/gitweb.css')[0];;
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
                        git([ 'mv-local', item.object, target ], (data) => {});
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
        showBlob() {
            // Show file in editor
            const self = this;
            self.readOnly = self.isGit;
            let last = self.stack.last();
            if (last.type == 'blob') {
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
                    setTimeout(() => {
                        self.editor.refresh();
                    }, 100);
                } else {
                    // Load the file
                    self.editorLoad(self.editorPath);
                }
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
        stack: {
            handler(val, preVal) {
                console.log('Editor.watch stack');
                const self = this;
                self.showBlob();
            },
            deep: true
        }
    },
    mounted() {
        console.log('Editor.mounted');
        const self = this;
        self.editor = markRaw(CodeMirror.fromTextArea(self.$el.querySelector('textarea'), self.codeMirrorOptions));
        self.editor.save = () => self.saveAction(); // save file command
        self.showBlob();
        window._editor = self.editor;
    }
})
</script>
