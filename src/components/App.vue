<template>

  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar id="sidebar" :stack="stack" :historyState="historyState" :current="current" :workspace-view="workspaceView"></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" id="main-view">
        <historyview :historyState="historyState"
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
        <div id="files-view" v-show='current.section == "files"'>
            <div style="height: 100%">
                <container :stack="stack" :config="config" :is-git="false"></container>
            </div>
        </div>
    </pane>
  </splitpanes>
</template>
<script>
import { defineComponent } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import { Stack } from '../stack';
import { WorkspaceView } from '../workspace';
import { HistoryState } from '../history_state';
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
            stack: new Stack(), // files stack
            historyState: new HistoryState(),
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
            const self = this;
            self.workspaceView = new WorkspaceView();
        },
    },
    mounted() {
        // Init
        const self = this;
        self.initViews();
    }
})
</script>

