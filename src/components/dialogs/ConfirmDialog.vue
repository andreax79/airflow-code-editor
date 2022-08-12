<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-confim">
      <h1>{{ title }}</h1>
      <label>{{ message }}</label>
      <div class="confim-dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary">Ok</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal.airflow-code-editor-modal-confim {
    padding: 1em;
    font-size: 1em;
}
.airflow-code-editor-modal-confim h1 {
    font-size: 1.5em;
    text-align: left;
    margin-top: 0;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-confim label {
    display: block;
    text-align: left;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-confim .confim-dialog-buttons {
    margin-top: 1em;
    text-align: right;
}
.airflow-code-editor-modal-confim .confim-dialog-buttons .btn {
    margin-left: 1em;
}
</style>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [ ],
    data() {
        return {
            title: null,
            message: null,
            show: false,
        }
    },
    methods: {
        showDialog(title, message) {
            if (this.resolve) {
                this.resolve(false);
                this.resolve = null;
            }
            this.title = title;
            this.message = message;
            this.show = true;
            return new Promise((resolve, reject) => {
                this.resolve = resolve;
            });
        },
        ok() {
            this.resolve(true);
            this.resolve = null;
            this.show = false;
        },
        cancel() {
            this.resolve(false);
            this.resolve = null;
            this.show = false;
        },
        close() {
            this.resolve(false);
            this.resolve = null;
            this.show = false;
        },
    }
})
</script>
