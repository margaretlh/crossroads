<template>
  <div class="row">
    <div class="col-lg-12">
      <div class="panel panel-primary">
        <div class="panel-heading">
          <strong>New Users - Edit Profile</strong>
        </div>
        <div class="panel-body">
          <form>
            <text-input
              v-model="new_user.email"
              :error="errors.email"
              class="col-sm-6"
              required
              label="Email"
            />
            <text-input
              v-model="new_user.first_name"
              :error="errors.first_name"
              class="col-sm-6 pd-left-zero"
              required
              label="First Name"
            />
            <text-input
              v-model="new_user.last_name"
              :error="errors.last_name"
              class="col-sm-6"
              required
              label="Last Name"
            />
            <text-input
              v-model="new_user.address_1"
              :error="errors.address_1"
              class="col-sm-6 pd-left-zero"
              required
              label="Address Line 1"
            />
            <text-input
              v-model="new_user.address_2"
              :error="errors.address_2"
              class="col-sm-6"
              label="Address Line 2"
            />
            <text-input
              v-model="new_user.city"
              :error="errors.city"
              required
              class="col-sm-6 pd-left-zero"
              label="City"
            />
            <text-input
              v-model="new_user.state"
              :error="errors.state"
              class="col-sm-6"
              label="State"
            />
            <text-input
              v-model="new_user.zip_code"
              :error="errors.zip_code"
              class="col-sm-6 pd-left-zero"
              label="Zip Code"
            />
            <text-input
              v-model="new_user.country"
              :error="errors.country"
              required
              class="col-sm-6"
              label="Country"
            />
            <text-input
              v-model="new_user.state"
              :error="errors.state"
              class="col-sm-6 pd-left-zero"
              label="State"
            />
            <text-input
              v-model="new_user.phone_number"
              :error="errors.phone_number"
              required
              class="col-sm-6"
              label="Phone Number"
            />
            <text-input
              v-model="new_user.company"
              :error="errors.company"
              class="col-sm-6 pd-left-zero"
              label="Company Name"
              required
            />
            <text-input
              v-model="new_user.company_website"
              :error="errors.company_website"
              class="col-sm-6"
              label="Company Website"
            />
            <text-input
              v-model="new_user.last_30_day_ad_revenue"
              :error="errors.last_30_day_ad_revenue"
              class="col-sm-6 pd-left-zero"
              label="Last 30 Days Ad Revenue"
            />
            <text-input
              v-model="new_user.hear_about"
              :error="errors.hear_about"
              class="col-sm-6"
              label="Hear About"
            />
            <text-input
              v-model="new_user.which_one"
              :error="errors.which_one"
              class="col-sm-6 pd-left-zero"
              label="Which One"
            />
            <text-input
              v-model="new_user.top_three_revenue_sites"
              :error="errors.top_three_revenue_sites"
              class="col-sm-6"
              label="Top Three Revenue Sites"
            />
            <text-input
              v-model="new_user.referred_by"
              :error="errors.referred_by"
              class="col-sm-6 pd-left-zero"
              label="Referred By"
            />
            <checkbox-input
              v-model="new_user.agree_not_click_ads"
              :error="errors.agree_not_click_ads"
              class="col-sm-6"
              label="Agree not click ads"
            />
            <checkbox-input
              v-model="new_user.no_incentives"
              :error="errors.no_incentives"
              class="col-sm-6 pd-left-zero"
              label="No Incentives"
            />
            <text-input
              v-model="new_user.user_sign"
              :error="errors.user_sign"
              class="col-sm-6"
              label="User Sign"
            />
            <text-input
              v-model="new_user.date"
              :error="errors.date"
              class="col-sm-6 pd-left-zero"
              label="Date"
            />
            <text-input
              v-model="new_user.signed_up_ip"
              :error="errors.signed_up_ip"
              class="col-sm-6"
              label="Signed Up IP"
            />
            <checkbox-input
              v-model="new_user.soft_deleted"
              :error="errors.soft_deleted"
              class="col-sm-6"
              label="Soft Deleted"
            />
            <br>
            <data-selector
              :options="account_manager_options"
              value-key="id"
              label-key="full_name"
              v-model="new_user.account_manager"
              :error="errors.account_manager"
              class="col-sm-6 pd-right-zero"
              label="Account Manager"
              required
            />
            <text-input
              v-model="new_user.three_ph_multiplier"
              :error="errors.three_ph_multiplier"
              class="col-sm-6 pd-left-zero"
              label="3PH Multiplier"
            />
            <data-selector
              :options="whitelabel_options"
              value-key="id"
              label-key="name"
              v-model="new_user.whitelabel_configuration"
              :error="errors.whitelabel_configuration"
              class="col-sm-6"
              label="Whitelabel Configuration"
            />
            <text-input
              v-model="new_user.username"
              :error="errors.username"
              class="col-sm-6 pd-left-zero"
              label="Username"
              required
            />
            <password-input
              v-model="new_user.password"
              :error="errors.password"
              class="col-sm-6"
              label="Password"
              with-strength-meter
            />
            <br>
            <h5>Account info</h5>
            <br>
            <data-selector
            :options="traffic_source_options"
            value-key="id"
            label-key="name"
            v-model="new_user.traffic_sources"
            :error="errors.traffic_sources"
            class="col-sm-6"
            label="Traffic Sources"
            multiple
            />
            <data-selector
              :options="traffic_flow_options"
              value-key="id"
              label-key="name"
              v-model="new_user.traffic_flow"
              :error="errors.traffic_flow"
              class="col-sm-6 pd-left-zero"
              label="Traffic Flow"
              multiple
            />
            <text-input
              v-model="new_user.content_sites"
              :error="errors.content_sites"
              class="col-sm-6"
              label="Content Sites"
            />
            <data-selector
              :options="feed_type_options"
              value-key="id"
              label-key="name"
              v-model="new_user.feed_types"
              :error="errors.feed_types"
              class="col-sm-6 pd-left-zero"
              label="Feed Types"
              multiple
            />
            <text-input
              v-model="new_user.revenue_share"
              :error="errors.revenue_share"
              class="col-sm-6"
              label="Revenue Share"
            />
            <data-selector
              :options="publisher_tracking_options"
              value-key="id"
              label-key="name"
              v-model="new_user.publisher_tracking"
              :error="errors.publisher_tracking"
              class="col-sm-6 pd-left-zero"
              label="Publisher Tracking"
              multiple
            />
            <textarea-input
              :rows="10"
              v-model="new_user.notes"
              :error="errors.notes"
              class="col-sm-12"
              label="Notes"
              :maxlength="4000"
            />
          </form>
        </div>
        <div class="panel-footer">
          <action-button
            :working="working"
            @click="approveNewUserProfile"
            class="btn-primary btn-sm mt-1 align-left">
            Approve
          </action-button>
          <action-button
            @click="denyNewUserProfile"
            class="btn-danger btn-sm mt-1 mr">
            Deny
          </action-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>

