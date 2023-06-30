<template>
    <div class="tree-view">
        <ol class="breadcrumb">
          <breadcrumb @changePath="changePath" :stack="stack" :isGit="isGit" v-if="showBreadcrumb"></breadcrumb>
          <div class="breadcrumb-buttons">
              <button v-on:click="newAction()" v-if="!isGit" type="button" class="btn btn-primary"><icon icon="add_circle"/> New</button>
              <button v-on:click="uploadAction()" v-if="!isGit" type="button" class="btn btn-primary"><icon icon="file_upload"/> Upload</button>
              <input type="file" multiple="multiple" style="display: none" ref="file" @change="handleUploadButton" />
          </div>
        </ol>

        <div class="tree-view-tree-content"
             @dragenter.stop.prevent="isDragEnter = true"
             @dragover.stop.prevent="() => {}"
             @dragleave.stop.prevent="isDragEnter = false"
             @drop.stop.prevent="handleDrop"
             @contextmenu.prevent.stop="showMenu($event, null)">
            <vue-good-table
              :fixed-header="true"
              max-height="100%"
              :columns="columns"
              :rows="items">
              <template #table-row="props">
                <div @contextmenu.prevent.stop="showMenu($event, props.row)">
                  <span v-if="props.column.field == 'name'" :class="props.column.field">
                    <a v-on:click.prevent="changePath(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')">
                      {{ props.row.name }}
                    </a>
                  </span>
                  <span v-else-if="props.column.field == 'icon'" :class="props.column.field">
                    <a v-on:click.prevent="changePath(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')">
                      <icon :icon="props.row.icon"/>
                    </a>
                  </span>
                  <span v-else-if="props.column.field == 'action'" class="btn-group">
                    <a v-if="props.row.type == 'blob'" class="download btn btn-default btn-sm" title="Download" :href="props.row.downloadHref"><icon icon="file_download"/></a>
                    <a v-if="(!props.row.isGit) && (props.row.type == 'blob' || props.row.size == 0)" class="trash-o btn btn-default btn-sm" title="Delete" target="_blank" v-on:click.prevent="showDeleteDialog(props.row)" :href="props.row.href"><icon icon="delete"/></a>
                    <a v-if="!props.row.isGit && (props.row.name != '..')" class="i-cursor btn btn-default btn-sm" title="Move/Rename" target="_blank" v-on:click.prevent="showRenameDialog(props.row)" :href="props.row.href"><icon icon="drive_file_rename_outline"/></a>
                    <a v-if="!props.row.isGit && (props.row.name != '..')" class="external-link btn btn-default btn-sm" title="Open in a new window" target="_blank" :href="props.row.href"><icon icon="open_in_new"/></a>
                  </span>
                  <span v-else-if="props.column.field == 'size'" :class="props.column.field">
                    {{ props.row.formattedSize }}
                  </span>
                  <span v-else :class="props.column.field">
                    {{ props.formattedRow[props.column.field] }}
                  </span>
                </div>
              </template>
            </vue-good-table>
        </div>
        <rename-dialog ref="renameDialog"></rename-dialog>
        <delete-dialog ref="deleteDialog"></delete-dialog>
        <vue-simple-context-menu
            :element-id="'files-menu-' + uuid"
            :options="options"
            ref="filesMenu"
            @option-clicked="menuOptionClicked"
        />
    </div>
</template>
<style>
.tree-view {
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    height: 100%;
}
.tree-view .breadcrumb {
    padding: 0.5rem 1rem 0.5rem 1rem;
    margin-bottom: 0;
    border-radius: 0px;
}
.tree-view .breadcrumb li {
    margin-top: 0.6rem;
    margin-bottom: 0.6rem;
}
.tree-view .breadcrumb a {
    text-decoration: none;
    cursor: pointer;
}
.tree-view .breadcrumb-buttons {
    float: right;
}
.tree-view .breadcrumb-buttons .btn {
    margin-left: 0.5em;
}
.tree-view-tree-content {
    margin: 0;
    height: inherit;
    background-color: #fff;
}
.tree-view-tree-content a:hover {
    text-decoration: none;
}
.tree-view-tree-content .icon {
    line-height: 2em;
}
.tree-view-tree-content .icon a,
.tree-view-tree-content .name a,
.tree-view-tree-content .action a {
    color: inherit;
}
.tree-view .tree-item-symlink {
    font-style: italic;
}
.tree-view-tree-content .btn .material-icons {
    margin-right: 0;
}
</style>
<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import { VueGoodTable } from 'vue-good-table-next';
// import 'vue-good-table-next/dist/vue-good-table-next.css';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import { basename, normalize, prepareHref, git_async, showError } from '../commons';
import { TreeEntry, prepareMenuOptions } from '../tree_entry';
import Icon from './Icon.vue';
import Breadcrumb from './Breadcrumb.vue';
import RenameDialog from './dialogs/RenameDialog.vue';
import DeleteDialog from './dialogs/DeleteDialog.vue';

function filenameCompare(a, b) {
    return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
}

