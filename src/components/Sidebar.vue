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
import TreeView from '@grapoza/vue-tree';
import { prepareHref, splitPath, getIcon } from '../commons';

export default {
    props: [ 'stack', 'current', 'historyView', 'workspaceView' ],
    components: {
        tree: TreeView
    },
    data: function () {
        return {
            model: [],
            modelDefaults: {
                loadChildrenAsync: this.loadChildrenAsync
            }
        }
    },
    methods: {
        parseURIFragment: function() {
            // Change the active section according to the uri fragment (hash)
            let self = this;
            return new Promise(function(resolve, reject) {
                let match = /#?([a-z-]+)(\/(.*))?/.exec(document.location.hash);
                let section = match !== null ? match[1] : 'files';
                let object = match !== null ? match[3] : null;

                if (section == 'tags' || section == 'local-branches' || section == 'remote-branches') {
                    self.current.section = section;
                    self.current.object = object;
                    self.historyView.update({ id: section, name: object });

                } else if (section == 'workspace') {
                    self.current.section = section;
                    self.current.object = null;
                    self.workspaceView.update([ 'stage' ]);

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
        showContainer: function() {
            // Show global container
            let self = this;
            jQuery('#global-container').show();
            return(Promise.resolve(true));
        },
        fetchTree: function() {
            // Load tree nodes
            let self = this;
            return new Promise(function(resolve, reject) {
                jQuery.get(prepareHref('tree'))
                      .done(function(data) {
                            self.model.length = 0; // flush model
                            data.value.forEach(function(part) {
                                part.label = part.label || part.id;
                                part.treeNodeSpec = {
                                    'expandable': !part.leaf,
                                }
                                if (!part.leaf) {
                                    part.children = [];
                                }
                                self.model.push(part);
                            });
                            resolve(true);
                      })
                      .fail(function(jqXHR, textStatus, errorThrown) {
                            reject();
                      })
                });
        },
        click: function(model) {
            let self = this;
            let sectionAndName = splitPath(model.id);
            let section = sectionAndName[0];
            let name = sectionAndName[1];
            if (section == 'workspace' || section == 'git') { // Workspace
                self.current.section = 'workspace';
                self.current.object = name;
                self.workspaceView.update([ 'stage' ]);

            } else if (section == 'files') { // Files
                self.current.section = section
                self.current.object = '/' + name;
                self.stack.updateStack('/' + name, model.leaf ? 'blob' : 'tree');

            } else if (section == 'tags' ||
                       section == 'remote-branches' ||
                       section == 'local-branches') {
                if (name) {
                    self.current.section = section;
                    self.current.object = name;
                    self.historyView.update({ id: section, name: name });
                } else {
                    jQuery('#sidebar-tree-' + section + '-exp').click();
                }
            }
            return false;
        },
        loadChildrenAsync: function(parent) {
            let self = this;
            return new Promise(function(resolve, reject) {
                jQuery.get(prepareHref('tree/' + parent.id))
                      .done(function(data) {
                            data.value.forEach(function(part) {
                                part.label = part.label || part.id;
                                if (!part.icon || part.icon == 'fa-file') {
                                    part.icon = getIcon(part.type, part.label);
                                }
                                part.treeNodeSpec = {
                                    'expandable': !part.leaf,
                                }
                                if (!part.leaf) {
                                    part.children = [];
                                }
                                part.id = parent.id + '/' + part.id;
                            });
                            resolve(data.value);
                      })
                      .fail(function(jqXHR, textStatus, errorThrown) {
                            reject();
                      })
                });
        },
    },
    mounted: function() {
        // Init
        let self = this;
        self.fetchTree()
            .then(self.parseURIFragment)
            .then(self.showContainer);
    }
}
</script>
