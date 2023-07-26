<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-rename">
      <h1>Move/Rename File</h1>
      <label>Please enter a new name for the item:</label>
      <input type="text" class="form-control" v-model="target" @keyup.enter="ok" />
      <div class="dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-default"
          :disabled="target == ''">Rename</button>
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
            source: null,
            target: null,
            show: false,
        }
    },
    methods: {
        showDialog(source) {
            return new Promise((resolve, reject) => {
                this.source = source;
                this.target = source;
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
