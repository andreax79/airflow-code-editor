<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-rename">
      <h1>Move/Rename File</h1>
      <label>Please enter a new name for the item:</label>
      <input type="text" class="form-control" v-model="target" @keyup.enter="ok" />
      <div class="rename-dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary"
          :disabled="target == ''">Ok</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal.airflow-code-editor-modal-rename {
    padding: 1em;
    font-size: 1em;
}
.airflow-code-editor-modal-rename h1 {
    font-size: 1.5em;
    text-align: left;
    margin-top: 0;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-rename label {
    display: block;
    text-align: left;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-rename .rename-dialog-buttons {
    margin-top: 1em;
    text-align: right;
}
.airflow-code-editor-modal-rename .rename-dialog-buttons .btn {
    margin-left: 1em;
}
</style>
<script>
import { defineComponent } from 'vue';
import { normalize, git, showError } from '../../commons';

export default defineComponent({
    props: [],
    data() {
        return {
            source: null,
            target: null,
            show: false,
        }
    },
    methods: {
        showDialog(source) {
            this.source = source;
            this.target = source;
            this.show = true;
        },
        ok() {
            // Rename a file
            let target = normalize(this.target);
            if (target == "/") {
                showError('Invalid filename');
                this.close();
            } else if (this.source != target) {
                git([ 'mv-local', this.source, target ], data => this.$emit('refresh'));
            }
            this.close();
        },
        cancel() {
            this.close();
        },
        close() {
            this.show = false;
        },
    }
})
</script>
