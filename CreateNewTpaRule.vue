<template>
<div class="align-items-center is-flex">
  <action-button
    class="btn btn-default btn-xs mr"
    left-icon="plus"
    @click="() => {
      if (!tpaOptions.length) {
        loadingTpaOptions = true;
        loadTpaOptions(
          {publisher_id: publisherId},
          response => {
            tpaOptions = response?.data?.options || [];
            loadingTpaOptions = false;
            isModalVisible = true;
          },
          () => {
            loadingTpaOptions = false;
          }
        )
      }
      else {
        isModalVisible = true;
      }
    }"
    :working="loadingTpaOptions"
  >Create rule</action-button>
  <create-rules-modal
    v-if="isModalVisible"
    :on-close="() => {isModalVisible = false}"
    :refetch="loadReport"
    :tpa-options="tpaOptions"
    :publisher-id="publisherId"
  />
</div>
</template>
<script>
import Vue from 'vue';
import { bizdevRules as backend } from '@/api';
export default {
  components: {
    CreateRulesModal: () => import('./CreateRulesModal.vue'),
  },
  props: {
    publisherId: {
      type: Number,
      required: true
    },
    loadReport: {
      type: Function,
      required: true
    }
  },
  data: () => ({
    isModalVisible: false,
    tpaOptions: [],
    loadingTpaOptions: false,
  }),
  methods: {
    loadTpaOptions: backend.loadTpaOptions,
  },
}
</script>