<template>

  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar class="app-sidebar"
            :current="current"
            @showFile="showFile"
            @showHistory="showHistory"
            @showWorkspace="showWorkspace"
            ></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" class="app-main-view">
        <historyview ref="historyview"
            :config="config"
            v-show='current.section == "local-branches" | current.section == "remote-branches" | current.section == "tags"'></historyview>
        <div id="workspace-view" v-show='current.section == "workspace"'>
            <div id="workspace-diff-view">
                <div class="diff-view-container panel panel-default">
                    <div class="panel-heading btn-toolbar" role="toolbar">
                        <button type="button" class="btn btn-sm btn-default diff-ignore-whitespace" data-toggle="button">Ignore Whitespace</button>
                        <button type="button" class="btn btn-sm btn-default diff-context-all" data-toggle="button">Complete file</button>
                        <div class="btn-group btn-group-sm">
                            <span></span>&nbsp;
                            <button type="button" class="btn btn-default diff-context-remove">-</button>
                            <button type="button" class="btn btn-default diff-context-add">+</button>
                        </div>
                        <div class="btn-group btn-group-sm diff-selection-buttons">
                            <button type="button" class="btn btn-default diff-stage" style="display:none">Stage</button>
                            <button type="button" class="btn btn-default diff-cancel" style="display:none">Cancel</button>
                            <button type="button" class="btn btn-default diff-unstage" style="display:none">Unstage</button>
                        </div>
                    </div>
                    <div class="panel-body"></div>
                </div>
            </div>
            <div id="workspace-editor">
            </div>
        </div>
        <container
            clas="app-files-view"
            ref="container"
            v-show='current.section == "files"'
            :config="config"
            :is-git="false"></container>
    </pane>
  </splitpanes>
</template>
<style>
.app-sidebar {
    height: 100%;
    overflow-y: auto;
    background-color: #333333;
}
.app-main-view {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
}
</style>
<script>
import { defineComponent } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import { WorkspaceView } from '../workspace';
import Sidebar from './Sidebar.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import HistoryView from './HistoryView.vue';

export default defineComponent({
    components: {
        splitpanes: Splitpanes,
        pane: Pane,
        sidebar: Sidebar,
        container: FilesEditorContainer,
        historyview: HistoryView,
    },
    data() {
        return {
            current: {
                section: null, // current sidebar section (files, werkspace, ...)
                object: null, // current sidebar object
            },
            config: {
                theme: localStorage.getItem('airflow_code_editor_theme') || 'default', // editor theme
                mode: localStorage.getItem('airflow_code_editor_mode') || 'default', // edit mode (default, vim, etc...)
            },
            workspaceView: null,
            sidebarSize: 190 * 100 / jQuery(document).width() // sidebar size (percentage)
        };
    },
    methods: {
        initViews() {
            // Init views
            this.workspaceView = new WorkspaceView();
        },
        showFile(target) {
            this.current.section = 'files';
            this.current.object = target.path;
            this.$refs.container.updateStack(target.path, target.type);
        },
        showHistory(target) {
            this.current.section = target.id;
            this.current.object = target.name;
            this.$refs.historyview.update(target);
        },
        showWorkspace(target) {
            this.current.section = target.id;
            this.current.object = target.name;
            this.workspaceView.update();
        }
    },
    mounted() {
        // Init
        this.initViews();
    }
})
</script>

