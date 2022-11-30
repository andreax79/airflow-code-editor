<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-delete">
      <h1>Confirm Close</h1>
      <label>Are you sure you want to close {{ target }} ?<br/>
      Your changed will be lost if you don't save them.</label>
      <div class="delete-dialog-buttons">
        <button @click="cancel" class="btn btn-primary">Cancel</button>
        <button @click="ok" class="btn btn-default">Ok</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal.airflow-code-editor-modal-delete {
    padding: 1em;
    font-size: 1em;
}
.airflow-code-editor-modal-delete h1 {
    font-size: 1.5em;
    text-align: left;
    margin-top: 0;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-delete label {
    display: block;
    text-align: left;
    margin-bottom: 1em;
}
.airflow-code-editor-modal-delete .delete-dialog-buttons {
    margin-top: 1em;
    text-align: right;
}
.airflow-code-editor-modal-delete .delete-dialog-buttons .btn {
    margin-left: 1em;
}
</style>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [],
    data() {
        return {
            target: null,
            show: false,
        }
    },
    methods: {
        showDialog(target) {
            return new Promise((resolve, reject) => {
                this.target = target;
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
            });
        },
        ok() {
            this.close(this.target);
        },
        cancel() {
            this.close();
        },
        close(target) {
            this.show = false;
            this.resolve(target);
        },
    }
})
</script>
