<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-commit">
      <h1>Commit</h1>
      <label>Please enter the commit message:</label>
      <textarea class="form-control" v-model="message">
      </textarea>
      <label>
          <icon icon="check_box" :state="amend" @click="toggleamend" />
          Amend previous commit
      </label>
      <div class="dialog-buttons">
        <button @click="cancel" class="btn btn-default">Cancel</button>
        <button @click="ok" class="btn btn-primary"
          :disabled="message == ''">Commit</button>
      </div>
    </div>
  </modal>
</template>
<script>
import { defineComponent } from 'vue';
import Icon from '../Icon.vue';

export default defineComponent({
    components: {
        'icon': Icon,
    },
    props: [],
    data() {
        return {
            message: null,
            amend: false,
            show: false,
        }
    },
    methods: {
        showDialog() {
            return new Promise((resolve, reject) => {
                this.message = '';
                this.amend = false;
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
            });
        },
        ok() {
            this.close({ amend: this.amend, message: this.message });
        },
        cancel() {
            this.close();
        },
        close(response) {
            this.show = false;
            this.resolve(response);
        },
        toggleamend() {
            this.amend = !this.amend;
        },
    }
})
</script>
