<template>
    <div class="tree-view">
        <ol class="breadcrumb">
          <breadcrumb :stack="stack" :is-git="false"></breadcrumb>
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
    props: [ 'stack', 'config', 'isGit' ],
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
            const self = this;
            if (!self.isGit) {
                document.location.hash = self.normalize('files' + (self.stack.last().object || '/'));
            }
        },
        click(item) {
            // File/directory action
            const self = this;
            if (item.name == '..') {
                self.stack.pop();
            } else {
                self.stack.push(item);
            }
            // Update href hash
            self.updateLocation();
            return false;
        },
        breadcrumbClicked(index, item) {
            // Breadcrumb action
            const self = this;
            self.stack.slice(index + 1);
            // Update href hash
            self.updateLocation();
            return false;
        },
        moveAction(item) {
            // Delete a file
            const self = this;
            BootstrapDialog.show({
                title: 'Move/Rename File',
                message: 'Destination <input type="text" class="form-control" value="' + item.object + '" />',
                buttons: [{
                    label: 'Ok',
                    action(dialogRef) {
                        let target = dialogRef.getModalBody().find('input').val().trim();
                        git([ 'mv-local', item.object, target ], function(data) {
                            self.refresh();
                        });
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
                        git([ 'rm-local', item.object ], function(data) {
                            self.refresh();
                        });
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
            const self = this;
            let item = { name: '✧', type: 'blob', object: (self.stack.last().object || '') + '/✧' };
            self.stack.push(item);
        },
        uploadAction() {
            // Upload button action
            const self = this;
            this.$refs.file.click();
        },
        refresh() {
            console.log("Files.refresh");
            // Update tree view
            const self = this;
            let path = null;
            let last = this.stack.last();
            if (last.type != 'blob') {
                if (self.isGit) { // git
                    path = 'tree' + self.normalize('git/' + last.object);
                } else { // local
                    path = 'tree' + self.normalize('files' + (last.object || ''));
                    // Update url hash
                    document.location.hash = self.normalize('files' + (last.object || ''));
                }
                // Get tree items
                axios.get(prepareHref(path), { params: { long: true }})
                     .then((response) => {
                        let blobs = []; // files
                        let trees = []; // directories
                        response.data.value.forEach((part) => {
                            let item = new TreeEntry(part, self.isGit, last.object);
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
                        if (self.stack.parent() || (last.object !== undefined && last.object.startsWith('/')) ) {
                            trees.unshift({ type: 'tree', name: '..', isSymbolicLink: false, icon: 'fa-folder', href: '#' });
                        }
                        self.items = trees.concat(blobs);
                  })
                  .catch(error => {
                        console.log(error);
                  })
            }
        },
        handleDrop($event) {
            // Upload files (drag and drop)
            const self = this;
            self.isDragEnter = false;
            // Convert FileList into Array
            const files = [...$event.dataTransfer.files];
            self.uploadFiles(files);
        },
        handleUploadButton($event) {
            // Upload files (upload button)
            const self = this;
            const files = Array.from($event.target.files);
            self.uploadFiles(files);
            $event.target.value = '';
        },
        uploadFiles(files) {
            // Upload files
            const self = this;
            if (!self.isGit) {
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
                const self = this;
                self.refresh();
            },
            deep: true
        }
    },
    mounted() {
        console.log('Files.mounted');
        const self = this;
        self.refresh();
    }
})
</script>
