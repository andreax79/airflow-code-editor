<template>
    <div class="tree-view">
        <ol class="breadcrumb" v-if="showBreadcrumb">
            <breadcrumb @changePath="changePath" :stack="stack" :is-git="isGit"></breadcrumb>
        </ol>

        <div class="tree-view-blob-content">
            <div class="cm-fullscreen-container cm-flex-container">
                <div class="cm-toolbar cm-flex-child-fixed">
                </div>
                <div class="cm-body cm-flex-child-grow codemirror-editor-parent">
                </div>
                <div class="cm-footer cm-flex-child-fixed">
                    <button v-on:click="saveAction()" v-if="!readOnly" type="button" class="btn btn-primary"><icon icon="save"/> Save</button>
                    <button v-on:click="saveAsAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="save_as"/> Save as</button>
                    <button v-on:click="revertAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="rotate_left"/> Revert</button>
                    <button v-on:click="findAction()" v-if="!readOnly" type="button" class="btn btn-default"><icon icon="search"/> Find/Replace</button>
                    <button v-on:click="findAction()" v-if="readOnly" type="button" class="btn btn-default"><icon icon="search"/> Find</button>
                    <button v-on:click="formatAction()" v-if="!readOnly" type="button" class="btn btn-default" v-show="language == 'Python'"><icon icon="format_indent_increase"/> Format Code</button>
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
/* CodeMirror styles */
.codemirror-editor-parent {
    height: 100% !important;
    overflow: auto !important;
}

.ͼ2 .cm-panels.cm-panels-bottom {
    border-top: 1px solid #ddd !important;
}
.ͼ2 .cm-search {
    background-color: #f5f5f5 !important;
}

.dark-theme .ͼ2 .cm-search {
    background-color: #333 !important;

}
.ͼ2 .cm-button {
    background-image: none !important;
    background: transparent !important;
    color: #017cee !important;
    border-radius: 1.25rem;
    border: 1px solid;
    line-height: 1.25rem;
    padding-left: 1rem;
    padding-right: 1rem;
    letter-spacing: .00625rem;
    font-weight: 700;
    font-family: Roboto Flex,roboto,system-ui,-apple-system,blinkmacsystemfont,Segoe UI,helvetica,arial,ubuntu,Noto Sans,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
    text-transform: capitalize;
    min-width: 8em;
}

.dark-theme button.cm-button {
    color: #d5eb2c !important;
}

.ͼ2 .cm-button:hover {
    background-color: #017cee0f !important;
    color: #0cb6ff !important;
}

.dark-theme .cm-button:hover {
    background-color: #d5eb2c0f !important;
    color: #d5eb2c !important;
}

.ͼ2 input.cm-textfield {
    border-radius: 4px;
}

.ͼ1 .cm-panel.cm-search label {
    font-weight: normal;
    margin-left: 1em;
}

.dark-theme .cm-panel.cm-search label {
    color: #fff !important;
}

.ͼ1 .cm-panel.cm-search label input {
    margin-right: 0.75em !important;
}

.dark-theme .cm-textfield {
    background-color: #333;
    color: #fff;
}

</style>
<script>
import axios from 'axios';
import { ref, defineComponent, markRaw } from 'vue';
import { str as crc32 } from 'crc-32';

import { basicSetup } from 'codemirror';
import { EditorView, keymap } from "@codemirror/view"
import { indentWithTab } from "@codemirror/commands"
import { EditorState } from '@codemirror/state';
import { openSearchPanel, closeSearchPanel } from '@codemirror/search';
import { ViewUpdate } from '@codemirror/view';
import { python } from '@codemirror/lang-python';
import { sql } from '@codemirror/lang-sql';
import { json } from '@codemirror/lang-json';
import { yaml } from '@codemirror/lang-yaml';
import { Vim, vim, getCM } from '@replit/codemirror-vim';
import { emacs } from "@replit/codemirror-emacs";

import { normalize, prepareHref, showNotification, parseErrorResponse } from '../commons';
import Breadcrumb from './Breadcrumb.vue';
import Icon from './Icon.vue';
import SettingsDialog from './dialogs/SettingsDialog.vue';
import SaveAsDialog from './dialogs/SaveAsDialog.vue';
import themes from "../themes";

Vim.defineEx('write', 'w', function(cm) {
    cm.cm6.vue.saveAction();
});

const languages = [
    { name: 'Python', extensions: ['py'] },
    { name: 'SQL', extensions: ['sql'] },
    { name: 'JSON', extensions: ['json'] },
    { name: 'YAML', extensions: ['yaml', 'yml'] },
];