import {
  trafficGuard as backend
} from '@/api'
import swal from 'sweetalert2'

export default {
  props: {
    userId: {
      type: Number
    },
  },

  data: () => ({
    working: false,
    new_user: {
      username: '',
      password: '',
      first_name: '',
      last_name: '',
      email: '',
      company: '',
      address_1: '',
      address_2: '',
      city: '',
      zip_code: '',
      country: '',
      state: '',
      phone_number: '',
      company_website: '',
      last_30_day_ad_revenue: '',
      hear_about: '',
      which_one: '',
      top_three_revenue_sites: '',
      referred_by: '',
      agree_not_click_ads: '',
      no_incentives: '',
      user_sign: '',
      signed_up_ip: '',
      soft_deleted: '',
      account_manager: '',
      three_ph_multiplier: '',
      whitelabel_configuration: '',
      traffic_sources: [],
      traffic_flow: '',
      content_sites: '',
      feed_types: [],
      revenue_share: '',
      publisher_tracking: [],
      notes: ''
    },
    whitelabel_options: [],
    account_manager_options: [],
    traffic_flow_options: [],
    feed_type_options: [],
    publisher_tracking_options: [],
    traffic_source_options: [],
    errors: {}
  }),

  created() {
    this.loadNewUserProfile()
  },

  methods: {
    approveNewUserProfile() {
      this.loading = true
      this.working = true
      backend.approveNewUserProfile({
        userId: this.userId,
        ...this.new_user
      }, async response => {
        await swal({
          title: 'Success!',
          html: response.data.message,
          type: 'success',
        })
        location.replace('/admin/new_users/')
      }, error => {
        if (error.response.data.error) {
          swal({
            title: 'Failed!',
            html: error.response.data.message,
            type: 'error',
          })
        }
        this.errors = error.response.data
        this.working = false
      })
    },
    denyNewUserProfile() {
      this.loading = true
      this.working = true
      backend.denyNewUserProfile({
        userId: this.userId,
        ...this.new_user
      }, async response => {
        await swal({
          title: 'Success!',
          text: response.data.message,
          type: 'success',
        })
        location.replace('/admin/new_users/')
      }, error => {
        swal({
          title: 'Failed!',
          text: error.response.data.message,
          type: 'error',
        })
        this.errors = error.response.data
        this.working = false
      })
    },
    loadNewUserProfile() {
      this.loading = true
      backend.loadNewUserProfile({
        userId: this.userId,
      }, ({data}) => {
        this.new_user = data.new_user
        this.whitelabel_options = data.whitelabel_options
        this.account_manager_options = data.account_manager_options
        this.traffic_flow_options = data.traffic_flow_options
        this.feed_type_options = data.feed_type_options
        this.publisher_tracking_options = data.publisher_tracking_options
        this.traffic_source_options = data.traffic_source_options
      }, error => {
        this.errors = error.response.data
        this.loading = false
      })
    },
  }
}
</script>
