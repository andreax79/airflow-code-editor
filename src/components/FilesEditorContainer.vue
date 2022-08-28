<template>
    <div class="tree-view">
        <spinner v-show="loading"/>
        <files ref="files"
            :stack="stack"
            :config="config"
            :isGit="isGit"
            :showBreadcrumb="true"
            @changePath="changePath"
            @changePathUp="changePathUp"
            @updateLocation="updateLocation"
            @loaded="loaded"
            v-show="!isEditorOpen"></files>
        <editor ref="editor"
            :stack="stack"
            :config="config"
            :isGit="isGit"
            :showBreadcrumb="true"
            @changePathUp="changePathUp"
            @updateLocation="updateLocation"
            @loaded="loaded"
            v-if="isEditorOpen"></editor>
    </div>
</template>
<script>
import { defineComponent } from 'vue';
import { Stack } from '../stack';
import { normalize } from '../commons';
import Files from './Files.vue';
import Editor from './Editor.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'files': Files,
        'editor': Editor,
        'spinner': Spinner,
    },
    props: [ 'config', 'isGit' ],
    data() {
        return {
            stack: new Stack(), // files stack
            isEditorOpen: false, // is editor open
            loading: false,
        }
    },
    methods: {
        updateLocation() {
            // Update href hash
            if (!this.isGit) {
                const section = (this.stack.last().type == 'blob') ? 'edit' : 'files';
                const object = this.stack.last().object || '/';
                document.location.hash = normalize(section + object);
            }
        },
        updateStack(path, type) {
            this.loading = true;
            // Update current file/directory
            this.stack.updateStack(path, type);
            // Refresh files/editor
            this.refresh();
        },
        changePath(item) {
            // Change File/directory
            console.log("FilesEditorContainer.changePath item.name:" + item.name);
            this.loading = true;
            if (item.name == '..') {
                this.stack.pop();
            } else {
                this.stack.push(item);
            }
            // Refresh files/editor
            this.refresh();
        },
        changePathUp(index) {
            // Change directory to a parent directory (for breadcrum)
            console.log("FilesEditorContainer.changePathUp index: " + index);
            this.loading = true;
            this.stack.slice(index + 1);
            // Refresh files/editor
            this.refresh();
        },
        refresh() {
            // Refresh files/editor
            if (this.stack.last().type == 'blob') {
                if (this.$refs.editor) { // update editor if already open
                    this.$refs.editor.refresh();
                }
                this.isEditorOpen = true;
            } else {
                if (this.$refs.files) { // update files if already open
                    this.$refs.files.refresh();
                }
                this.isEditorOpen = false;
            }
            // Update href hash
            this.updateLocation();
        },
        loaded() {
            // Emitted then commit is loaded
            this.loading = false;  // Hide the spinner
        },
    },
})
</script>
