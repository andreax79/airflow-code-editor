<template>
  <splitpanes class="default-theme">
    <pane key="1" :size="50" class="history-view">
        <spinner v-show="loading"/>
        <log ref="log" @updateCommit="updateCommit" />
    </pane>
    <pane key="2" :size="50" class="commit-view">
        <ul class="nav nav-tabs">
          <li role="presentation" :class="tab == 'commit' ? 'active' : ''" ><a href="#" @click.prevent="tab = 'commit'" >Commit</a></li>
          <li role="presentation" :class="tab == 'tree' ? 'active' : ''" ><a href="#" @click.prevent="tab = 'tree'">Tree</a></li>
        </ul>
        <div class="diff-view-container panel panel-default" v-show="tab == 'commit'">
            <commit ref="commit" linesOfContext="3" @loaded="loaded"></commit>
        </div>
        <div class="tree-view" v-show="tab == 'tree'">
            <container ref="container" :config="config" :is-git="true"></container>
        </div>
    </pane>
  </splitpanes>
</template>
<style>
.history-view {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    background-color: #eee;
}
.commit-view {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    background-color: #fff;
}
.commit-view .nav-tabs {
    padding-top: 1em;
    padding-left: 1em;
}
.commit-view .nav-tabs a:hover {
    color: #000;
}
.diff-view-container {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    border: 0;
    margin: 0;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import { normalize } from '../commons';
import LogView from './LogView.vue';
import FilesEditorContainer from './FilesEditorContainer.vue';
import ShowCommit from './ShowCommit.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'splitpanes': Splitpanes,
        'pane': Pane,
        'log': LogView,
        'container': FilesEditorContainer,
        'commit': ShowCommit,
        'spinner': Spinner,
    },
    props: [ 'config', 'target' ],
    data() {
        return {
            tab: 'commit', // active tab
            loading: false,
            id: ref(null), // section (tags, local-branches, remote-branches)
            name: ref(null), // reference
            commit: ref(null) // commit object
        }
    },
    mounted() {
        this.refresh();
    },
    methods: {
        isChanged() {
            return false;
        },
        updateLocation() {
            // Update href hash
            document.location.hash = normalize(this.id + '/' + this.name);
        },
        update(target) {
            // Load log view
            if ((this.id != target.id) || (this.name != target.name)) {
                this.id = target.id;
                this.name = target.name;
                this.$refs.log.update(this.name);
                this.updateCommit({ commit: this.name });
                this.updateLocation();
            }
        },
        updateCommit(commit) {
            // Emitted on click on log view items
            if (!this.loading) {
                this.commit = commit;
                this.loading = true; // Show the spinner
                this.$refs.commit.refresh(this.commit);  // Load commit
                this.$refs.container.updateStack(this.commit.commit, 'tree');  // Load tree
            }
        },
        refresh() {
            if (this.target) {
                this.update(this.target);
            }
        },
        loaded() {
            // Emitted then commit is loaded
            this.loading = false;  // Hide the spinner
        },
    },
})
</script>
