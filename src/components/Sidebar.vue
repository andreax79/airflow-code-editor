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
            :options="options"
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
import { prepareHref, splitPath } from '../commons';
import { getIcon } from '../tree_entry';
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
            options: [
                {
                  name: '<span class="material-icons">refresh</span> Refresh',
                  slug: 'refresh',
                },
            ],
        }
    },
    methods: {
        parseURIFragment() {
            // Change the active section according to the uri fragment (hash)
            return new Promise((resolve, reject) => {
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
                resolve(true);
            });
        },
        showContainer() {
            // Show global container
            jQuery('#global-container').show();
            return(Promise.resolve(true));
        },
        fetchTree() {
            // Load tree nodes
            const self = this;
            return new Promise((resolve, reject) => {
                axios.get(prepareHref('tree'))
                      .then((response) => {
                            self.model.length = 0; // flush model
                            response.data.value.forEach((node) => {
                                node = self.prepareTreeNode(node);
                                self.model.push(node);
                            });
                            resolve(true);
                      })
                      .catch(error => reject());
                });
        },
        click(model) {
            const sectionAndName = splitPath(model.id);
            const section = sectionAndName[0];
            const name = (sectionAndName[1] || '').trim();
            console.log('Sidebar.click section: ' + section + ' name: ' + name);
            if (section == 'workspace' || section == 'git') { // Workspace
                this.$emit("show", { id: 'workspace', name: name });

            } else if (section == 'files') { // Files
                this.$emit("show", { id: 'files', path: '/' + name, type: model.leaf ? 'blob' : 'tree' });

            } else if (section == 'tags' ||
                       section == 'remote-branches' ||
                       section == 'local-branches') { // Git tags/branches
                if (name) {
                    this.$emit("show", { id: section, name: name });
                } else {
                    // Open tree node
                    jQuery('#sidebar-tree-' + section + '-exp').click();
                }
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
            }
            return node;
        },
        loadChildrenAsync(parent) {
            const self = this;
            return new Promise((resolve, reject) => {
                axios.get(prepareHref('tree/' + parent.id))
                      .then((response) => resolve(response.data.value.map((node) => self.prepareTreeNode(node, parent))))
                      .catch(error => reject());
                });
        },
        showMenu(event, item) {
            // Show sidebar menu
            if (item && !item.leaf) {
                this.$refs.sidebarTreeMenu.showMenu(event, item);
            }
        },
        menuOptionClicked(event) {
            // Menu click
            if (event.option.slug == 'refresh') {
                this.menuOptionRefresh(event);
            }
        },
        menuOptionRefresh(event) {
            if (!event.item.treeNodeSpec.expandable) {
                return;
            }
            // Close
            event.item.treeNodeSpec.state.expanded = false;
            event.item.children = [];
            event.item.treeNodeSpec._.state.areChildrenLoaded = false;
            // Reload
            setTimeout(() => {
                let spec = event.item.treeNodeSpec;
                spec.state.expanded = true;
                // If children need to be loaded asynchronously, load them.
                if (spec.state.expanded && !spec._.state.areChildrenLoaded && !spec._.state.areChildrenLoading) {
                    spec._.state.areChildrenLoading = true;
                    spec.loadChildrenAsync(event.item)
                        .then((childrenResult) => {
                            if (childrenResult) {
                                spec._.state.areChildrenLoaded = true;
                                event.item.children.splice(0, event.item.children.length, ...childrenResult);
                            }
                            spec._.state.areChildrenLoading = false;
                        });
                }
            }, 1);
        },
    },
    mounted() {
        // Init
        this.fetchTree()
            .then(this.parseURIFragment)
            .then(this.showContainer)
    }
})
</script>
