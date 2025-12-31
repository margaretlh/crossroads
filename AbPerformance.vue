<template>
<loader v-bind="{ loading }">
  <table class="table">
    <table-head 
      :columns="columns"
      :sortDirection="direction"
      :sortBy="sort"
      @sort="handleSort"
    />
    <tbody>
      <tr v-for="data in sortedTableData" :key="data.campaign_id">
        <td>
          <route 
            :to="`/admin/trafficguard/campaign/${data.campaign_id}`">
            {{ data.campaign_name }}
          </route>
        </td>
        <td>
          {{ data.performance | toFixed(2) }}%
        </td>
        <td>
          {{ data.comparison ? 'Better' : 'Worse' }}
        </td>
        <td>
          <span v-tooltip="`${data.ratioTooltip}`">
            {{ data.ratio }}
          </span>
        </td>
        <td>
          {{ data.gross_visitors }}
        </td>
        <td>
          {{ data.total_revenue | asCurrency('$') }}
        </td>
      </tr>
    </tbody>
  </table>  

  <p class="has-text-centered" v-if="!sortedTableData.length">No data available.</p>

</loader>
</template>
<script>
import groupBy from 'lodash/groupBy'
import first from 'lodash/first'
import sortBy from 'lodash/sortBy'
import forEach from 'lodash/forEach'
import QueryParams from '../../mixins/query-params'
import StickyTableHeaders from '../../mixins/sticky-table-header'
import CleanObject from '../../mixins/clear-empty-object-values'

export default {

  mixins: [
    QueryParams,
    CleanObject,
    StickyTableHeaders
  ],
  
  data: () => ({
    sort: 'total_revenue',
    direction: 'asc',
    loading: true,
    data: [],
    columns: [
      { name: 'camapign_name', label: 'Camapaign Name', component: null, display: 'string' },
      { name: 'performance', label: 'Performance', component: null, display: 'string' },
      { name: 'comparison', label: 'Comparison Indicator', component: null, display: 'string' },
      { name: 'ratio', label: 'Ratio Regular vs Optimised Visits', component: null, display: 'string' },
      { name: 'gross_visitors', label: 'Gross Visitors', component: null, display: 'string' },
      { name: 'total_revenue', label: 'Total Revenue', component: null, display: 'string' },
    ],
  }),

  created() {
    this.loadData()
  },

  methods: {
    loadData() {
      axios.get('/kw_reports/load-lkw-ab-report/', {
        params: this.cleanObject(this.query_params)
      }).then(response => {
        this.processData(response.data.report)
        this.loading = false
        this.makeTablesSticky()
      }).catch(error => {
        this.loading = false
      })
    },
    processData(data) {
      forEach(this.groupedCampaigns(data), (reportData, campaignName) => {
        this.data.push({
          campaign_id: reportData[0].campaign_id,
          campaign_name: campaignName,
          performance: this.performance(reportData),
          comparison: this.comparison(reportData),
          ratioTooltip: this.ratioTooltip(reportData),
          ratio: this.ratio(reportData),
          gross_visitors: this.totalVisitors(reportData),
          total_revenue: this.totalRevenue(reportData),
        })
      })
    },
    campaignsWithOptimization(rawData) {
      return rawData.filter(campaign => rawData.filter(data => data.campaign_name === campaign.campaign_name).length > 1)
    },
    groupedCampaigns(data) {
      return groupBy(this.campaignsWithOptimization(data), 'campaign_name')
    },
    totalRevenue(data) {
      return data.reduce((total, item) => total + Number(item.sum_revenue), 0)
    },
    totalVisitors(data) {
      return data.reduce((total, item) => total + Number(item.sum_lander_visits), 0)
    },
    rpv(data) {
      if(!data) return 0
      if(Number(data.sum_lander_visits) === 0) return 0
      return Number(data.sum_revenue) / Number(data.sum_lander_visits)
    },
    performance(data) {
      let unoptimizedRpv = this.rpv(first(data.filter(row => row.is_managed === false)))
      let optimizedRpv = this.rpv(first(data.filter(row => row.is_managed === true)))
      if(!unoptimizedRpv) return 0
      return 100 / unoptimizedRpv * optimizedRpv - 100
    },
    comparison(data) {
      let unoptimizedRpv = this.rpv(first(data.filter(row => row.is_managed === false)))
      let optimizedRpv = this.rpv(first(data.filter(row => row.is_managed === true)))
      return optimizedRpv > unoptimizedRpv
    },
    ratioTooltip(data) {
      let unoptimized = first(data.filter(row => row.is_managed === false))
      let optimized = first(data.filter(row => row.is_managed === true))
      if(!unoptimized || !optimized) return 0
      return (Number(unoptimized.sum_lander_visits) / Number(optimized.sum_lander_visits) * 100).toFixed(2) + '%'
    },
    ratio(data) {
      let unoptimized = Number(first(data.filter(row => row.is_managed === false)).sum_lander_visits)
      let optimized = Number(first(data.filter(row => row.is_managed === true)).sum_lander_visits)
      if(unoptimized > optimized) {
        return `${(unoptimized / optimized).toFixed(2)}:1`
      }
      if(optimized > unoptimized) {
        return `1:${(optimized / unoptimized).toFixed(2)}`
      }
      return '1:1'
    },
    handleSort(payload) {
      this.sort = payload.column;
      this.direction = payload.direction;
    }
  },

  computed: {
    sortedTableData() {
      let data = sortBy(this.data, this.sort)
      return this.direction === 'asc' ? data.reverse() : data
    },
  }

}
</script>