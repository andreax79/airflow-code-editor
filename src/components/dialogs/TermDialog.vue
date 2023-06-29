<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-term">
      <pre></pre>
      <div class="term-dialog-buttons">
        <button @click="ok" class="btn btn-primary">Ok</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal.airflow-code-editor-modal-term {
    padding: 1em;
    font-size: 1em;
}
.airflow-code-editor-modal-term h1 {
    font-size: 1.5em;
    text-align: left;
    margin-top: 0;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-term label {
    display: block;
    text-align: left;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-term .term-dialog-buttons {
    margin-top: 1em;
    text-align: right;
}
.airflow-code-editor-modal-term .term-dialog-buttons .btn {
    margin-left: 1em;
}
</style>
<script>
import { defineComponent } from 'vue';
import { Terminal } from 'xterm';
//import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';

export default defineComponent({
    props: [],
    data() {
        return {
            command: null,
            show: false,
        }
    },
    methods: {
        showDialog(command) {
            return new Promise((resolve, reject) => {
                console.log("XXXX");
                //this.startTerminal();
                this.command = command;
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
            });
        },
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
            /*
            // Load fit addon
            this.fit = new FitAddon();
            this.term.loadAddon(this.fit);
            */
            // Load attach addon
            const url =
                (document.location.protocol == 'http:' ? 'ws://' : 'wss://') +
                document.location.host +
                document.location.pathname +
                'ws?columns=' + this.term.cols + '&lines=' + this.term.rows
            ;
            console.log(url);
            /*
            this.ws = new WebSocket(url);
            const attachAddon = new AttachAddon(this.ws, { bidirectional: true });
            this.term.loadAddon(attachAddon);
            // Open the terminal
            this.term.open(this.$refs.terminald);
            this.fit.fit();
            */
        },
        ok() {
            this.close();
        },
        cancel() {
            this.close();
        },
        close() {
            /*
            // Dispose
            this.ws.send("\u001b$,F");
            this.term.dispose();
            this.term = null;
            this.fit = null;
            try {
                this.ws.close();
            } catch(err) {}
            */
            this.show = false;
            this.resolve(true);
        },
    }
})
</script>
