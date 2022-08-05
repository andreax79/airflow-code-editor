<template>
    <div class="tree-view">
        <ol class="breadcrumb">
          <breadcrumb :stack="stack" :isGit="isGit" v-if="showBreadcrumb"></breadcrumb>
          <div class="breadcrumb-buttons">
              <button v-on:click="newAction()" v-if="!isGit" type="button" class="btn btn-default btn-sm">New <i class="fa fa-plus-square" aria-hidden="true"></i></button>
              <button v-on:click="uploadAction()" v-if="!isGit" type="button" class="btn btn-default btn-sm">Upload <i class="fa fa-cloud-upload" aria-hidden="true"></i></button>
              <input type="file" multiple="multiple" style="display: none" ref="file" @change="handleUploadButton" />
          </div>
        </ol>

        <div class="tree-view-tree-content"
             @dragenter.stop.prevent="isDragEnter = true"
             @dragover.stop.prevent="() => {}"
             @dragleave.stop.prevent="isDragEnter = false"
             @drop.stop.prevent="handleDrop">
            <vue-good-table
              :fixed-header="true"
              max-height="100%"
              :columns="columns"
              :rows="items">
              <template #table-row="props">
                <span v-if="props.column.field == 'name'" :class="props.column.field">
                  <a v-on:click.prevent="click(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')" >
                    {{ props.row.name }}
                  </a>
                </span>
                <span v-else-if="props.column.field == 'icon'" :class="props.column.field">
                  <a v-on:click.prevent="click(props.row)" :href="props.row.href" :class="'tree-item-' + props.row.type + ' ' + (props.row.isSymbolicLink ? 'tree-item-symlink' : '')" >
                    <i :class="'fa ' + props.row.icon" aria-hidden="true"></i>
                  </a>
                </span>
                <span v-else-if="props.column.field == 'action'" class="btn-group">
                  <a v-if="props.row.type == 'blob'" class="download btn btn-default btn-sm" title="Download" :href="props.row.downloadHref"><i class="fa fa-download" aria-hidden="true"></i></a>
                  <a v-if="(!props.row.isGit) && (props.row.type == 'blob' || props.row.size == 0)" class="trash-o btn btn-default btn-sm" title="Delete" target="_blank" v-on:click.prevent="deleteAction(props.row)" :href="props.row.href"><i class="fa fa-trash-o" aria-hidden="true"></i></a>
                  <a v-if="!props.row.isGit && (props.row.name != '..')" class="i-cursor btn btn-default btn-sm" title="Move/Rename" target="_blank" v-on:click.prevent="moveAction(props.row)" :href="props.row.href"><i class="fa fa-i-cursor" aria-hidden="true"></i></a>
                  <a v-if="!props.row.isGit && (props.row.name != '..')" class="external-link btn btn-default btn-sm" title="Open in a new window" target="_blank" :href="props.row.href"><i class="fa fa-external-link" aria-hidden="true"></i></a>
                </span>
                <span v-else-if="props.column.field == 'size'" :class="props.column.field">
                  {{ props.row.formattedSize }}
                </span>
                <span v-else :class="props.column.field">
                  {{ props.formattedRow[props.column.field] }}
                </span>
              </template>
            </vue-good-table>
        </div>

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
</style>
<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import { VueGoodTable } from 'vue-good-table-next';
import { BootstrapDialog } from '../bootstrap-dialog';
import { prepareHref, showError, git } from '../commons';
import { TreeEntry } from '../tree_entry';
import Breadcrumb from './Breadcrumb.vue';

