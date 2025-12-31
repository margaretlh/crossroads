<template>
<div>
  <div class="panel panel-primary">
    <div class="panel-heading align-items-center is-flex">
      TPA: &nbsp;<b>{{tpa}}</b>
      <div class="flex-grow"/>
      <action-button
        left-icon="plus" class="btn-xs btn-default ml-2"
        @click="() => {isCreateModalVisible = true}"
      >Create rule</action-button>
    </div>
    <div class="panel-body">
      <div class="panel panel-default">
        <div class="panel-heading">
          Edit rule
        </div>
        <div class="panel-body">
          <loader v-bind="{ loading }" text="Loading rules...">
            <rule-form
              v-if="!!data?.current"
              :initial-params="data.current"
              :on-save="updateRule"
              :on-delete="deleteRule"
              :on-saved="refetch"
              :on-deleted="refetch"
            />
          </loader>
        </div>
      </div>
      <div class="panel panel-default">
        <div class="panel-heading">
          Previous rules
        </div>
        <div class="">
          <loader v-bind="{ loading }" text="Loading rules...">
            <flex-table
              class="flex-table-body-min-height-zero cancel-outer-border cancel-min-height table-border-top"
              is-bordered
              is-striped
              shrink-columns
              sort-by="date_effective"
              sort-direction="desc"
              :columns="columns"
              :rows="data.previous"
            />
          </loader>
        </div>
      </div>
    </div>
  </div>
  <create-rules-modal
    v-if="isCreateModalVisible"
    :on-close="() => {isCreateModalVisible = false}"
    :refetch="refetch"
    :tpa-ids="[tpaId]"
    :publisher-id="publisherId"
  />
</div>
</template>
<script>
import Vue from 'vue';
import { bizdevRules as backend } from '@/api';
import { computed } from 'vue'
import TableColumn from '@/models/table-column';
import useQuery from '@/utils/query';
export default {
  components: {
    RuleForm: () => import('./RuleForm.vue'),
    CreateRulesModal: () => import('./CreateRulesModal.vue'),
  },
  props: {
    tpa: {
      type: String,
      required: true
    },
    tpaId: {
      type: Number,
      required: true
    },
    publisherId: {
      type: Number,
      required: true
    },
    username: {
      type: String,
      required: true
    },
  },
  data: () => ({
    isCreateModalVisible: false,
  }),
  setup(props) {
    const params = computed(() => ({
      tpa_id: props.tpaId,
      publisher_id: props.publisherId,
    }))
    const { loading, data, refetch } = useQuery({
      fetchMethod: backend.loadTpaRules,
      params,
      onSuccess: result => {
        if (!result.current.id) {
          window.location.replace(`/admin/publisher/bizdev_rule/?username=${props.username}`)
        }
      }
    })
    return { loading, data, refetch }
  },
  methods: {
    updateRule: backend.updateRule,
    deleteRule: backend.deleteRule,
  },
  computed: {
    columns() {
      return [
        new TableColumn({
          name: 'id', label: 'ID',
        }),
        new TableColumn({
          name: "date_effective", label: "Date effective",
        }),
        new TableColumn({
          name: "rule_type_display", label: "Type",
        }),
        new TableColumn({
          name: "owner_username", label: "Owner",
          component: 'external-link',
          component_payload: {
            getText: row => row.owner_username,
            getHref: row => `/admin/publisher/?username=${row.owner_username}`,
            textLink: true,
            targetBlank: true,
          }
        }),
        new TableColumn({
          name: "percentage", label: "Percentage",
        }),
        new TableColumn({
          name: "overhead", label: "Overhead",
        }),
      ]
    },
  },
};
</script>


