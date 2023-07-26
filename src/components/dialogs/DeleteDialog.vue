<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-delete">
      <h1>Confirm Delete</h1>
      <label>Are you sure you want to delete {{ target }}</label>
      <div class="dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-default">Delete</button>
      </div>
    </div>
  </modal>
</template>
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
