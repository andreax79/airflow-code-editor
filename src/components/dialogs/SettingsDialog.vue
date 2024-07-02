<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-settings">
      <h1>Settings</h1>
      <label>Color:</label>
      <select class="form-control" v-model="config.color">
          <option>Light</option>
          <option>Dark</option>
      </select>
      <br/>
      <label>Editor Theme:</label>
      <select class="form-control" v-model="config.theme">
          <option v-for="theme in themes">
          {{ theme }}
          </option>
      </select>
      <br/>
      <label>Editor Mode:</label>
      <select class="form-control" v-model="config.mode">
          <option selected>default</option>
          <option>emacs</option>
          <option>sublime</option>
          <option>vim</option>
      </select>
      <div class="dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary">Ok</button>
      </div>
    </div>
  </modal>
</template>
<script>
import { defineComponent } from 'vue';
import { setColor } from "../../commons";
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
            // Save setting on the local storage
            localStorage.setItem('airflow_code_editor_theme', this.config.theme);
            localStorage.setItem('airflow_code_editor_mode', this.config.mode);
            localStorage.setItem('airflow_code_editor_color', this.config.color);
            // Apply light/dark mode
            setColor(this.config.color);
            // Close the dialog
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