export default defineComponent({
    components: {
        'breadcrumb': Breadcrumb,
        'vue-good-table': VueGoodTable
    },
    props: [ 'stack', 'config', 'isGit', 'showBreadcrumb' ],
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
            ]
        }
    },
    methods: {
        normalize(path) {
            if (path[0] != '/') {
                path = '/' + path;
            }
            return path.split(/[/]+/).join('/');
        },
        basename(path) {
            return path.substring(path.lastIndexOf('/') + 1);
        },
        updateLocation() {
            // Update href hash
            if (!this.isGit) {
                document.location.hash = this.normalize('files' + (this.stack.last().object || '/'));
            }
        },
        click(item) {
            // File/directory action
            if (item.name == '..') {
                this.stack.pop();
            } else {
                this.stack.push(item);
            }
            // Update href hash
            this.updateLocation();
            return false;
        },
        breadcrumbClicked(index, item) {
            // Breadcrumb action
            this.stack.slice(index + 1);
            // Update href hash
            this.updateLocation();
            return false;
        },
        moveAction(item) {
            // Rename a file
            const self = this;
            BootstrapDialog.show({
                title: 'Move/Rename File',
                message: 'Destination <input type="text" class="form-control" value="' + item.object + '" />',
                buttons: [{
                    label: 'Ok',
                    action(dialogRef) {
                        const target = dialogRef.getModalBody().find('input').val().trim();
                        git([ 'mv-local', item.object, target ], (data) => self.refresh());
                        dialogRef.close();
                    }
                },{
                    label: 'Cancel',
                    action(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
            return false;
        },
        deleteAction(item) {
            // Delete a file
            const self = this;
            BootstrapDialog.show({
                title: 'Confirm Delete',
                message: 'Are you sure you want to delete ' + item.name + ' ?',
                buttons: [{
                    label: 'Delete',
                    cssClass: 'btn-danger',
                    action(dialogRef) {
                        git([ 'rm-local', item.object ], (data) => self.refresh());
                        dialogRef.close();
                    }
                },{
                    label: 'Cancel',
                    action(dialogRef) {
                        dialogRef.close();
                    }
                }]
            });
            return false;
        },
        newAction() {
            // New file button action
            let item = { name: '✧', type: 'blob', object: (this.stack.last().object || '') + '/✧' };
            this.stack.push(item);
        },
        uploadAction() {
            // Upload button action
            this.$refs.file.click();
        },
        refresh() {
            console.log("Files.refresh");
            // Update tree view
            let path = null;
            let last = this.stack.last();
            if (last.type != 'blob') {
                if (this.isGit) { // git
                    path = 'tree' + this.normalize('git/' + last.object);
                } else { // local
                    path = 'tree' + this.normalize('files' + (last.object || ''));
                    // Update url hash
                    document.location.hash = this.normalize('files' + (last.object || ''));
                }
                // Get tree items
                axios.get(prepareHref(path), { params: { long: true }})
                     .then((response) => {
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
                        const compare = (a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase());
                        blobs.sort(compare);
                        trees.sort(compare);
                        // Add link to parent directory on top
                        if (this.stack.parent() || (last.object !== undefined && last.object.startsWith('/')) ) {
                            trees.unshift({ type: 'tree', name: '..', isSymbolicLink: false, icon: 'fa-folder', href: '#' });
                        }
                        this.items = trees.concat(blobs);
                  })
                  .catch(error => {
                        console.log(error);
                  })
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
        uploadFiles(files) {
            // Upload files
            const self = this;
            if (!this.isGit) {
                files.forEach((file) => {
                    const filename = self.normalize((self.stack.last().object || '') + '/' + self.basename(file.name));
                    const payload = file;
                    const options = {
                        headers: {
                            'Content-Type': file.type
                        }
                    };
                    // Upload file
                    axios.post(prepareHref('files' + filename), payload, options)
                         .then((response) => self.refresh())
                         .catch((error) => console.log(error));
                });
            }
        },
    },
    watch: {
        stack: {
            handler(val, preVal) {
                console.log('Files.watch stack');
                this.refresh();
            },
            deep: true
        }
    },
    mounted() {
        console.log('Files.mounted');
        this.refresh();
    }
})
</script>
