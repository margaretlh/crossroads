<template>
  <div class='mb-2'>
    <div class="is-flex space-between">  
      <h5>Category Manager</h5>
      <div class="btn-group is-flex justify-end align-center">
        <button class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">
          Tools
          <span class="caret"></span>
        </button>
        <ul class="dropdown-menu dropdown-menu-right">
          <li><a href="/admin/trafficguard/category-manager/name-suggester/"
          >Name Suggester</a></li>
        </ul>
      </div>
    </div>
    <div class="divider mb-2"></div>
    <div class="mb-2 flex">
      <div class="flex flex-grow">
        <div class="btn-group" role="group">
          <button
            :class="{'active': isCategoryMode}"
            type="button" class="btn btn-sm btn-default mr-1"
            @click="$store.commit('categoryManager/setMode', MODES.ALL_CATEGORIES)"
            @mousedown.prevent
          >Categories</button>
        </div>
        <button
          :class="{'active': mode == MODES.CATEGORY_GROUPS}"
          type="button" class="btn btn-sm btn-default"
          @click="$store.commit('categoryManager/setMode', MODES.CATEGORY_GROUPS)"
          @mousedown.prevent
        >Category groups</button>
      </div>
      <div>
        <button
          type="button" class="btn btn-sm btn-default mr"
          @click="showCreateCategoryModal = true"
          @mousedown.prevent
        >Create category</button>
        <category-modal
          v-if="showCreateCategoryModal"
          @close="showCreateCategoryModal = false"
          @update="$refs.report.reset()"
        ></category-modal>
        <button
          type="button" class="btn btn-sm btn-default"
          @click="showCreateCategoryGroupModal = true"
          @mousedown.prevent
        >Create category group</button>
        <category-group-modal
          v-if="showCreateCategoryGroupModal"
          @close="showCreateCategoryGroupModal = false"
          @update="$refs.report.reset()"
        ></category-group-modal>
      </div>
    </div>
    <div class="divider mb-2"></div>
    <category-report
      v-if="([
        MODES.ALL_CATEGORIES,
        MODES.MAPPED_CATEGORIES,
        MODES.UNMAPPED_CATEGORIES,
      ].includes(mode))"
      ref="report" 
    />
    <category-group-report ref="report" v-if="mode === MODES.CATEGORY_GROUPS"/>
  </div>
</template>
<script>


import { mapGetters } from 'vuex'
import debounce from 'lodash/debounce'
import nestedComputedStore from '@/utils/nested-computed-store'
import getParamsFromURL from '@/utils/get-params-from-url'
import { MODES, FILTERS_CONFIG, FILTER_TYPE_TO_KEY } from './constants.js'

const CategoryModal = () => import('./modals/Category.vue')
const CategoryGroupModal = () => import('./modals/CategoryGroup.vue')
const CategoryReport = () => import('./Report/Category/Index.vue')
const CategoryGroupReport = () => import('./Report/CategoryGroup/Index.vue')

export default {
  components: {
    CategoryModal, CategoryGroupModal,
    CategoryReport, CategoryGroupReport
  },
  data: () => ({
    showCreateCategoryModal: false,
    showCreateCategoryGroupModal: false,
    debouncedUpdateUrl: null
  }),
  methods: {
    updateUrl() {
      const url = new URL(document.URL);
      url.search = new URLSearchParams({
        mode: this.mode,
        ...Object.fromEntries([
          'start_date', 'end_date', 'sort_by', 'sort_direction',
          ...this.modeFilterKeys
        ].map(
          filterKey => [filterKey, this.currentFilters[filterKey]]
        ).filter(
          ([filterKey, filterVal]) => filterVal
        ))
      });
      history.pushState(null, 'Crossroads | Category Manager', url.toString());
    }
  },
  watch: {
    mode: {
      handler(val){
        this.$store.commit("categoryManager/filters/setCurrents",
          {
            ...Object.fromEntries(
              Object.values(FILTER_TYPE_TO_KEY).filter(
                key => !this.modeFilterKeys.includes(key)
              ).map(key => [key, null])
            ),
            sort_by: 'updated_at',
            sort_direction: 'desc'
          }
        );
        this.debouncedUpdateUrl();
      }
    },
    currentFilters: {
      handler(val){
        this.debouncedUpdateUrl();
      },
      deep: true
    }
  },
  computed: {
    ...mapGetters('categoryManager', ['mode']),
    current: nestedComputedStore(
      'categoryManager/filters/current', 'categoryManager/filters/setCurrent',
      ['sort_by', 'sort_direction']
    ),
    ...mapGetters("categoryManager/filters", {currentFilters: "current"}),
    MODES() {
      return MODES
    },
    isCategoryMode() {
      return [
        MODES.ALL_CATEGORIES, MODES.MAPPED_CATEGORIES, MODES.UNMAPPED_CATEGORIES
      ].includes(this.mode);
    },
    modeFilterKeys() {
      return FILTERS_CONFIG[this.mode].map(
        filterType => FILTER_TYPE_TO_KEY[filterType]
      )
    }
  },
  created() {
    this.debouncedUpdateUrl = debounce(this.updateUrl, 50);
    var params = getParamsFromURL();
    if (params.mode) {
      this.$store.commit('categoryManager/setMode', params.mode)
    };
    this.$store.commit("categoryManager/filters/setCurrents", {
        'start_date': params.start_date,
        'end_date': params.end_date,
        'sort_by': params.sort_by || 'updated_at',
        'sort_direction': params.sort_direction || 'desc',
        ...Object.fromEntries(
          this.modeFilterKeys.map(filterKey => [
            filterKey, parseInt(params[filterKey])
          ]).filter(([k, v]) => v)
        )
      }
    );
  }
}
</script>
