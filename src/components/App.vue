<template>
  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
      <sidebar id="sidebar" :stack="stack" :current="current" :history-view="historyView" :workspace-view="workspaceView"></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" id="main-view">
        <div id="history-view" v-show='current.section == "local-branches" | current.section == "remote-branches" | current.section == "tags"'>
            <div id="log-view" class="list-group"><svg xmlns="http://www.w3.org/2000/svg"></svg><div></div></div>
            <div id="commit-view">
                <div class="commit-view-header"></div>
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
                <div class="tree-view" style="display: none">
                    <files :stack='historyStack' :config="config" :is-git="true"></files>
                </div>
            </div>
        </div>
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
                <files :stack='stack' :config="config" :is-git="false"></files>
            </div>
        </div>
    </pane>
  </splitpanes>
</template>
<script>
import { Splitpanes, Pane } from 'splitpanes';
import { Stack } from '../commons';
import { HistoryView } from '../history';
import { WorkspaceView } from '../workspace';
import Sidebar from './Sidebar.vue';
import FilesView from './Files.vue';

export default {
    components: {
        splitpanes: Splitpanes,
        pane: Pane,
        sidebar: Sidebar,
        files: FilesView
    },
    data() {
        return {
            current: {
                section: null, // current sidebar section (files, werkspace, ...)
                object: null, // current sidebar object
            },
            stack: new Stack(), // files stack
            historyStack: new Stack(), // history view files stack
            config: {
                theme: localStorage.getItem('airflow_code_editor_theme') || 'default', // editor theme
                mode: localStorage.getItem('airflow_code_editor_mode') || 'default', // edit mode (default, vim, etc...)
            },
            historyView: null,
            workspaceView: null,
            sidebarSize: 190 * 100 / jQuery(document).width() // sidebar size (percentage)
        };
    },
    methods: {
        initViews() {
            // Init views
            const self = this;
            return new Promise((resolve, reject) => {
                self.historyView = new HistoryView(self.historyStack);
                self.workspaceView = new WorkspaceView();
                resolve(true);
            });
        },
    },
    mounted() {
        // Init
        const self = this;
        self.initViews();
    }
}
</script>