export default defineComponent({
    components: {
        'icon': Icon,
        'breadcrumb': Breadcrumb,
        'vue-good-table': VueGoodTable,
        'rename-dialog': RenameDialog,
        'delete-dialog': DeleteDialog,
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    props: [ 'stack', 'config', 'isGit', 'showBreadcrumb', 'uuid' ],
    data() {
        return {
            items: [], // tree items (blobs/trees)
            isDragEnter: false,
            columns: [
                {
                  label: '',
                  field: 'icon',
                  width: '20px',
                  sortable: true
                },
                {
                  label: 'Name',
                  field: 'name',
                  thClass: 'vgt-right-align',
                  filterOptions: {
                      enabled: true
                  }
                },
                {
                  label: 'Modified',
                  field: 'mtime',
                  thClass: 'vgt-right-align',
                  tdClass: 'vgt-right-align',
                  filterOptions: {
                      enabled: true
                  }
                },
                {
                  label: 'Size',
                  field: 'size',
                  thClass: 'vgt-right-align',
                  type: 'number'
                },
                {
                  label: 'Actions',
                  field: 'action',
                  thClass: 'vgt-right-align',
                  tdClass: 'vgt-right-align',
                  sortable: false
                }
            ],
            options: [],
        }
    },
    methods: {
        async showRenameDialog(item) {
            // Show Move/Rename file dialog
            let target = await this.$refs.renameDialog.showDialog(item.object);
            if (target) {
                target = normalize(target);
                if (target == "/") {
                    showError('Invalid filename');
                } else if (this.source != target) {
                    await git_async([ 'mv-local', item.object, target ]);
                    this.refresh();
                }
            }
        },
        async showDeleteDialog(item) {
            // Show Delete file dialog
            const target = await this.$refs.deleteDialog.showDialog(item.object);
            if (target) {
                await git_async([ 'rm-local', target ]);
                this.refresh();
            }
        },
        newAction() {
            // New file button action
            const item = { name: '✧', type: 'blob', object: (this.stack.last().object || '') + '/✧' };
            this.changePath(item);
        },
        uploadAction() {
            // Upload button action
            this.$refs.file.click();
        },
        changePath(item) {
            // Change File/directory
            this.$emit('changePath', item);
        },
        async refresh() {
            console.log("Files.refresh");
            // Update tree view
            let path = null;
            const last = this.stack.last();
            if (last.type != 'blob') {
                if (this.isGit) { // git
                    path = 'tree' + normalize('git/' + last.object);
                } else { // local
                    path = 'tree' + normalize('files' + (last.object || ''));
                }
                // Get tree items
                try {
                    const params = this.config.showHiddenFiles ? { long: true, all: true } : { long : true };
                    const response = await axios.get(prepareHref(path), { params: params });
                    let blobs = []; // files
                    let trees = []; // directories
                    response.data.value.forEach((part) => {
                        let item = new TreeEntry(part, this.isGit, last.object);
                        if (item.type == 'tree') {
                            trees.push(item);
                        } else {
                            blobs.push(item);
                        }
                    });
                    // Sort files and directories
                    blobs.sort(filenameCompare);
                    trees.sort(filenameCompare);
                    // Add link to parent directory on top
                    if (!this.stack.isRoot()) {
                        if (this.isGit) {
                            trees.unshift({ type: 'tree', name: '..', isSymbolicLink: false, icon: 'folder', href: '#' });
                        } else {
                            trees.unshift({ ...this.stack.parent(), name: '..', icon: 'folder', href: '#' });
                        }
                    }
                    this.items = trees.concat(blobs);
                    this.$emit('loaded', false); // close the spinner
                } catch(error) {
                    this.$emit('loaded', false); // close the spinner
                    console.log(error);
                }
            }
        },
        handleDrop($event) {
            // Upload files (drag and drop)
            this.isDragEnter = false;
            // Convert FileList into Array
            const files = [...$event.dataTransfer.files];
            this.uploadFiles(files);
        },
        handleUploadButton($event) {
            // Upload files (upload button)
            const files = Array.from($event.target.files);
            this.uploadFiles(files);
            $event.target.value = '';
        },
        async uploadFiles(files) {
            // Upload files
            if (!this.isGit) {
                for (const file of files){
                    const filename = normalize((this.stack.last().object || '') + '/' + basename(file.name));
                    const payload = file;
                    const options = {
                        headers: {
                            'Content-Type': file.type
                        }
                    };
                    // Upload file
                    try {
                        await axios.post(prepareHref('files' + filename), payload, options);
                        this.refresh();
                    } catch(error) {
                        console.log(error);
                    }
                };
            }
        },
        showMenu(event, item) {
            // Prepare the menu
            this.options = prepareMenuOptions(item, this.isGit, this.config.showHiddenFiles);
            // Show menu
            this.$refs.filesMenu.showMenu(event, item);
        },
        menuOptionClicked(event) {
            if (event.option.slug == 'open') {
                this.changePath(event.item);
            } else if (event.option.slug == 'download') {
                window.open(event.item.downloadHref);
            } else if (event.option.slug == 'delete') {
                this.showDeleteDialog(event.item);
            } else if (event.option.slug == 'rename') {
                this.showRenameDialog(event.item);
            } else if (event.option.slug == 'open_in_new') {
                window.open(event.item.href, '_blank');
            } else if (event.option.slug == 'refresh') {
                this.refresh();
            } else if (event.option.slug == 'show_hidden') {
                // Save setting on the local storage
                this.config.showHiddenFiles = !this.config.showHiddenFiles;
                localStorage.setItem('airflow_code_editor_show_hidden_files', this.config.showHiddenFiles);
                this.refresh();
            } else if (event.option.slug == 'new') {
                this.newAction();
            } else if (event.option.slug == 'upload') {
                this.uploadAction();
            }
        }
    },
    mounted() {
        this.refresh();
    }
})
</script>
