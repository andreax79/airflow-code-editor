<template>
  <div class="workspace-view">
      <ol class="breadcrumb">
        <div class="breadcrumb-buttons">
            <button v-on:click="pull()" type="button" class="btn btn-outlined"><icon icon="keyboard_double_arrow_down"/> Pull</button>
            <button v-on:click="push()" type="button" class="btn btn-outlined"><icon icon="keyboard_double_arrow_up"/> Push</button>
        </div>
      </ol>
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
  </div>
</template>
<style>
.workspace-view {
    width: 100%;
}
.workspace-view .breadcrumb {
    padding: 0.5rem 1rem 0.5rem 1rem;
    margin-bottom: 0;
    border-radius: 0px;
    text-align: right;
    background-color: inherit;
    border-bottom: 1px solid #dddddd;
}
.workspace-view .breadcrumb-buttons {
}
.workspace-view .breadcrumb-buttons .btn {
    margin-left: 0.5em;
}
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
import { git_async } from '../commons';
import { Splitpanes, Pane } from 'splitpanes';
import Icon from './Icon.vue';
import WorkspaceFiles from './WorkspaceFiles.vue';
import ShowDiff from './ShowDiff.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'icon': Icon,
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
        async pull(item) {
            // Pull
            const cmd = [
                'pull', '--no-rebase', '--ff-only'
            ];
            await git_async(cmd, { type: 'terminal', 'title': 'Git Pull' });
            this.refresh();
        },
        async push(item) {
            // Push
            const cmd = [
                'push'
            ];
            await git_async(cmd, { type: 'terminal', 'title': 'Git Push' });
            this.refresh();
        },
    },
})
</script>
