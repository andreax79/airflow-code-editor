<template>
    <div class='tree-view'>
        <ol class="breadcrumb">
          <li v-for="(item, index) in stack.stack" :index="index" class="breadcrumb-item">
              <a v-if="index != stack.stack.length-1" :href="item.uri" v-on:click.prevent="breadcrumbClicked(index, item)">{{ item.name }}</a>
              <span class="active" v-if="index == stack.stack.length-1">{{ item.name }}</span>
          </li>
          <div class="breadcrumb-buttons">
              <button v-on:click="newAction()" v-if="!isEditorOpen && !isGit" type="button" class="btn btn-default btn-sm">New <i class="fa fa-plus-square" aria-hidden="true"></i></button>
              <button v-on:click="uploadAction()" v-if="!isEditorOpen && !isGit" type="button" class="btn btn-default btn-sm">Upload <i class="fa fa-cloud-upload" aria-hidden="true"></i></button>
              <input type="file" multiple="multiple" style="display: none" ref="file" @change="handleUploadButton"></input>
          </div>
        </ol>

        <div class="tree-view-tree-content"
             @dragenter.stop.prevent="isDragEnter = true"
             @dragover.stop.prevent="() => {}"
             @dragleave.stop.prevent="isDragEnter = false"
             @drop.stop.prevent="handleDrop"
             v-show="!isEditorOpen">
            <vue-good-table
              :fixed-header="true"
              max-height="100%"
              :columns="columns"
              :rows="items">
              <template slot="table-row" slot-scope="props">
                <span v-if="props.column.field == 'name'" :class="props.column.field">
                  <a v-on:click.prevent="click(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')" >
                    {{ props.row.name }}
                  </a>
                </span>
                <span v-else-if="props.column.field == 'icon'" :class="props.column.field">
                  <a v-on:click.prevent="click(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')" >
                    <i :class="'fa ' + props.row.icon" aria-hidden="true"></i>
                  </a>
                </span>
                <span v-else-if="props.column.field == 'action'" class="btn-group">
                  <a v-if="props.row.type == 'blob'" class="download btn btn-default btn-sm" title="Download" :href="props.row.downloadHref"><i class="fa fa-download" aria-hidden="true"></i></a>
                  <a v-if="(!props.row.isGit) && (props.row.type == 'blob' || props.row.size == 0)" class="trash-o btn btn-default btn-sm" title="Delete" target="_blank" v-on:click.prevent="deleteAction(props.row)" :href="props.row.href"><i class="fa fa-trash-o" aria-hidden="true"></i></a>
                  <a v-if="!props.row.isGit && (props.row.name != '..')" class="i-cursor btn btn-default btn-sm" title="Move/Rename" target="_blank" v-on:click.prevent="moveAction(props.row)" :href="props.row.href"><i class="fa fa-i-cursor" aria-hidden="true"></i></a>
                  <a v-if="!props.row.isGit && (props.row.name != '..')" class="external-link btn btn-default btn-sm" title="Open in a new window" target="_blank" :href="props.row.href"><i class="fa fa-external-link" aria-hidden="true"></i></a>
                </span>
                <span v-else-if="props.column.field == 'size'" :class="props.column.field">
                  {{ props.row.formattedSize }}
                </span>
                <span v-else :class="props.column.field">
                  {{ props.formattedRow[props.column.field] }}
                </span>
              </template>
            </vue-good-table>
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
import axios from 'axios';
import { VueGoodTable } from 'vue-good-table';
import { BootstrapDialog } from '../bootstrap-dialog';
import { TreeEntry, prepareHref, showError, git } from "../commons";
import EditorSettings from './EditorSettings.vue';

export default {
    components: {
        'settings': EditorSettings,
        'vue-good-table': VueGoodTable
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
            },
            columns: [
                {
                  label: '',
                  field: 'icon',
                  width: '20px',
                  sortable: true
                },
                {
                  label: 'Name',
                  field: 'name',
                  thClass: 'vgt-right-align',
                  filterOptions: {
                      enabled: true
                  }
                },
                {
                  label: 'Modified',
                  field: 'mtime',
                  thClass: 'vgt-right-align',
                  tdClass: 'vgt-right-align',
                  filterOptions: {
                      enabled: true
                  }
                },
                {
                  label: 'Size',
                  field: 'size',
                  thClass: 'vgt-right-align',
                  type: 'number'
                },
                {
                  label: 'Actions',
                  field: 'action',
                  thClass: 'vgt-right-align',
                  tdClass: 'vgt-right-align',
                  sortable: false
                }
            ]
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
                 .then(function (response) {
                      let data = response.data;
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
                  .catch(function (error) {
                      console.log(error);
                      self.editor.setValue('');
                      self.editor.refresh();
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
                    self.editor.refresh();
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
        uploadAction() {
            // Upload button action
            const self = this;
            this.$refs.file.click();
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
                path = 'tree' + self.normalize('git/' + last.object);
            } else { // local
                path = 'tree' + self.normalize('files' + (last.object || ''));
                // Update url hash
                document.location.hash = self.normalize('files' + (last.object || ''));
            }
            // Get tree items
            axios.get(prepareHref(path), { params: { long: true }})
                  .then((response) => {
                        let blobs = []; // files
                        let trees = []; // directories
                        response.data.value.forEach((part) => {
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
                  .catch(error => {
                        console.log(error);
                  })
        },
        handleDrop($event) {
            // Upload files (drag and drop)
            this.isDragEnter = false;
            this.uploadFiles($event.dataTransfer.files);
        },
        handleUploadButton($event) {
            // Upload files (upload button)
            const self = this;
            const files = Array.from($event.target.files);
            self.uploadFiles(files);
            $event.target.value = '';
        },
        uploadFiles(files) {
            // Upload files
            const self = this;
            if (!self.isGit) {
                files.forEach((file) => {
                    const filename = self.normalize((self.stack.last().object || '') + '/' + self.basename(file.name));
                    const payload = file;
                    const options = {
                        headers: {
                            'Content-Type': file.type
                        }
                    };
                    // Upload file
                    axios.post(prepareHref('files' + filename), payload, options)
                         .then((response) => self.refresh())
                         .catch((error) => console.log(error));
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
