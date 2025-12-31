<template>
<div>
  <div class="is-flex">
    <h5>New Users</h5>
  </div>
  <div class="divider mb-2"/>
  <paging-flex-table
    :loading="loading"
    :rows="filteredRows" 
    :columns="columns"
    sort-by="id"
    sort-direction="asc"
    :default-limit="25"
    :min-shrink-col-width="60"
    searchable
    apply-search
    is-striped 
    is-bordered
    shrink-columns
    column-switcher
  >
    <span slot="left-of-the-buttons">
      <div class="btn-group" role="group">
        <button
          v-for="status in statuses" :key="`button_${status}`"
          :class="{'active': filterStatus == status}"
          type="button" class="btn btn-sm btn-default"
          @click="filterStatus = status"
          @mousedown.prevent
        >{{status}}</button>
      </div>
    </span>
  </paging-flex-table>
</div>
</template>

<script>
import {trafficGuard as backend} from '@/api'
import TableColumn from '@/models/table-column'

export default {
  data: () => ({
    loading: false,
    rows: [],
    filterStatus: 'pending'
  }),

  methods: {
    loadIndex() {
      this.loading = true
      backend.newUsersIndex(({data}) => {
        this.rows = data.rows
        this.loading = false
      }, () => {
        this.loading = false
      })
    }
  },

  computed: {
    statuses() {
      return [
        'pending', 'denied', 'all'
      ]
    },
    columns() {
      return [
        new TableColumn({
          name: 'id',
          label: 'ID',
          component: 'table-link',
          hide_text: true,
          component_payload: {
            textKey: 'id',
            path: '/admin/new_users/show-new-user/{id}',
          }
        }),
        new TableColumn({name: 'email', label: 'Email'}),
        new TableColumn({name: 'first_name', label: 'First Name'}),
        new TableColumn({name: 'last_name', label: 'Last Name'}),
        new TableColumn({name: 'company', label: 'Company Name'}),
        new TableColumn({
          name: 'signed_up_on',
          label: 'Date Submitted',
          format: 'date',
          meta: {display_format: 'Y-MM-DD M:SS'}
        }),
        ...((this.filterStatus == 'all') ? [new TableColumn({
          name: 'status', label: 'Status',
          formatter: (val) => val.charAt(0).toUpperCase() + val.slice(1)
        })] : [])
      ]
    },
    filteredRows() {
      if (this.filterStatus === 'all') return this.rows;
      return this.rows.filter(row => row.status === this.filterStatus);
    }
  },

  created() {
    this.loadIndex()
  }
}
</script>
