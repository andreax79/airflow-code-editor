<template>
    <div class="tree-view">
        <files :stack="stack" :config="config" :is-git="isGit" v-if="!isEditorOpen"></files>
        <editor :stack="stack" :config="config" :is-git="isGit" v-if="isEditorOpen"></editor>
    </div>
</template>
<script>
import { defineComponent } from 'vue';
import Files from './Files.vue';
import Editor from './Editor.vue';

export default defineComponent({
    components: {
        'files': Files,
        'editor': Editor,
    },
    props: [ 'stack', 'config', 'isGit' ],
    data() {
        return {
            isEditorOpen: false, // is editor open
        }
    },
    watch: {
        stack: {
            handler(val, preVal) {
                console.log('Pane.watch stack.stack');
                const self = this;
                if (self.stack.last().type == 'blob') {
                    self.isEditorOpen = true;
                } else {
                    self.isEditorOpen = false;
                }
            },
            deep: true
        }
    }
})
</script>
