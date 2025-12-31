<template>
<form>
  <div class="row mb-1">
    <div class="col-lg-3">
      <select
        class="form-control"
        v-model="filters.publisher">
        <option
          v-text="'Filter by Publisher'"
          value="">
        </option>
        <option
          v-for="(item, index) in sortedPublishers"
          v-text="item"
          :key="index"
          :value="item">
        </option>
      </select>
    </div>
    <div class="col-lg-3">
      <select
        class="form-control"
        v-model="filters.configuration">
        <option
          v-text="'Filter by Configuration'"
          value="">
        </option>
        <option
          v-for="(item, index) in sortedConfigurations"
          v-text="item"
          :key="index"
          :value="item">
        </option>
      </select>
    </div>
    <div class="col-lg-4">
      <div class="input-group input-daterange">
        <input id="start_date" autocomplete="off" type="text" class="form-control" v-model="filters.start_date">
        <div class="input-group-addon">to</div>
        <input id="end_date" autocomplete="off" type="text" class="form-control" v-model="filters.end_date">
      </div>
    </div>
    <div class="col-lg-2">
      <action-button v-if="hasFilters" @click="clearFilters" class="btn btn-sm btn-danger btn-default">
        <span>Clear</span>
      </action-button>
      <action-button @click="runFilters" class="btn btn-sm btn-default">
        <icon icon="search"/>
        <span>Filter</span>
      </action-button>
    </div>  
  </div>
</form>
</template>
<script>
import $ from 'jquery'
import datepicker from 'bootstrap-datepicker'
import qs from 'qs'
import QueryParams from '../../mixins/query-params'
import CleanObject from '../../mixins/clear-empty-object-values'

export default {

  mixins: [
    QueryParams,
    CleanObject
  ],
  
  props: {
    publishers: {
      type: Array
    },
    configurations: {
      type: Array
    },
    endpoint: {
      type: String
    }
  },

  data: () => ({
    filters: {
      publisher: '',
      configuration: '',
      start_date: '',
      end_date: '',
      sort: ''
    },
  }),

  created() {
    if(this.query_params.sort) this.filters.sort = this.query_params.sort
    if(this.query_params.start_date) this.filters.start_date = this.query_params.start_date
    if(this.query_params.end_date) this.filters.end_date = this.query_params.end_date
    if(this.query_params.publisher) this.filters.publisher = this.query_params.publisher
    if(this.query_params.configuration) this.filters.configuration = this.query_params.configuration
  },

  mounted() {
    let vm = this
    $('.input-daterange input').datepicker({
      format: 'yyyy-mm-dd',
    }).on('changeDate', function(e) {
      vm.filters.start_date = $('#start_date').val()
      vm.filters.end_date = $('#end_date').val()
    })
  },
  
  methods: {
    runFilters() {
      window.location.replace(
        `${window.location.origin}${this.endpoint}?${qs.stringify(this.cleanObject(this.filters))}`
      )
    },
    clearFilters() {
      window.location.replace(
        `${window.location.origin}${this.endpoint}`
      )
    }
  },

  computed: {
    sortedPublishers() {
      return this.publishers.sort()
    },
    sortedConfigurations() {
      return this.configurations.sort()
    },
    hasFilters() {
      return Object.keys(this.cleanObject(this.query_params))
        .filter(key => ['page', 'sort'].includes(key) === false)
        .length > 0
    }
  }

}
</script>