function getLanguageFromFilename(filename) {
    const dot = filename.lastIndexOf(".");
    const extension = dot > -1 && filename.substring(dot + 1, filename.length).toLowerCase();
    const language = languages.find(lang => lang.extensions?.includes(extension));
    return language;
}

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
            language: null, // CodeMirror language (Python, SQL, JSON, YAML) or null 
            readOnly: false,
            checksum: 0,
        }
    },
    methods: {
        isNew(filename) {
            return /✧$/.test(filename);
        },
        isChanged() {
            // Check if the editor content has changed
            return this.checksum != crc32(this.getValue());
        },
        getValue() {
            // Get editor content
            return this.editor.state.doc.toString();
        },
        setValue(data) {
            // Set editor content
            let transaction = this.editor.state.update({changes: {from: 0, to: this.editor.state.doc.length, insert: data}})
            this.editor.dispatch(transaction);
            // Update checksum
            this.checksum != crc32(this.getValue());
            // Clear history
            this.updateState();
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
                if (this.language == 'Python') {
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
                const message = parseErrorResponse(error, 'Error loading file');
                showNotification({ message: message, title: 'Load' });
            };
        },
        async editorSave(path) {
            // Save editor content
            const payload = this.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            path = normalize(path);
            if (path == "/") {
                showNotification({ message: 'Invalid filename', title: 'Save' });
                return;
            }
            try {
                const response = await axios.post(prepareHref('files' + path), payload, options);
                if (response.data.error) {
                    const message = response.data.error.message || 'Error saving file';
                    showNotification({ message: message, title: 'Save' });
                } else {
                    // Update editor path and the breadcrumb
                    if (path != this.editorPath) {
                        this.editorPath = path;
                        this.stack.updateStack(path, 'blob');
                    }
                    // Show notification
                    showNotification({ message: 'File saved', title: 'Save', type: 'success' });
                    // Update url hash
                    this.$emit('updateLocation');
                    // Update checksum
                    this.checksum = crc32(payload);
                }
            } catch(error) {
                const message = parseErrorResponse(error, 'Error saving file');
                showNotification({ message: message, title: 'Save' });
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
            const payload = this.getValue();
            const options = {
                headers: {
                    'Content-Type': 'text/plain'
                }
            };
            try {
                const response = await axios.post(prepareHref('format'), payload, options);
                const newState = EditorState.create({
                    doc: response.data.data,
                    extensions: this.getExtensions(),
                });
                this.editor.setState(newState);
            } catch(error) {
                const message = parseErrorResponse(error, 'Error formatting file');
                showNotification({ message: message, title: 'Format' });
            }
        },
        async updateSettings(config) {
            // Update the editor settings (theme, mode, color)
            this.config.theme = config.theme;
            this.config.mode = config.mode;
            this.config.color = config.color;
            this.updateState();
        },
        updateState() {
            // Update the editor state
            const newState = EditorState.create({
                doc: this.editor.state.doc,
                extensions: this.getExtensions(),
            });
            this.editor.setState(newState);
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
            closeSearchPanel(this.editor) || openSearchPanel(this.editor);
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
            // Show file in editor
            this.readOnly = this.isGit;
            let last = this.stack.last();
            if (last.type == 'blob') {
                if (this.isGit){ // Git hash
                    this.editorPath = normalize('/~git/' + last.object + '/'+ last.name);
                } else { // File path
                    this.editorPath = last.object;
                }
                if (this.isNew(last.name)) {
                    this.language = 'Python';
                } else {
                    let dot = last.name.lastIndexOf('.');
                    let ext = dot > -1 && last.name.substring(dot + 1, last.name.length).toLowerCase();
                }
                // Update state
                this.updateState();

                if (this.isNew(last.name)) {
                    // New file
                    this.$emit('loaded', false); // close the spinner
                    this.setValue('');
                } else {
                    // Load the file
                    this.editorLoad(this.editorPath);
                    // Move cursor to line
                    // if (typeof last.line != 'undefined') {
                    //   this.editor.setCursor({line: last.line - 1, ch: 0, sticky: "after"});
                    //}
                }
            }
        },
        getExtensions() {
            let extensions = [];
            // Key bindings
            if (this.config.mode == 'vim') {
                extensions.push(vim());
            } else if (this.config.mode == 'emacs') {
                extensions.push(emacs());
            }
            extensions.push(basicSetup);
            extensions.push(keymap.of([indentWithTab]));
            // Language
            const last = this.stack.last();
            const filename = last.type == 'blob' ? last.name : '';
            const language = getLanguageFromFilename(filename);
            this.language = language?.name;
            switch (language?.name) {
                case 'Python':
                    extensions.push(python());
                    break;
                case 'SQL':
                    extensions.push(sql());
                    break;
                case 'JSON':
                    extensions.push(json());
                    break;
                case 'YAML':
                    extensions.push(yaml());
                    break;
            }
            // Read only
            if (this.readOnly) {
                extensions.push(EditorState.readOnly.of(true));
            }
            // Theme
            const theme = themes.find(theme => theme.name === this.config.theme);
            if (theme && theme.extension) {
                extensions.push(theme.extension);
            }
            return extensions;
        },
    },
    mounted() {
        const parent = this.$el.querySelector('.cm-body');
        const newState = EditorState.create({
            doc: '',
            extensions: this.getExtensions(),
        });
        this.editor = markRaw(new EditorView({
            state: newState,
            parent: parent
        }));
        this.editor.vue = this;  // used by Vim.defineEx
        this.refresh();
    },
    beforeDestroy() {
    }
})
</script>
