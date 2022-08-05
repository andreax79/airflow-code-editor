<template>
    <div class="tree-view">
        <ol class="breadcrumb" v-if="showBreadcrumb">
            <breadcrumb :stack="stack" :is-git="isGit"></breadcrumb>
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
<style>
.tree-view-blob-content {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    width: 100%;
}
</style>
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
    props: [ 'stack', 'config', 'isGit', 'showBreadcrumb' ],
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
            axios.get(prepareHref('files' + path))
                 .then((response) => {
                      let data = response.data;
                      // Replace tabs with spaces
                      if (this.editor.getMode().name == 'python') {
                          data = data.replace(/\t/g, '    ');
                      }
                      this.editor.setValue(data);
                      this.editorPath = path;
                      // Update url hash
                      if (! path.startsWith('/~git/')) {
                          document.location.hash = this.normalize('edit' + path);
                      }
                  })
                  .catch((error) => {
                      console.log(error);
                      this.editor.setValue('');
                      this.editorPath = path;
                      this.editor.openNotification('file not found', { duration: 5000 })
                  });
        },
        editorSave(path) {
            // Save editor content
            const self = this;
            const payload = this.editor.getValue();
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
            if (this.isNew(path)) {
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
            const payload = this.editor.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            axios.post(prepareHref('format'), payload, options)
                 .then((response) => this.editor.setValue(response.data.data))
                 .catch((error) => showError(error.response ? error.response.data.message : error));
        },
        setOption(option, value) {
            // Set editor option
            if (this.editor) {
                this.editor.setOption(option, value);
            }
            // Store settings in localStorage
            if (option == 'keyMap') {
                option = 'mode';
            }
            localStorage.setItem('airflow_code_editor_' + option, value);
        },
        setTheme(theme) {
            // Set editor theme
            if (theme == 'default') {
                this.setOption('theme', theme);
            } else {
                let link = document.createElement('link');
                link.onload = () => this.setOption('theme', theme);
                let baseUrl = jQuery('link[rel=stylesheet]').filter((i, e) => e.href.match(/gitweb.css/) !== null)[0].href.split('/gitweb.css')[0];;
                link.rel = 'stylesheet';
                link.type = 'text/css';
                link.href = baseUrl + '/theme/' + theme + '.css';
                document.getElementsByTagName('head')[0].appendChild(link);
            }
        },
        updateLocation() {
            // Update href hash
            if (!this.isGit) {
                document.location.hash = this.normalize('files' + (this.stack.last().object || '/'));
            }
        },
        click(item) {
            // File/directory action
            if (item.name == '..') {
                this.stack.pop();
            } else {
                this.stack.push(item);
            }
            // Update href hash
            this.updateLocation();
            return false;
        },
        breadcrumbClicked(index, item) {
            // Breadcrumb action
            this.stack.slice(index + 1);
            // Update href hash
            this.updateLocation();
            return false;
        },
        moveAction(item) {
            // Delete a file
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
            if (this.isNew(this.editorPath)) {
                this.editorSaveAs(this.editorPath);
            } else {
                this.editorSave(this.editorPath);
            }
        },
        saveAsAction() {
            // Save as button action
            this.editorSaveAs(this.editorPath);
        },
        revertAction() {
            // Revert button action
            if (! this.isNew(this.editorPath)) {
                this.editorLoad(this.editorPath);
            }
        },
        findAction() {
            // Find button action
            this.editor.execCommand('find');
        },
        replaceAction() {
            // Replace button action
            this.editor.execCommand('replace');
        },
        formatAction() {
            // Format button action
            this.editorFormat();
        },
        settingsAction() {
            // Settings button action
            jQuery(this.$el.querySelector('.settings-modal')).modal({ backdrop: false, show: true });
        },
        refresh() {
            console.log('Editor.refresh');
            // Show file in editor
            this.readOnly = this.isGit;
            let last = this.stack.last();
            if (last.type == 'blob') {
                if (this.isGit){ // Git hash
                    this.editorPath = this.normalize('/~git/' + last.object + '/'+ last.name);
                } else { // File path
                    this.editorPath = last.object;
                }
                // Create CodeMirror instance and set the mode
                let info;
                if (this.isNew(last.name)) {
                    info = { 'mode': 'python' };
                } else {
                    info = CodeMirror.findModeByFileName(last.name);
                }
                this.editor.setOption('mode', info && info.mode);
                this.isPython = info && info.mode == 'python';
                this.setTheme(this.config.theme);
                this.setOption('keyMap', this.config.mode);
                this.setOption('readOnly', this.readOnly);
                if (info) {
                    CodeMirror.autoLoadMode(this.editor, info.mode);
                }
                if (this.isNew(last.name)) {
                    // New file
                    this.editor.setValue('');
                    setTimeout(() => {
                        this.editor.refresh();
                    }, 100);
                } else {
                    // Load the file
                    this.editorLoad(this.editorPath);
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
    },
    mounted() {
        console.log('Editor.mounted');
        this.editor = markRaw(CodeMirror.fromTextArea(this.$el.querySelector('textarea'), this.codeMirrorOptions));
        this.editor.save = () => this.saveAction(); // save file command
        this.refresh();
        window._editor = this.editor;
    }
})
</script>
