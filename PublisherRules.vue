<template>
<div class="panel panel-primary">
  <div class="panel-heading align-items-center is-flex">
    Bizdev Rules: &nbsp;<b>{{username}}</b>
    <div class="flex-grow"/>
    <create-new-tpa-rule
      :publisher-id="publisherId"
      :load-report="() => {$refs.report.loadReport()}"
      :style="{color: '#666666'}"
    />
  </div>
  <div class="panel-body">
    <div class="is-flex mb-1 align-items-center is-flex">
      <div class="flex-grow has-text-weight-bold">
        TPAs selected: {{selectedTPAs.length}}
      </div>
      <div class="is-flex">
        <button
          class="btn btn-default btn-xs mr"
          @click.prevent="selectAll"
        >Select all</button>
        <button
          class="btn btn-default btn-xs"
          @click.prevent="deselectAll"
        >Deselect all</button>
        <div class='vertical-divider ml-1 mr-1'></div>
        <span class="is-flex">
          <button 
            class="btn btn-success btn-xs"
            @click="isVisibleCreateModal = true"
            :disabled="selectedTPAs.length == 0"
          ><i class="fa fa-plus"></i> Bulk create rules</button>
          <create-rules-modal
            v-if="isVisibleCreateModal"
            :on-close="() => {isVisibleCreateModal = false}"
            :refetch="() => {$refs?.report?.loadReport()}"
            :tpa-ids="selectedTPAs"
            :publisher-id="publisherId"
          />
        </span>
      </div>
    </div>
    <generic-report
      ref="report"
      :columns="columns"
      :load-method="loadPublisherRules"
      :default-limit="100"
      :externalParams="{username}"
      sort-by="date_effective"
      sort-direction="desc"
      :export-file-name="`bizdev-rules-${username}.csv`"
      :sticky-columns-amount="2"
      :detail-columns-amount="2"
      advanced-searchable
      disable-date-filtering
      hide-filters-panel
      @updated-response="data => allTpaIds = data.rows.map(row => row.tpa_id)"
      @select-row="(row, value) => set(selectedTPAsMap, row.tpa_id, value)"
    />
  </div>
</div>
</template>
<script>
import Vue from 'vue';
import { bizdevRules as backend } from '@/api';
import TableColumn from '@/models/table-column';
export default {
  components: {
    CreateRulesModal: () => import('./CreateRulesModal.vue'),
    CreateNewTpaRule: () => import('./CreateNewTpaRule.vue'),
  },
  props: {
    username: {
      type: String,
      required: true
    },
    publisherId: {
      type: Number,
      required: true
    }
  },
  data: () => ({
    selectedTPAsMap: {},
    isVisibleCreateModal: false,
    allTpaIds: [],
    tpaOptions: [],
    loadingTpaOptions: false,
  }),
  methods: {
    set: Vue.set,
    loadPublisherRules: backend.loadPublisherRules,
    selectAll() {
      this.allTpaIds.forEach(tpaId => this.set(this.selectedTPAsMap, tpaId, true));
    },
    deselectAll() {
      this.selectedTPAs.forEach(tpaId => this.set(this.selectedTPAsMap, tpaId, false));
    }
  },
  computed: {
    columns() {
      return [
        new TableColumn({
          name: 'selected', label: 'Selected',
          component: 'row-selector',
          component_payload: {
            event: 'select-row',
            selectedRowsKeys: this.selectedTPAsMap,
            selectionKey: 'tpa_id',
          }
        }),
        new TableColumn({
          name: 'id', label: 'ID',
          component: 'external-link',
          component_payload: {
            getText: row => row.id,
            getHref: row => `/admin/publisher/bizdev_rule/tpa/?tpa_id=${row.tpa_id}&username=${this.username}`,
            textLink: true,
          }
        }),
        new TableColumn({
          name: "tpa_username", label: "TPA username",
          component: 'external-link',
          component_payload: {
            getText: row => row.tpa_username,
            getHref: row => `/admin/publisher/bizdev_rule/tpa/?tpa_id=${row.tpa_id}&username=${this.username}`,
            textLink: true,
          }
        }),
        new TableColumn({
          name: 'publisher_username', label: 'TPA Publisher',
          component: 'external-link',
          component_payload: {
            getText: row => row.publisher_username,
            getHref: row => `/admin/publisher/?username=${row.publisher_username}`,
            textLink: true,
            targetBlank: true,
          }
        }),
        new TableColumn({
          name: "tpa_type", label: "TPA Type",
        }),
        new TableColumn({
          name: 'owner_username', label: 'Owner',
          component: 'external-link',
          component_payload: {
            getText: row => row.owner_username,
            getHref: row => `/admin/publisher/?username=${row.owner_username}`,
            textLink: true,
            targetBlank: true,
          }
        }),
        new TableColumn({
          name: "date_effective", label: "Date effective",
        }),
        new TableColumn({
          name: "rule_type", label: "Rule Type",
        }),
        new TableColumn({
          name: "percentage", label: "Percentage",
        }),
        new TableColumn({
          name: "overhead", label: "Overhead",
        }),
      ]
    },
    selectedTPAs() {
      return Object.entries(this.selectedTPAsMap).filter(
        ([tpaId, isSelected]) => isSelected
      ).map(([tpaId, isSelected]) => tpaId);
    }
  }
};
</script>


