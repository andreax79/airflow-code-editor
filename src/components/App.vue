<template>
  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar class="app-sidebar"
            @show="show"
            ></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" class="app-main">
        <div class="app-main-nav" v-show="activeTabs.length > 1">
            <ul class="nav nav-tabs">
              <li role="presentation" v-for="tab in tabs" :class="selectedTab == tab.uuid ? 'active': ''">
                <a v-if="!tab.closed" href="#" @click.stop="selectTab(tab)">{{ tab.name }} <i class='fa fa-close' @click.stop="closeTab(tab)"></i></a>
              </li>
            </ul>
        </div>
        <div class="app-main-view">
            <template v-for="tab in tabs">
                <component
                    :is="tab.component"
                    :ref="tab.uuid"
                    :config="config"
                    :target="tab.target"
                    :is-git="false"
                    @setTabTitle="(event) => tab.name = event.name"
                    v-show="selectedTab == tab.uuid"
                    v-if="!tab.closed"></component>
            </template>
        </div>
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
.app-main {
    height: 100%;
    display: flex;
    flex-direction: column;
}
.app-main-nav {
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
import 'vue-simple-context-menu/dist/vue-simple-context-menu.css';
import '../css/material-icons.css';
import { v4 as uuidv4 } from 'uuid';
import { defineComponent, ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import Sidebar from './Sidebar.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import HistoryView from './HistoryView.vue';
import Workspace from './Workspace.vue';
import ErrorDialog from './dialogs/ErrorDialog.vue';

const WORKSPACE_UUID = 'd15216ca-854d-4705-bff5-1887e8bf1180';

class TabState {
    constructor(name, component, target) {
        if (component == Workspace) {
            this.uuid = WORKSPACE_UUID;
        } else {
            this.uuid = uuidv4();
        }
        this.name = name;
        this.component = component;
        this.target = target;
        this.closed = false;
    }
}

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
            tabs: [],
            selectedTab: null, // selected tab
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
            if (target.id == 'files') {
                let tab = new TabState(target.path, FilesEditorContainer, target);
                this.tabs.push(tab);
                this.selectedTab = tab.uuid;
            } else if (target.id == 'workspace') {
                let tab = this.tabs.find(tab => tab.uuid == WORKSPACE_UUID && !tab.closed);
                if (tab) {
                    tab.closed = false;
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState('Workspace', Workspace);
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else { // history (tags, local/remote branches)
                let tab = new TabState(target.name, HistoryView, target);
                this.tabs.push(tab);
                this.selectedTab = tab.uuid;
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
        selectTab(tab) {
            // Set active tab
            this.selectedTab = tab.uuid;
        },
        closeTab(tab) {
            // Close a tab
            let tabIndex = this.activeTabs.indexOf(tab);
            if (tabIndex != -1) {
                // The user is closing the selected tab
                if (this.selectedTab == tab.uuid) {
                    this.selectedTab = null;
                    if (this.activeTabs.length == 1) { // No more tabs left
                        this.selectedTab = null;
                    } else if (tabIndex == 0) { // Select the first tab (first after deleting)
                        this.selectedTab = this.activeTabs[1].uuid;
                    } else { // Select the prev tab
                        this.selectedTab = this.activeTabs[tabIndex - 1].uuid;
                    }
                }
                // Mark the tab as closed
                tab.closed = true
            }
        },
    },
    computed: {
        activeTabs: function() {
            return this.tabs.filter((val, index, array) => !val.closed);
        }
    },
    mounted() {
        // Init
        this.initViews();
    }
})
</script>
