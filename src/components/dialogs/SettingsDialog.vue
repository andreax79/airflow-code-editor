<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-settings">
      <h1>Settings</h1>
      <label>Theme:</label>
      <select class="form-control" v-model="config.theme">
          <option v-for="theme in themes">
          {{ theme }}
          </option>
      </select>
      <br/>
      <label>Mode:</label>
      <select class="form-control" v-model="config.mode">
          <option selected>default</option>
          <option>emacs</option>
          <option>sublime</option>
          <option>vim</option>
      </select>
      <div class="settings-dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary">Ok</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal.airflow-code-editor-modal-settings {
    padding: 1em;
    font-size: 1em;
}
.airflow-code-editor-modal-settings h1 {
    font-size: 1.5em;
    text-align: left;
    margin-top: 0;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-settings label {
    display: block;
    text-align: left;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-settings .settings-dialog-buttons {
    margin-top: 1em;
    text-align: right;
}
.airflow-code-editor-modal-settings .settings-dialog-buttons .btn {
    margin-left: 1em;
}
</style>
<script>
import { defineComponent } from 'vue';
import themes from "../../themes";

export default defineComponent({
    props: [],
    data() {
        return {
            themes: themes, // themes list from "themes.js"
            show: false,
        }
    },
    methods: {
        showDialog(config) {
            return new Promise((resolve, reject) => {
                this.config = Object.assign({}, config); // copy config object
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
            });
        },
        ok() {
            this.close(this.config);
        },
        cancel() {
            this.close();
        },
        close(config) {
            this.show = false;
            this.resolve(config);
        },
    }
})
</script>
