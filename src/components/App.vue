<template>
  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar class="app-sidebar"
            :current="current"
            @show="show"
            ></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" class="app-main-view">
        <historyview ref="historyview"
            :config="config"
            v-show='current.section == "local-branches" | current.section == "remote-branches" | current.section == "tags"'></historyview>
        <workspace ref="workspace"
            v-show='current.section == "workspace"'></workspace>
        <container
            clas="app-files-view"
            ref="container"
            v-show='current.section == "files"'
            :config="config"
            :is-git="false"></container>
    </pane>
    <error-dialog ref="errorDialog" @refresh="refresh"></error-dialog>
  </splitpanes>
</template>
<style>
html,
body {
    height: 100%;
    width: 100%;
}
body {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    margin: 0;
    font: 10pt sans-serif;
}
footer {
    display: none;
}
#global-container {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
}
#global-container .splitpanes.default-theme .splitpanes__splitter {
    background-color: #333333;
    border-left: 1px solid #333333 !important;
}
#global-container .splitpanes.default-theme .splitpanes__splitter::before {
    background-color: #666666;
    }
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
.vue-universal-modal {
    z-index: 100;
}
.btn .material-icons {
    margin-right: 0.5em;
}
</style>
<script>
import 'splitpanes/dist/splitpanes.css';
import 'vue-universal-modal/dist/index.css';
import '../css/material-icons.css';
import { defineComponent, ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import Sidebar from './Sidebar.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import HistoryView from './HistoryView.vue';
import Workspace from './Workspace.vue';
import ErrorDialog from './dialogs/ErrorDialog.vue';

export default defineComponent({
    components: {
        'splitpanes': Splitpanes,
        'pane': Pane,
        'sidebar': Sidebar,
        'container': FilesEditorContainer,
        'historyview': HistoryView,
        'workspace': Workspace,
        'error-dialog': ErrorDialog,
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
            sidebarSize: 190 * 100 / jQuery(document).width() // sidebar size (percentage)
        };
    },
    methods: {
        initViews() {
            // Init views
        },
        show(target) {
            this.current.section = target.id;
            if (target.id == 'files') {
                this.current.object = target.path;
                this.$refs.container.updateStack(target.path, target.type);
            } else if (target.id == 'workspace') {
                this.current.object = target.name;
                this.$refs.workspace.refresh();
            } else { // history (tags, local/remote branches)
                this.current.object = target.name;
                this.$refs.historyview.update(target);
            }
        },
        showError(message) {
            // Show error in modal message window
            this.$refs.errorDialog.showDialog({ message: message, type: 'error' });
        },
        showWarning(message) {
            // Show warning in modal message window
            this.$refs.errorDialog.showDialog({ message: message, type: 'warning' });
        },
    },
    mounted() {
        // Init
        this.initViews();
    }
})
</script>
