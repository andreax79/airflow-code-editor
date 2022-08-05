<template>
    <div class="tree-view">
        <files ref="files" :stack="stack" :config="config" :isGit="isGit" :showBreadcrumb="true" v-if="!isEditorOpen"></files>
        <editor ref="editor" :stack="stack" :config="config" :isGit="isGit" :showBreadcrumb="true" v-if="isEditorOpen"></editor>
    </div>
</template>
<script>
import { defineComponent } from 'vue';
import { Stack } from '../stack';
import Files from './Files.vue';
import Editor from './Editor.vue';

export default defineComponent({
    components: {
        'files': Files,
        'editor': Editor,
    },
    props: [ 'config', 'isGit' ],
    data() {
        return {
            stack: new Stack(), // files stack
            isEditorOpen: false, // is editor open
        }
    },
    methods: {
        updateStack(path, type) {
            this.stack.updateStack(path, type);
        }
    },
    watch: {
        stack: {
            handler(val, preVal) {
                console.log('FilesEditorContainer.watch stack');
                if (this.stack.last().type == 'blob') {
                    if (this.$refs.editor) { // update editor if already open
                        this.$refs.editor.refresh();
                    }
                    this.isEditorOpen = true;
                } else {
                    this.isEditorOpen = false;
                }
            },
            deep: true
        }
    }
})
</script>
