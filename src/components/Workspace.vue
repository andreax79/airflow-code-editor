<template>
  <splitpanes class="default-theme">
    <pane class="workspace-file-pane" :size="33">
      <spinner v-show="loading"/>
      <workspacefiles @showDiff="showDiff" ref="unstaged" kind="unstaged" @refresh="refresh"></workspacefiles>
    </pane>
    <pane class="workspace-file-pane" :size="33">
      <workspacefiles @showDiff="showDiff" ref="staged" kind="staged" @refresh="refresh"></workspacefiles>
    </pane>
    <pane :size="34" class="workspace-show-diff-pane">
      <diff ref="diff" linesOfContext="3" @loaded="loaded"></diff>
    </pane>
  </splitpanes>
</template>
<style>
.workspace-file-pane {
    display: flex;
    flex-direction: column;
    min-height: 0;
}
.workspace-show-diff-pane {
    display: flex;
    flex-direction: column;
    min-height: 0;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import WorkspaceFiles from './WorkspaceFiles.vue';
import ShowDiff from './ShowDiff.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'splitpanes': Splitpanes,
        'pane': Pane,
        'workspacefiles': WorkspaceFiles,
        'diff': ShowDiff,
        'spinner': Spinner,
    },
    props: [],
    data() {
        return {
            loading: false,
            showDiffPane: false,
        }
    },
    mounted() {
        this.refresh();
    },
    methods: {
        isChanged() {
            return false;
        },
        showDiff(target) {
            this.loading = true;
            this.$refs.diff.refresh(target);
        },
        updateLocation() {
            // Update href hash
            document.location.hash = 'workspace';
        },
        refresh() {
            // Refresh
            this.showDiffPane = false;
            this.$refs.unstaged.refresh();
            this.$refs.staged.refresh();
            // Update href hash
            this.updateLocation();
        },
        loaded(success) {
            // Emitted then commit is loaded/loading fails
            this.loading = false;  // Hide the spinner
            this.showDiffPane = success;
        },
    },
})
</script>
