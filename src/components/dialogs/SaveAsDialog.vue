<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-save-as">
      <h1>Save File</h1>
      <label>Please enter a new name for the item:</label>
      <input type="text" class="form-control" v-model="target" @keyup.enter="ok" />
      <div class="dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary"
          :disabled="target == '' || target.endsWith('/')">Save</button>
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
