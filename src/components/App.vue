<template>
  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar class="app-sidebar"
            @show="show"
            :config="config"
            ></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" class="app-main">
        <div class="app-main-nav" v-show="activeTabs.length > 1 && !config.singleTab">
            <ul class="nav nav-tabs">
              <li role="presentation" v-for="tab in tabs" :class="selectedTab == tab.uuid ? 'active': ''">
                <a v-if="!tab.closed" href="#"
                    @click.stop="selectTab(tab)"
                    @contextmenu.prevent.stop="showMenu($event, tab)"
                    >{{ tab.name }} <i class='fa fa-close' @click.stop="closeTab(tab)"></i></a>
              </li>
            </ul>
            <vue-simple-context-menu
                element-id="app-main-nav-menu"
                :options="options"
                ref="appMainNavMenu"
                @option-clicked="menuOptionClicked"
            />
        </div>
        <div class="app-main-view">
            <template v-for="tab in tabs">
                <component
                    :is="tab.component"
                    :ref="tab.uuid"
                    :uuid="tab.uuid"
                    :config="config"
                    :target="tab.target"
                    :is-git="false"
                    @show="show"
                    @setTab="(event) => { tab.name = event.name; tab.target = event; }"
                    v-show="selectedTab == tab.uuid"
                    v-if="!tab.closed"></component>
            </template>
        </div>
    </pane>
    <error-dialog ref="errorDialog"></error-dialog>
    <close-tab-dialog ref="closeTabDialog"></close-tab-dialog>
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
.vue-simple-context-menu {
    background-color: #fff;
    font-size: 1em;
}
.vue-simple-context-menu .vue-simple-context-menu__item .material-icons {
    color: #666;
    font-size: 1.5em;
    margin-right: 0.5em;
}
.vue-simple-context-menu .vue-simple-context-menu__item:hover .material-icons {
    color: #fff;
}
.vue-simple-context-menu__divider {
    height: 1px;
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
import VueSimpleContextMenu from 'vue-simple-context-menu';
import Sidebar from './Sidebar.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import HistoryView from './HistoryView.vue';
import Workspace from './Workspace.vue';
import ErrorDialog from './dialogs/ErrorDialog.vue';
import CloseTabDialog from './dialogs/CloseTabDialog.vue';

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
        'close-tab-dialog': CloseTabDialog,
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    data() {
        return {
            tabs: [],
            selectedTab: null, // selected tab
            config: {
                theme: localStorage.getItem('airflow_code_editor_theme') || 'default', // editor theme
                mode: localStorage.getItem('airflow_code_editor_mode') || 'default', // edit mode (default, vim, etc...)
                showHiddenFiles: localStorage.getItem('airflow_code_editor_show_hidden_files') == 'true',
                singleTab: false,
            },
            sidebarSize: 190 * 100 / jQuery(document).width(), // sidebar size (percentage)
            options: [
                {
                  name: '<span class="material-icons">close</span> Close',
                  slug: 'close',
                },
                {
                  name: '<span class="material-icons">cancel</span> Close other tabs',
                  slug: 'close_others',
                },
            ],
        };
    },
    methods: {
        initViews() {
            // Init views
        },
        show(target) {
            if (target.id == 'files') {
                let path = target.path != '/' ? target.path : undefined;
                let tab = this.tabs.find(tab => tab.target && tab.target.object == path && tab.target.type == target.type && !tab.closed);
                if (tab) {
                    if (target.type == 'tree') {
                        this.$refs[tab.uuid][0].refresh();
                    }
                } else {
                    tab = new TabState(target.path, FilesEditorContainer, target);
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else if (target.id == 'workspace') {
                let tab = this.tabs.find(tab => tab.uuid == WORKSPACE_UUID && !tab.closed);
                if (tab) {
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState('Workspace', Workspace);
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else { // history (tags, local/remote branches)
                let tab = this.tabs.find(tab => tab.target && tab.target.id == target.id && tab.target.name == target.name && !tab.closed);
                if (tab) {
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState(target.name, HistoryView, target);
                    this.tabs.push(tab);
                }
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
        showMenu(event, tab) {
            // Show tab menu
            if (tab) {
                this.$refs.appMainNavMenu.showMenu(event, tab);
            }
        },
        async menuOptionClicked(event) {
            // Menu click
            if (event.option.slug == 'close_others') {
                for (const tab of this.tabs.filter(x => x != event.item && !x.closed)) {
                    await this.closeTab(tab);
                }
            } else if (event.option.slug == 'close') {
                await this.closeTab(event.item);
            }
        },
        selectTab(tab) {
            // Set active tab
            this.selectedTab = tab.uuid;
        },
        isChanged(tab) {
            if (tab) {
                return this.$refs[tab.uuid][0].isChanged();
            } else {
                return false;
            }
        },
        async closeTab(tab) {
            // Close a tab
            if (this.isChanged(tab)) {
                // Show confirm dialog
                if (!await this.$refs.closeTabDialog.showDialog(tab.name)) {
                    return;
                }
            }
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
