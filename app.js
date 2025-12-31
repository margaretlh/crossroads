import './bootstrap'
import Vue from 'vue'
import VTooltip from 'v-tooltip'
import { filters } from '@billow/js-helpers'
import VueApexCharts from 'vue-apexcharts'
import vSelect from 'vue-select'
import './authentication/install'
import './components/install'
import './crossroads/install'
import './trafficguard/install'
import './accounting/install'
import './admin/install'
import './notifications/install'
import './cost/install'
import store from './store'
import './modals'
import * as ModalDialogs from 'vue-modal-dialogs'
import vueFilePond from "vue-filepond";
import { mapGetters } from 'vuex'
Vue.use(filters)
Vue.use(ModalDialogs)
Vue.use(VTooltip)
VTooltip.options.defaultBoundariesElement = document.body;
Vue.use(VueApexCharts)
Vue.component('apexchart', VueApexCharts)
Vue.component('v-select', vSelect)
Vue.component('FilePond', vueFilePond())

Vue.prototype.$bus = new Vue()

let app = document.getElementById("vue-app")
if(app) {
  Promise.all([
    store.dispatch('auth/loadAuthUser')
  ]).then(() => {
    new Vue({

      el: '#vue-app',

      store,

      data: {
        sideNavIsOpen: true
      },

      methods: {
        hasPermission(permission) {
          if (this.isSuperAdmin) return true
          return this.permissions.includes(permission)
        },
        isAnAdmin() {
          return this.isAdmin
        },
        isASuperAdmin() {
          return this.isSuperAdmin
        },
        isAccountManager() {
          return this.permissions.includes('account_manager')
        }
      },

      created() {
        this.$bus.$on('toggle-side-bar', () => {
          this.sideNavIsOpen = !this.sideNavIsOpen
        })
      },

      mounted() {
        window.dispatchEvent(new CustomEvent("vue-app-mounted"));
      },

      computed: {
        ...mapGetters('auth', [
          'permissions',
          'isSuperAdmin',
          'isAdmin',
        ])
      }
    })
  })
}
