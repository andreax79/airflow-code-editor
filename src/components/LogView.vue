<template>
  <div ref="logView" class="log-view">
    <svg xmlns="http://www.w3.org/2000/svg"></svg>
    <div></div>
  </div>
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
import { LogView } from "../log";

export default defineComponent({
    data() {
        return {
            logView: null, // LogView instance
        }
    },
    methods: {
        initViews() {
            // Init views
            this.logView = new LogView(this.$refs.logView, this);
        },
        update(target) {
            // Update log view
            if (this.logView) {
                this.logView.update(target);
            }
        },
        updateCommit(commit) {
            this.$emit('updateCommit', commit);
        },
    },
    mounted() {
        // Init
        this.initViews();
    }
})
</script>
