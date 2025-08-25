<template>
    <div>
        <div class="sidebar-content">
            <tree id="sidebar-tree"
                  :initial-model="model"
                  :model-defaults="modelDefaults">
                <template #text="{ model }">
                    <div :title="model.treeNodeSpec.title"
                         class="grtvn-self-text"
                         @contextmenu.prevent.stop="showMenu($event, model)"
                         v-on:click="click(model)">
                         <icon :icon="model.icon" />
                         {{ model.label }}
                    </div>
                </template>
            </tree>
            <span class="bug-report">
               <a href="https://github.com/andreax79/airflow-code-editor/issues" target="_blank"><icon icon="bug_report"/> Report an issue</a>
            </span>
        </div>
        <vue-simple-context-menu
            element-id="sidebar-tree-menu"
            :options="menuOptions"
            ref="sidebarTreeMenu"
            @option-clicked="menuOptionClicked"
        />
    </div>
</template>
<style>
.sidebar-content {
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    height: 100%;
    overflow-x: auto;
    overflow-y: auto;
    cursor: default;
    color: #eeeeee;
    padding: 1em;
}
.sidebar-content .bug-report {
    position: absolute;
    z-index: 10;
    bottom: 5px;
    left: 5px;
}
.sidebar-content .bug-report a {
    color: #ddd;
}
.sidebar-content .bug-report .material-icons {
    margin-right: 0;
}
.grtv-wrapper.grtv-default-skin .grtvn-self {
    line-height: inherit;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import { TreeView } from '@grapoza/vue-tree';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import { prepareHref, splitPath, showNotification, parseErrorResponse } from '../commons';
import { getIcon } from '../tree_entry';
import { getBookmarks, findBookmark, removeBookmark } from '../bookmarks.js';
import Icon from './Icon.vue';

export default defineComponent({
    components: {
        'icon': Icon,
        'tree': TreeView,
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    props: [ 'config' ],
    data() {
        return {
            model: ref([]),
            modelDefaults: {
                loadChildrenAsync: this.loadChildrenAsync
            },
            menuOptions: [],
        }
    },
    methods: {
        async parseURIFragment() {
            // Change the active section according to the uri fragment (hash)
            const match = /#?([a-z-]+)(\/(.*))?/.exec(document.location.hash);
            const section = match !== null ? match[1] : 'files';
            const object = match !== null ? match[3] : null;

            if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                this.$emit("show", { id: section, name: object });

            } else if (section == 'workspace') {
                this.$emit("show", { id: 'workspace', name: name });

            } else if (section == 'edit' && object) {
                this.$emit("show", { id: 'files', path: '/' + object, type: 'blob' });

            } else { // files
                if (object) {
                    this.$emit("show", { id: 'files', path: '/' + object, type: 'tree' });
                } else {
                    this.$emit("show", { id: 'files', path: '/', type: 'tree' });
                }
            }
        },
        async showContainer() {
            // Show global container
            document.querySelector('#global-container').style.display='block';
        },
        async fetchTree() {
            // Load tree nodes
            const response = await axios.get(prepareHref('tree'));
            this.model.length = 0; // flush model
            response.data.value.forEach((node) => {
                node = this.prepareTreeNode(node);
                this.model.push(node);
            });
            // Add the bookmarks node
            let bookmarksNode = {
                "id": "bookmarks",
                "label": "Bookmarks",
                "leaf": false,
                "icon": "bookmark",
                "type": "tree",
                "treeNodeSpec": {
                    "expandable": true,
                }
            };
            this.model.push(bookmarksNode);
        },
        click(model) {
            const sectionAndName = splitPath(model.id);
            const section = sectionAndName[0];
            const name = (sectionAndName[1] || '').trim();
            console.log('Sidebar.click section: ' + section + ' name: ' + name);

            switch (section) {
                case 'workspace': // Workspace
                case 'git':
                    this.$emit("show", { id: 'workspace', name: name });
                    break;
                case 'files': // Files
                    this.$emit("show", { id: 'files', path: '/' + name, type: model.type == 'blob' ? 'blob' : 'tree' });
                    break;
                case 'tags': // Git tags
                case 'remote-branches': // Git remote branches
                case 'local-branches': // Git local branches
                    if (name) {
                        this.$emit("show", { id: section, name: name });
                    } else {
                        // Open tree node
                        document.getElementById(`sidebar-tree-${section}-exp`).click();
                    }
                    break;
                case 'bookmarks':
                    // Open tree node
                    document.getElementById(`sidebar-tree-${section}-exp`).click();
                    break;
            }
            return false;
        },
        prepareTreeNode(node, parent) {
            node.label = node.label || node.id;
            node.type = node.leaf ? 'blob' : 'tree';
            if (!node.icon || node.icon == 'file') {
                node.icon = getIcon(node.label, node.type);
            }
            node.treeNodeSpec = {
                'expandable': !node.leaf,
            }
            if (!node.leaf) {
                node.children = [];
            }
            if (parent) {
                node.id = parent.id + '/' + node.id;
                node.section = parent.id;
            }
            return node;
        },
        loadBookmarks() {
            // Populate bookmarks from local storage
            const bookmarks = getBookmarks();
            return bookmarks.map((bookmark) => {
                // Prepare a tree node for each bookmark
                if (!bookmark) {
                    return null;
                }
                let node = {
                    "id": '',
                    "leaf": true,
                    "icon": "bookmark",
                    "label": '',
                    "section": 'bookmarks',
                    "treeNodeSpec": {
                        "expandable": false,
                    }
                };
                switch (bookmark.id) {
                    case 'workspace': // Workspace
                    case 'git':
                        node.id = 'workspace';
                        node.label = 'Workspace';
                        node.icon = 'work';
                        break;
                    case 'files': // Files
                        if (!bookmark.path) {
                            return null;
                        }
                        node.id = 'files' + bookmark.path;
                        node.type = bookmark.type;
                        node.label = bookmark.path.split('/').pop() || '/';
                        node.icon = (bookmark.type == 'blob') ? 'file' : 'folder';
                        break;
                    case 'tags': // Git tags
                        node.id = bookmark.id + '/' + bookmark.name;
                        node.label = bookmark.name;
                        node.icon = 'style';
                        break;
                    case 'remote-branches': // Git remote branches
                        node.id = bookmark.id + '/' + bookmark.name;
                        node.label = bookmark.name;
                        node.icon = 'public';
                        break;
                    case 'local-branches': // Git local branches
                        node.id = bookmark.id + '/' + bookmark.name;
                        node.label = bookmark.name;
                        node.icon = 'fork_right';
                        break;
                }
                return node;
            }).filter(x => !!x);
        },
        async loadChildrenAsync(parent) {
            // Load children of a tree node
            if (parent.id == 'bookmarks') {
                // Load bookmarks from local storage
                return this.loadBookmarks();
            } else {
                // Load children from the server
                const self = this;
                const path = 'tree/' + parent.id;
                const params = this.config.showHiddenFiles ? { all: true } : {};
                try {
                    const response = await axios.get(prepareHref(path), { params: params });
                    return response.data.value.map((node) => self.prepareTreeNode(node, parent));
                } catch(error) {
                    const message = parseErrorResponse(error, 'Error loading tree');
                    showNotificentry_numberation({ message: message, title: 'Load' });
                    return [];
                }
            }
        },
        async showMenu(event, item) {
            // Show sidebar menu
            this.menuOptions = this.prepareMenuOptions(item);
            if (this.menuOptions.length > 0) {
                this.$refs.sidebarTreeMenu.showMenu(event, item);
            }
        },
        prepareMenuOptions(item) {
            // Prepare tab menu options
            if (!item) {
                return [];
            } else if (item.section == 'bookmarks') {
                return [
                    {
                        name: '<span class="material-icons">bookmark</span> Remove bookmark',
                        slug: 'removeBookmark',
                    }
                ];
            } else if (!item.leaf) {
                return [
                    {
                      name: '<span class="material-icons">refresh</span> Refresh',
                      slug: 'refresh',
                    },
                ];
            } else {
                return [];
            }
        },
        menuOptionClicked(event) {
            // Menu click
            if (event.option.slug == 'refresh') {
                this.menuOptionRefresh(event);
            }
            else if (event.option.slug == 'removeBookmark') {
                this.menuOptionRemoveBookmark(event);
            }
        },
        menuOptionRefresh(event) {
            // Menu click on Refresh
            if (!event.item.treeNodeSpec.expandable) {
                return;
            }
            // Close
            event.item.treeNodeSpec.state.expanded = false;
            event.item.children = [];
            event.item.treeNodeSpec._.state.areChildrenLoaded = false;
            // Reload
            setTimeout(async () => {
                let spec = event.item.treeNodeSpec;
                spec.state.expanded = true;
                // If children need to be loaded asynchronously, load them.
                if (spec.state.expanded && !spec._.state.areChildrenLoaded && !spec._.state.areChildrenLoading) {
                    spec._.state.areChildrenLoading = true;
                    const childrenResult = await spec.loadChildrenAsync(event.item);
                    if (childrenResult) {
                        spec._.state.areChildrenLoaded = true;
                        event.item.children.splice(0, event.item.children.length, ...childrenResult);
                    }
                    spec._.state.areChildrenLoading = false;
                }
            }, 1);
        },
        menuOptionRemoveBookmark(event) {
            // Menu click on Remove bookmark
            if (event.item.section != 'bookmarks') {
                return;
            }
            const sectionAndName = splitPath(event.item.id);
            const id = sectionAndName[0];
            const name = (sectionAndName[1] || '').trim();
            const bookmark = findBookmark(id, name);
            if (bookmark) {
                removeBookmark(bookmark);
                this.refreshBookmarks();
            }
        },
        refreshBookmarks() {
            // Refresh bookmarks
            const bookmarks = this.model.at(-1);  // bookmarks node is the last one
            const event = { item: bookmarks };
            this.menuOptionRefresh(event);
        }
    },
    async mounted() {
        // Init
        await this.fetchTree();
        await this.parseURIFragment();
        await this.showContainer();
    }
})
</script>
