<template>
  <div class="terminal-view" tabindex="1">
    <div style="width: 100%; height: 100%" ref="terminal"></div>
  </div>
</template>
<style>
.terminal-view {
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
</style>
<script>
import { defineComponent } from 'vue';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';

export default defineComponent({
    components: {},
    props: [],
    data() {
        return {
            loading: false,
        }
    },
    mounted() {
        this.startTerminal();
        this.refresh();
    },
    methods: {
        fitToscreen() {
            this.fit.fit();
            console.log("sending new dimensions to server [8;" + term.cols + ";" + term.rows + "t");
            this.ws.send("\u001b[8;" + term.cols + ";" + term.rows + "t");
        },
        startTerminal() {
            this.term = new Terminal({
                cursorBlink: true,
                macOptionIsMeta: true,
                scrollback: true,
            });
            // Load fit addon
            this.fit = new FitAddon();
            this.term.loadAddon(this.fit);
            // Load attach addon
            const url =
                (document.location.protocol == 'http:' ? 'ws://' : 'wss://') +
                document.location.host +
                document.location.pathname +
                'ws?columns=' + this.term.cols + '&lines=' + this.term.rows
            ;
            console.log(url);
            this.ws = new WebSocket(url);
            const attachAddon = new AttachAddon(this.ws, { bidirectional: true });
            this.term.loadAddon(attachAddon);
            // Open the terminal
            this.term.open(this.$refs.terminal);
            this.fit.fit();
        },
        isChanged() {
            return false;
        },
        updateLocation() {
            // Update href hash
            document.location.hash = 'terminal';
        },
        refresh() {
            // Update href hash
            this.updateLocation();
        },
        dispose() {
            // Dispose
            this.ws.send("\u001b$,F");
            this.term.dispose();
            this.term = null;
            this.fit = null;
            try {
                this.ws.close();
            } catch(err) {}
        },
        loaded(success) {
            // Emitted then commit is loaded/loading fails
            this.loading = false;  // Hide the spinner
        },
    },
})
</script>
