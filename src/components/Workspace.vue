<template>
  <div class="workspace-view">
    <ol class="breadcrumb">
      <div class="breadcrumb-buttons">
        <button style="display: none"  v-on:click="pushAction()" type="button" class="btn btn-primary"><icon icon="file_upload"/> Push</button>
        <button v-on:click="pullAction()" type="button" class="btn btn-primary"><icon icon="file_download"/> Pull</button>
        <button v-on:click="fetchAction()" type="button" class="btn btn-primary"><icon icon="download_for_offline"/> Fetch</button>
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
    <term-dialog ref="termDialog"></term-dialog>
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
    height: 4rem;
    border-bottom: 1px solid #ccc;
}
.workspace-view .breadcrumb li {
    margin-top: 0.6rem;
    margin-bottom: 0.6rem;
}
.workspace-view .breadcrumb a {
    text-decoration: none;
    cursor: pointer;
}
.workspace-view .breadcrumb-buttons {
    float: right;
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
import { Splitpanes, Pane } from 'splitpanes';
import WorkspaceFiles from './WorkspaceFiles.vue';
import ShowDiff from './ShowDiff.vue';
import Spinner from './Spinner.vue';
import Icon from './Icon.vue';
import TermDialog from './dialogs/TermDialog.vue';

export default defineComponent({
    components: {
        'splitpanes': Splitpanes,
        'icon': Icon,
        'pane': Pane,
        'workspacefiles': WorkspaceFiles,
        'diff': ShowDiff,
        'spinner': Spinner,
        'term-dialog': TermDialog,
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
        dispose() {
            // Dispose
        },
        pushAction() {
            // Git push
            // TODO
        },
        async pullAction() {
            // Git pull
            await this.$refs.termDialog.showDialog("pull");
            this.refresh();
        },
        async fetchAction() {
            // Git fetch
            await this.$refs.termDialog.showDialog("fetch");
            this.refresh();
        },
        loaded(success) {
            // Emitted then commit is loaded/loading fails
            this.loading = false;  // Hide the spinner
            this.showDiffPane = success;
        },
    },
})
</script>
