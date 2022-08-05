<template>
    <div>
        <div id="sidebar-content">
            <tree id="sidebar-tree"
                  :initial-model="model"
                  :model-defaults="modelDefaults">
                <template #text="{ model, customClasses }">
                    <div :title="model.treeNodeSpec.title"
                         class="grtvn-self-text"
                         v-on:click="click(model)"
                         :class="customClasses.treeViewNodeSelfText">
                         <i v-if="model.icon" :class="'fa ' + model.icon" aria-hidden="true"></i>
                         {{ model.label }}
                    </div>
                </template>
            </tree>
        </div>
    </div>
</template>
<script>
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import TreeView from '@grapoza/vue-tree';
import { prepareHref, splitPath } from '../commons';
import { getIcon } from '../tree_entry';

export default defineComponent({
    props: [ 'stack', 'historyState', 'current', 'workspaceView' ],
    components: {
        tree: TreeView
    },
    data() {
        return {
            model: ref([]),
            modelDefaults: {
                loadChildrenAsync: this.loadChildrenAsync
            }
        }
    },
    methods: {
        parseURIFragment() {
            // Change the active section according to the uri fragment (hash)
            const self = this;
            return new Promise((resolve, reject) => {
                const match = /#?([a-z-]+)(\/(.*))?/.exec(document.location.hash);
                const section = match !== null ? match[1] : 'files';
                const object = match !== null ? match[3] : null;

                if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                    self.current.section = section;
                    self.current.object = object;
                    self.historyState.update({ id: section, name: object });

                } else if (section == 'workspace') {
                    self.current.section = section;
                    self.current.object = null;
                    self.workspaceView.update();

                } else if (section == 'edit' && object) {
                    self.current.section = 'files';
                    self.current.object = '/' + object.split('/')[0];
                    self.stack.updateStack('/' + object, 'blob');

                } else { // files
                    self.current.section = 'files';
                    if (object) {
                        self.current.object = '/' + object.split('/')[0];
                        self.stack.updateStack('/' + object, 'tree');
                    } else {
                        self.current.object = null;
                        self.stack.updateStack('/', 'tree');
                    }
                }
                resolve(true);
            });
        },
        showContainer() {
            // Show global container
            const self = this;
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
            const self = this;
            const sectionAndName = splitPath(model.id);
            const section = sectionAndName[0];
            const name = (sectionAndName[1] || '').trim();
            console.log('Sidebar.click section: ' + section + ' name: ' + name);
            if (section == 'workspace' || section == 'git') { // Workspace
                self.current.section = 'workspace';
                self.current.object = name;
                self.workspaceView.update();

            } else if (section == 'files') { // Files
                self.current.section = section
                self.current.object = '/' + name;
                self.stack.updateStack('/' + name, model.leaf ? 'blob' : 'tree');

            } else if (section == 'tags' ||
                       section == 'remote-branches' ||
                       section == 'local-branches') { // Git tags/branches
                if (name) {
                    self.current.section = section;
                    self.current.object = name;
                    self.historyState.update({ id: section, name: name });
                } else {
                    // Open tree node
                    jQuery('#sidebar-tree-' + section + '-exp').click();
                }
            }
            return false;
        },
        prepareTreeNode(node, parent) {
            const self = this;
            node.label = node.label || node.id;
            node.type = node.leaf ? 'blob' : 'tree';
            if (!node.icon || node.icon == 'fa-file') {
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
        }
    },
    mounted() {
        // Init
        const self = this;
        self.fetchTree()
            .then(self.parseURIFragment)
            .then(self.showContainer)
    }
})
</script>
