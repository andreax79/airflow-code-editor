<template>
  <div ref="logView" class="log-view" @contextmenu.prevent.stop="showMenu($event, null)">
    <template v-for="entry in entries">
        <a class="log-entry list-group-item"
           @click="updateCommit(entry.commit)"
           @contextmenu.prevent.stop="showMenu($event, entry)">
            <header>
                <h6>{{ entry.author.name }}
                    <template v-for="ref in entry.refs">
                        <span>&nbsp;</span>
                        <span :class="'label label-' + ref.reftype">{{ ref.ref }}</span>
                    </template>
                </h6>
                <span class="log-entry-date">{{ entry.author.formattedDate }}&nbsp;</span>
                <span class="badge">{{ entry.abbrevCommitHash }}</span>
            </header>
            <p class="list-group-item-text">{{ entry.abbrevMessage }}</p>
        </a>
    </template>
    <svg ref="svg" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
  <vue-simple-context-menu
      :element-id="'log-view-menu-' + uuid"
      :options="options"
      ref="logViewMenu"
      @option-clicked="menuOptionClicked"
  />
</template>
<style>
.log-view {
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    overflow-y: auto;
    cursor: default;
    margin-bottom: 0;
    position: relative;
    background-color: #fff;
}
.log-view svg {
    position: absolute;
    top: 0;
    left: 0;
}
.log-view svg path {
    stroke-width: 2;
    fill: none;
}
.log-view svg circle {
    stroke: none;
    fill: #555555;
}
.log-view .log-entry {
    padding: 5px 10px;
    background-color: transparent;
    margin: 0;
    border-width: 0 0 1px 0;
    border-radius: 0;
    height: 55px;
}
.log-view .log-entry:hover {
    background-color: rgba(244, 244, 244, 0.9);
}
.log-view .log-entry.active {
    background-color: rgba(244, 244, 244, 0.9);
    border-color: #ccc;
    color: #000;
}
.log-view .log-entry.active .list-group-item-text,
.log-view .log-entry.active .list-group-item-text:hover {
    color: #000 !important;
}
.log-view .log-entry.active header h6 a {
    color: #ffffff;
}
.log-view .log-entry header {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    align-items: baseline;
    -webkit-align-items: baseline;
}
.log-view .log-entry header h6 {
    font-weight: bold;
    margin-top: 0;
}
.log-view .log-entry header h6 a {
    color: #777777;
}
.log-view .log-entry header .badge {
    font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
}
.log-view .log-entry header .log-entry-date {
    margin-left: auto;
    font-size: 0.8em;
    margin-right: 1em;
}
.log-view .log-entry .list-group-item-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: inherit;
}
.log-view .log-entry-more {
    padding: 10px 16px;
}
.log-view .log-entry-more a {
    display: block;
    text-align: center;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { loadGitHistory, updateGraph } from "../log";
import VueSimpleContextMenu from 'vue-simple-context-menu';

export default defineComponent({
    components: {
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    props: [ 'target', 'uuid' ],
    data() {
        return {
            entries: [], // log entries
            options: [  // menu options
                {
                  name: '<span class="material-icons">refresh</span> Refresh',
                  slug: 'refresh',
                },
            ],
        }
    },
    methods: {
        async initViews() {
            this.refresh();
        },
        async refresh() {
            // Refresh
            const self = this;
            const svg = self.$refs.svg;
            // Load git history
            const entries = await loadGitHistory(self.target);
            self.entries.length = 0;
            self.entries.push(...entries);
            // Update graph
            await updateGraph(svg, self.entries);
            self.$refs.logView.setAttribute("style", "padding-left:" + svg.getAttribute('width') + "px");
        },
        updateCommit(commit) {
            this.$emit('updateCommit', { 'commit': commit });
        },
        async showMenu(event, entry) {
            // Show sidebar menu
            await this.$refs.logViewMenu.showMenu(event, entry);
        },
        async menuOptionClicked(event) {
            // Menu click
            if (event.option.slug == 'refresh') {
                await this.refresh();
            }
        },
    },
    async mounted() {
        // Init
        this.initViews();
    }
})
</script>
