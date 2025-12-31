<template>
<form>
  <div class="form-group">
    <text-input
      label="Name"
      v-model="settings.name"
      max-length="255"
      required
    />
  </div>
  <div class="form-group">
    <select-input
      :items="campaignStatuses"
      value-key="key"
      label-key="value"
      v-model="settings.status"
      required>
      Status
    </select-input>
  </div>
  <div>
    <action-button
      :working="saving"
      @click="save"
      left-icon="save">Update Settings</action-button>
     <span class="text-warning" title="data is not final yet"><strong>*</strong></span> Changes might take a few minutes to take effect
  </div>
</form>
</template>
<script>
import { trafficGuard as backend } from '@/api'
import swal from 'sweetalert2'
export default {

  props: {
    campaignId: {
      type: Number,
    },
    campaignName: {
      type: String,
    },
    statuses: {
      type: Array,
      default: () => ([])
    },
    currentStatus: {
      type: String,
    }
  },

  data: () => ({
    saving: false,
    settings: {
      name: '',
      status: ''
    }
  }),

  created() {
    this.settings.status = this.currentStatus
    this.settings.name = this.campaignName
  },

  methods: {
    save() {
      this.saving = true
      backend.updateCampaignSettings({
        campaign_id: this.campaignId,
        payload: this.settings
      }, ({data}) => {
        this.saving = false
        swal('Campaign Settings Updated');
        window.location.reload();

      }, error => {
        if(error.response.status === 406) {
          swal('Could not Update Settings', error.response.data.error)
        }
        this.saving = false
      })
    }
  },

  computed: {
    campaignStatuses() {
      return this.statuses.map(status => {
        return {
          key: status,
          value: status,
        }
      })
    }
  }

}
</script>
