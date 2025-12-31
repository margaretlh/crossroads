<template>
<modal
  title="Create Rule"
  @close="onClose"
  :with-footer="false"
>
  <rule-form
    :on-save="(params, onSuccess, onError) => createRules({
      ...params, owner: publisherId,
      tpa_ids: (!!params?.singleTpaId ? [params.singleTpaId] : tpaIds)
    }, onSuccess, onError)"
    :on-saved="() => {
      onClose();
      refetch();
    }"
    :on-cancel="onClose"
    :tpa-options="tpaOptions"
  />
</modal>
</template>
<script>
import Vue from 'vue';
import { bizdevRules as backend } from '@/api';
export default {
  components: {
    RuleForm: () => import('./RuleForm.vue'),
  },
  props: {
    onClose: {
      type: Function,
      required: true
    },
    refetch: {
      type: Function,
      required: true
    },
    publisherId: {
      type: Number,
      required: true
    },
    tpaIds: {
      type: Array,
      default: undefined
    },
    tpaOptions: {
      type: Array,
      default: undefined
    },
  },
  methods: {
    createRules: backend.createRules,
  },
}
</script>