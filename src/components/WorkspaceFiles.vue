<template>
  <div class="workspace-file-header">
    <span class="workspace-file-header-checkbox" @click="toggleAll()">
        <icon icon="check_box" :state="items.length && selected.length == items.length" />
    </span>
    <h1>{{ kind == 'unstaged' ? 'Unstaged files' : 'Staged files' }}</h1>
    <div class="header-buttons">
      <!-- <div class="btn-group" role="group"> -->
      <!--   <button type="button" class="btn btn-default" @click="selectAll">Select All</button> -->
      <!--   <button type="button" class="btn btn-default" @click="deselectAll">Deselect All</button> -->
      <!-- </div> -->
      <button @click="process"
              type="button"
              :disabled="selected.length == 0 ? 'disabled' : null"
              class="btn btn-default">
              {{ kind == 'unstaged' ? 'Stage' : 'Unstage' }} <span class="badge">{{ selected.length }}</span>
      </button>
      <button @click="showCommitDialog"
              type="button"
              :disabled="items.length == 0 ? 'disabled' : null"
              class="btn btn-primary"
              v-if="kind == 'staged'">
              Commit
      </button>
      <button @click="showRevertDialog"
              type="button"
              :disabled="selected.length == 0 ? 'disabled' : null"
              class="btn btn-warning"
              v-if="kind == 'unstaged'">
              Revert <span class="badge">{{ selected.length }}</span>
      </button>
    </div>
  </div>
  <div class="workspace-file-table table-responsive">
    <table class="table table-hover table-striped">
      <tbody>
        <tr v-for="item in items" :key="item" :class="item.selected ? 'info' : ''">
          <td class="workspace-file-checkbox" @click="toggleItem(item)">
            <icon icon="check_box" :state="item.selected" />
          </td>
          <td class="workspace-file-icon" @click="showDiff(item)">
            <icon :icon="item.icon" />
          </td>
          <td class="workspace-file-name" @click="showDiff(item)">
            {{ item.name }}
          </td>
          <td class="workspace-file-badge" @click="showDiff(item)">
            <span class="badge">{{ item.status }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <commit-dialog ref="commitDialog" @refresh="$emit('refresh')"></commit-dialog>
  <confirm-dialog ref="confirmDialog" @refresh="$emit('refresh')"></confirm-dialog>
</template>
<style>
html body div#global-container div.splitpanes.splitpanes--vertical.default-theme div.splitpanes__pane.app-main-view div.splitpanes.splitpanes--vertical.default-theme div.splitpanes__pane div.splitpanes.splitpanes--horizontal.default-theme div.splitpanes__splitter {
    background-color: #eee;
    border-left: 1px solid #eee !importanti;
}
.workspace-file-header {
    flex: 0;
    border-bottom: 1px solid #ddd;
    padding: 0.5em;
}
.workspace-file-header h1 {
    display: inline-block;
    font-size: 1em;
    margin-top: 0.75em;
    font-weight: bold
}
.workspace-file-header .header-buttons {
    float: right;
}
.workspace-file-header .header-buttons .btn {
    margin-left: 0.5em;
}
.workspace-file-header .header-buttons .btn-group {
    margin-right: 1em;
}
.workspace-file-table {
    display: block;
    flex: 1;
    overflow: auto;
}
.workspace-file-table fa {
    margin-right: 1em;
}
.workspace-file-table td {
    padding: 0.25em;
    cursor: pointer;
}
.workspace-file-header-checkbox {
    font-size: 1.5em;
    width: 2em;
    display: inline-block;
    vertical-align: middle;
    padding-left: 1px;
    cursor: pointer;
}
.workspace-file-checkbox {
    width: 2em;
}
.workspace-file-icon {
    width: 2em;
}
.workspace-file-badge {
    width: 4em;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { git_async } from '../commons';
import { getIcon } from '../tree_entry';
import Icon from './Icon.vue';
import CommitDialog from './dialogs/CommitDialog.vue';
import ConfirmDialog from './dialogs/ConfirmDialog.vue';

const gitStatuses = {
    ' ': 'unmodified',
    'M': 'modified',
    'T': 'type changed',
    'A': 'added',
    'D': 'deleted',
    'R': 'renamed',
    'C': 'copied',
    'U': 'unmerged',
    '?': 'untracked',
    '!': 'ignored',
}

export default defineComponent({
    components: {
        'icon': Icon,
        'commit-dialog': CommitDialog,
        'confirm-dialog': ConfirmDialog,
    },
    props: [ 'kind' ], // staged/unstaged
    data() {
        return {
            items: ref([]),
        }
    },
    computed: {
        selected() {
            // Return the selected items
            return this.items.filter((item) => item.selected);
        },
    },
    methods: {
        toggleItem(item) {
            // Toggle item selection
            item.selected = !item.selected;
        },
        showDiff(item) {
            // Show item diff
            this.$emit('showDiff', item);
        },
        async showCommitDialog(item) {
            // Show commit dialog
            const response = await this.$refs.commitDialog.showDialog();
            if (response) {
                // Commit
                const cmd = [
                    'commit',
                    response.amend ? '--amend' : null,
                    '-m',
                    response.message
                ];
                const data = await git_async(cmd);
                console.log(data);
                this.refresh();
            }
        },
        async showRevertDialog(item) {
            // Show revert dialog
            if (await this.$refs.confirmDialog.showDialog(
                'Confirm Revert',
                'Are you sure you want to revert changes?'
            )) {
                this.revert();
            }
        },
        processLine(line) {
            // Parge git status --porcelain line
            const statusColumn = this.kind == 'staged' ? 0 : 1;
            const status = line[statusColumn];
            if ((this.kind == 'staged' && status != " " && status != "?") ||
                (this.kind == 'unstaged' && status != " ")) {
                let name = line.substring(3);
                if (name.indexOf(' -> ') != -1) {  // Renamed item
                    name = name.split(' -> ')[1];
                }
                const type = (name[name.length - 1] == '/') ? 'tree' : 'blob';
                return {
                    'name': name,
                    'status': gitStatuses[status] || status,
                    'type': type,
                    'kind': this.kind,
                    'icon': getIcon(name, type)
                };
            } else {
                return null;
            }
        },
        parseStatus(data) {
            // Parse git status --porcelain output
            const lines = data.split("\n").filter(line => line.length > 0);
            this.items = lines.map(this.processLine).filter(item => item != null);
        },
        selectAll() {
            // Select all
            this.items.forEach((item) => item.selected = true);
        },
        deselectAll() {
            // Deselect all
            this.items.forEach((item) => item.selected = false);
        },
        toggleAll() {
            // Select/Deselect all
            if (this.selected.length == this.items.length) {
                this.deselectAll();
            } else {
                this.selectAll();
            }
        },
        async process() {
            // Stage/Unstage selected items
            if (this.selected.length) {
                const cmd = [ this.kind == 'staged' ? 'reset' : 'add', '--' ].concat(this.selected.map(item => item.name));
                await git_async(cmd);
                this.$emit('refresh');
            }
        },
        async revert() {
            // Revert changes
            if (this.selected.length) {
                const cmd = [ 'checkout', '--' ].concat(this.selected.map(item => item.name));
                await git_async(cmd);
                this.$emit('refresh');
            }
        },
        async refresh() {
            // --untracked-files=all - Also shows individual files in untracked directories
            const data = await git_async([ 'status', '--porcelain', '--untracked-files=all' ]);
            if (data) {
                this.parseStatus(data);
            }
        },
    },
})
</script>
