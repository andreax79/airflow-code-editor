<template>
    <div class="tree-view">
        <spinner v-show="loading"/>
        <files ref="files"
            :uuid="uuid"
            :stack="stack"
            :config="config"
            :isGit="isGit"
            :showBreadcrumb="true"
            @changePath="changePath"
            @updateLocation="updateLocation"
            @loaded="loaded"
            v-show="!isEditorOpen"></files>
        <editor ref="editor"
            :uuid="uuid"
            :stack="stack"
            :config="config"
            :isGit="isGit"
            :showBreadcrumb="true"
            @changePath="changePath"
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
    props: [ 'config', 'isGit', 'target', 'uuid' ],
    data() {
        return {
            stack: new Stack(), // files stack
            isEditorOpen: false, // is editor open
            loading: false,
        }
    },
    mounted() {
        if (this.target) {
            this.update(this.target);
        }
    },
    methods: {
        isChanged() {
            return this.$refs.editor && this.$refs.editor.isChanged();
        },
        update(target) {
            if (target) {
                this.updateStack(target.path, target.type);
            }
        },
        updateLocation() {
            // Update href hash
            if (!this.isGit) {
                this.$emit('setTab', this.stack.last());
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
            if (this.isGit) { // Git
                this.loading = true;
                if (item.name == '..') {
                    this.stack.pop();
                } else {
                    let index = this.stack.indexOf(item);
                    if (index != -1) {
                        this.stack.slice(index + 1);
                    } else {
                        this.stack.push(item);
                    }
                }
                // Refresh files/editor
                this.refresh();
            } if (this.config.singleTab) { // Files - single tab
                this.updateStack(item.object, item.type);
                this.loading = true;
                // Refresh files/editor
                this.refresh();
            } else { // Files - multi tab
                this.$emit("show", { id: 'files', path: item.object, type: item.type });
            }
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
