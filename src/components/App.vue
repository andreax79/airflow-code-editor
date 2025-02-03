<template>
  <notifications position="bottom right" />
  <splitpanes class="default-theme">
    <pane key="1" :size="sidebarSize">
        <sidebar class="app-sidebar"
            @show="show"
            :config="config"
            :bookmarks="bookmarks"
            ref="sidebar"
            ></sidebar>
    </pane>
    <pane key="2" :size="100 - sidebarSize" class="app-main">
        <div class="app-main-nav" v-show="activeTabs.length > 1 && !config.singleTab">
            <ul class="tabs">
              <li role="presentation" v-for="tab in tabs" :class="selectedTab == tab.uuid ? 'active': ''">
                <a v-if="!tab.closed" href="#"
                    @click.stop="selectTab(tab)"
                    @contextmenu.prevent.stop="showMenu($event, tab)"
                    >{{ tab.name }} <i class='fa fa-close' @click.stop="closeTab(tab)"></i></a>
              </li>
            </ul>
            <vue-simple-context-menu
                element-id="app-main-nav-menu"
                :options="menuOptions"
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
/* Menu */
.vue-simple-context-menu {
    border-radius: 5px;
    background-color: #fff;
    font-size: 1em;
}
.vue-simple-context-menu .vue-simple-context-menu__item {
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
import '../css/dialogs.css';
import '../css/tabs.css';
import '../css/buttons.css';
import '../css/dark-theme.css';
import '../css/material-icons.css';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { defineComponent, ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import { setColor, prepareHref, splitPath, EDITOR_THEME_KEY, EDITOR_MODE_KEY, EDITOR_COLOR_KEY, SHOW_HIDDEN_FILES_KEY, BOOKMARKS_KEY, WORKSPACE_UUID } from "../commons";
import { TabState } from '../tabs.js';

import VueSimpleContextMenu from 'vue-simple-context-menu';
import Sidebar from './Sidebar.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import HistoryView from './HistoryView.vue';
import Search from './Search.vue';
import Workspace from './Workspace.vue';
import ErrorDialog from './dialogs/ErrorDialog.vue';
import CloseTabDialog from './dialogs/CloseTabDialog.vue';

export default defineComponent({
    components: {
        'splitpanes': Splitpanes,
        'pane': Pane,
        'sidebar': Sidebar,
        'container': FilesEditorContainer,
        'historyview': HistoryView,
        'workspace': Workspace,
        'search': Search,
        'error-dialog': ErrorDialog,
        'close-tab-dialog': CloseTabDialog,
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    data() {
        return {
            tabs: [],
            selectedTab: null, // selected tab
            config: {
                theme: localStorage.getItem(EDITOR_THEME_KEY) || 'default', // editor theme
                mode: localStorage.getItem(EDITOR_MODE_KEY) || 'default', // edit mode (default, vim, etc...)
                color: localStorage.getItem(EDITOR_COLOR_KEY) || 'Light', // light/dark mode
                showHiddenFiles: localStorage.getItem(SHOW_HIDDEN_FILES_KEY) == 'true',
                singleTab: false,
            },
            sidebarSize: 190 * 100 / document.documentElement.clientWidth, // sidebar size (percentage)
            menuOptions: [],
        };
    },
    methods: {
        initViews() {
            // Init views
            setColor(this.config.color);
        },
        async open(path) {
            if (!path.startsWith('/')) {
                path = '/' + path;
            }
            const response = await axios.head(prepareHref('tree/files' + path));
            const exists = response.headers['x-exists'] == 'true';
            const leaf = response.headers['x-leaf'] == 'true';
            const sectionAndName = splitPath(response.headers['x-id']);
            const section = sectionAndName[0];
            const name = '/' + (sectionAndName[1] || '').trim();
            if (leaf || !exists) {
                this.show({ id: section, path: name, type: 'blob' });
            } else {
                this.show({ id: section, path: name, type: 'tree' });
            }
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
                    tab = new TabState(target.path, FilesEditorContainer, target, uuidv4());
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else if (target.id == 'workspace') {
                let tab = this.tabs.find(tab => tab.uuid == WORKSPACE_UUID && !tab.closed);
                if (tab) {
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState('Workspace', Workspace, target, WORKSPACE_UUID);
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else if (target.id == 'search') {
                let tab = this.tabs.find(tab => tab.target && tab.target.id == target.id && tab.target.query == target.query && !tab.closed);
                if (tab) {
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState(target.path, Search, target, uuidv4());
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            } else { // history (tags, local/remote branches)
                let tab = this.tabs.find(tab => tab.target && tab.target.id == target.id && tab.target.name == target.name && !tab.closed);
                if (tab) {
                    this.$refs[tab.uuid][0].refresh();
                } else {
                    tab = new TabState(target.name, HistoryView, target, uuidv4());
                    this.tabs.push(tab);
                }
                this.selectedTab = tab.uuid;
            }
        },
        showError(message, options) {
            // Show modal message window
            options = (options !== undefined) ? options : {};
            options['message'] = message;
            options['type'] = options.type || 'error';
            console.log(options);
            this.$refs.errorDialog.showDialog(options);
        },
        showMenu(event, tab) {
            // Show tab menu
            if (tab) {
                this.menuOptions = this.prepareMenuOptions(tab);
                this.$refs.appMainNavMenu.showMenu(event, tab);
            }
        },
        prepareMenuOptions(tab) {
            // Prepare tab menu options
            const label = tab.isBookmarked() ? 'Remove bookmark' : 'Bookmark tab';
            return [
                {
                    name: '<span class="material-icons">bookmark</span> ' + label,
                    slug: 'bookmark',
                },
                {
                    type: 'divider'
                },
                {
                    name: '<span class="material-icons">close</span> Close',
                    slug: 'close',
                },
                {
                    name: '<span class="material-icons">cancel</span> Close other tabs',
                    slug: 'close_others',
                },
            ];
        },
        async menuOptionClicked(event) {
            // Menu click
            switch (event.option.slug) {
                case 'bookmark':
                    if (event.item.isBookmarked()) {
                        event.item.removeBookmark();
                    } else {
                        event.item.addBookmark();
                    }
                    // Refresh bookmarks in the sidebar
                    this.$refs.sidebar.refreshBookmarks();
                    break;
                case 'close_others':
                    for (const tab of this.tabs.filter(x => x != event.item && !x.closed)) {
                        await this.closeTab(tab);
                    }
                    break;
                case 'close':
                    await this.closeTab(event.item);
                    break
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
