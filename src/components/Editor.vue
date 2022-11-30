<template>
    <div class="tree-view">
        <ol class="breadcrumb" v-if="showBreadcrumb">
            <breadcrumb @changePath="changePath" :stack="stack" :is-git="isGit"></breadcrumb>
        </ol>

        <div class="tree-view-blob-content">
            <div class="cm-fullscreen-container cm-flex-container">
                <div class="cm-toolbar cm-flex-child-fixed">
                </div>
                <div class="cm-body cm-flex-child-grow">
                    <textarea rows="30" cols="80" name="editor" style="display: none"></textarea>
                </div>
                <div class="cm-footer cm-flex-child-fixed">
                    <button v-on:click="saveAction()" v-if="!readOnly" type="button" class="btn btn-primary"><icon icon="save"/> Save</button>
                    <button v-on:click="saveAsAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="save_as"/> Save as</button>
                    <button v-on:click="revertAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="rotate_left"/> Revert</button>
                    <button v-on:click="findAction()" type="button" class="btn btn-default"><icon icon="search"/> Find</button>
                    <button v-on:click="replaceAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="find_replace"/> Replace</button>
                    <button v-on:click="formatAction()" v-if="!readOnly" type="button" class="btn btn-default" v-show="isPython"><icon icon="format_indent_increase"/> Format Code</button>
                    <button v-on:click="settingsAction()" type="button" class="btn btn-default" style="float: right"><icon icon="settings"/> Settings</button>
                </div>
            </div>
        </div>

        <settings-dialog ref="settingsDialog"></settings-dialog>
        <save-as-dialog ref="saveAsDialog"></save-as-dialog>
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
.tree-view-blob-content .btn {
    margin-right: 0.5em;
}
</style>
<script>
import axios from 'axios';
import { defineComponent, markRaw } from 'vue';
// import { str as crc32 } from 'crc-32';
import { normalize, prepareHref, showError, importTheme } from '../commons';
import Breadcrumb from './Breadcrumb.vue';
import Icon from './Icon.vue';
import SettingsDialog from './dialogs/SettingsDialog.vue';
import SaveAsDialog from './dialogs/SaveAsDialog.vue';

export default defineComponent({
    components: {
        'icon': Icon,
        'settings-dialog': SettingsDialog,
        'save-as-dialog': SaveAsDialog,
        'breadcrumb': Breadcrumb,
    },
    props: [ 'stack', 'config', 'isGit', 'showBreadcrumb' ],
    data() {
        return {
            editorPath: null, // path of the file open in editor
            editor: null, // CodeMirror instance
            isPython: false, // is editor open on a python file
            readOnly: false,
            generation: 0,
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
        isNew(filename) {
            return /✧$/.test(filename);
        },
        isChanged() {
            return !this.editor.isClean(this.generation);
            // return this.checksum != crc32(this.editor.getValue());
        },
        setValue(data) {
            this.editor.setValue(data);
            // Update generation
            this.generation = this.editor.changeGeneration();
            // Update checksum
            // this.checksum = crc32(data);
            // Clear history
            this.editor.clearHistory()
        },
        async editorLoad(path) {
            // Load a file into the editor
            // Force data to String (avoid string.slit exception in CodeMirror)
            // https://github.com/axios/axios/issues/811
            try {
                const response = await axios.get(prepareHref('files' + path),
                    { transformResponse: res => res });
                let data = response.data;
                // Replace tabs with spaces
                if (this.editor.getMode().name == 'python') {
                    data = data.replace(/\t/g, '    ');
                }
                this.setValue(data);
                this.editorPath = path;
                this.$emit('loaded', false); // close the spinner
                // Update url hash
                this.$emit('updateLocation');
            } catch(error) {
                this.$emit('loaded', false); // close the spinner
                this.setValue('');
                this.editorPath = path;
                try {
                    const data = JSON.parse(error.response.data);
                    showError(data.error.message);
                } catch (ex) {
                    showError('Error loading file');
                }
            };
        },
        async editorSave(path) {
            // Save editor content
            const payload = this.editor.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            path = normalize(path);
            if (path == "/") {
                showError('Invalid filename');
                return;
            }
            try {
                const response = await axios.post(prepareHref('files' + path), payload, options);
                if (response.data.error) {
                    showError(response.data.error.message || 'Error saving file');
                } else {
                    // Update editor path and the breadcrumb
                    if (path != this.editorPath) {
                        this.editorPath = path;
                        this.stack.updateStack(path, 'blob');
                    }
                    this.editor.openNotification('file saved', { duration: 5000 })
                    // Update url hash
                    this.$emit('updateLocation');
                    // Update checksum
                    // this.checksum = crc32(payload);
                    // Update generation
                    this.generation = this.editor.changeGeneration();
                }
            } catch(error) {
                showError(error.response ? error.response.data.message : error);
            }
        },
        async editorSaveAs(path) {
            // Show 'Save as...' dialog
            if (this.isNew(path)) {
                path = path.replace('✧', 'new file.txt');
            }
            const target = await this.$refs.saveAsDialog.showDialog(path);
            if (target) {
                this.editorSave(target);
            }
        },
        async editorFormat() {
            // Format code
            const payload = this.editor.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            try {
                const response = await axios.post(prepareHref('format'), payload, options);
                this.editor.setValue(response.data.data);
            } catch(error) {
                showError(error.response ? error.response.data.message : error);
            }
        },
        setOption(option, value) {
            // Set editor option
            if (this.editor) {
                this.editor.setOption(option, value);
            }
        },
        async setTheme(theme) {
            // Set editor theme
            if (theme == 'default') {
                this.setOption('theme', theme);
            } else {
                await importTheme(theme);
                this.setOption('theme', theme);
            }
        },
        async updateSettings(config) {
            this.config.theme = config.theme;
            this.config.mode = config.mode;
            this.setTheme(this.config.theme); // Set theme
            this.setOption('keyMap', this.config.mode); // Set editor mode
            // Save setting on the local storage
            localStorage.setItem('airflow_code_editor_theme', config.theme);
            localStorage.setItem('airflow_code_editor_mode', config.mode);
        },
        async saveAction() {
            // Save button action
            if (this.isNew(this.editorPath)) {
                this.editorSaveAs(this.editorPath);
            } else {
                this.editorSave(this.editorPath);
            }
        },
        async saveAsAction() {
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
        async settingsAction() {
            // Settings button action
            const config = await this.$refs.settingsDialog.showDialog(this.config);
            if (config) {
                this.updateSettings(config);
            }
        },
        changePath(item) {
            // Change File/directory
            this.$emit('changePath', item);
        },
        refresh() {
            console.log('Editor.refresh');
            // Show file in editor
            this.readOnly = this.isGit;
            let last = this.stack.last();
            if (last.type == 'blob') {
                if (this.isGit){ // Git hash
                    this.editorPath = normalize('/~git/' + last.object + '/'+ last.name);
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
                    this.$emit('loaded', false); // close the spinner
                    this.setValue('');
                    setTimeout(() => this.editor.refresh(), 100);
                } else {
                    // Load the file
                    this.editorLoad(this.editorPath);
                }
            }
        },
    },
    mounted() {
        console.log('Editor.mounted');
        this.editor = markRaw(CodeMirror.fromTextArea(this.$el.querySelector('textarea'), this.codeMirrorOptions));
        this.editor.save = async () => this.saveAction(); // save file command
        this.refresh();
        window._editor = this.editor;
        window._e = this;
    }
})
</script>
