<template>
  <loader v-bind="{ loading }">
    <div class="panel panel-primary">
      <div class="panel-heading">
        Publishers
        <button
            v-if="isAnAdmin"
            class="btn btn-xs btn-default pull-right"
            @click="adding_publisher = true">
          Associate Publisher
        </button>
        <button
            class="btn btn-xs btn-default ms-4 pull-right"
            @click="goBack">
          ← Back
        </button>
      </div>
      <div class="panel-body">
        <d-table
            :raw-columns="publisher_columns"
            :table-data="publishers"
        />
      </div>
    </div>

    <div class="panel panel-primary">
      <div class="panel-heading">
        Admins
        <button
            v-if="isAnAdmin"
            class="btn btn-xs btn-default pull-right"
            @click="adding_admin = true">
          Add Admin
        </button>
      </div>
      <div class="panel-body">
        <d-table
            :raw-columns="admin_columns"
            :table-data="admins"
        />
      </div>
    </div>
    <div v-if="isAnAdmin">
      <div class="panel panel-primary">
        <div class="panel-heading">Whitelabel Settings</div>
        <div class="panel-body">
          <form method="post">
            <div class="row">
              <div class="col-lg-6">
                <text-input
                    :error="errors.name"
                    v-model="config.name"
                    label="Name"
                />
              </div>
              <div class="col-lg-6">
                <text-input
                    :error="errors.title"
                    v-model="config.title"
                    label="Title"
                />
              </div>
            </div>
            <div class="row">
              <div :class="{
              'col-lg-6': config.pay_difference_to_id === original_pay_difference_to_id,
              'col-lg-4': config.pay_difference_to_id !== original_pay_difference_to_id,
            }">
                <select-input
                    :error="errors.pay_difference_to_id"
                    :items="publisher_list"
                    value-key="id"
                    label-key="username"
                    :value="config.pay_difference_to_id"
                    @input="updatePayDifferenceTo"
                    label>
                  Pay Difference To
                </select-input>
              </div>
              <div class="col-lg-4" v-if="config.pay_difference_to_id !== original_pay_difference_to_id">
                <date-picker
                    :error="errors.effective_date"
                    v-model="config.effective_date"
                    label>
                  Effective Date
                  <icon icon="info" v-tooltip="'When updating the pay difference to field you may choose to update existing line items for this whitelabel account. If you do not wish to update existing line items simply clear this field.'"/>
                </date-picker>
              </div>
              <div :class="{
                'col-lg-6': config.pay_difference_to_id === original_pay_difference_to_id,
                'col-lg-4': config.pay_difference_to_id !== original_pay_difference_to_id,
              }">
                <text-input
                    :error="errors.logo_icon"
                    v-model="config.logo_icon"
                    label="Logo Icon"
                />
              </div>
            </div>
            <div class="row">
              <div class="col-lg-4">
                <text-input
                    :error="errors.primary_color"
                    v-model="config.primary_color"
                    label="Primary Color"
                />
              </div>
              <div class="col-lg-4">
                <text-input
                    :error="errors.secondary_color"
                    v-model="config.secondary_color"
                    label="Secondary Color"
                />
              </div>
              <div class="col-lg-4">
                <text-input
                    :error="errors.text_color"
                    v-model="config.text_color"
                    label="Text Color"
                />
              </div>
            </div>
            <div class="row">
              <div class="col-lg-4">
                <date-picker
                    ref="deactivatedDateChild"
                    @input="dateSelected"
                    v-model="config.deactivation_date"
                    label>
                </date-picker>
              </div>
            </div>
            <action-button
                @click="saveConfig"
                :working="saving"
                class="btn btn-primary">
              Save
            </action-button>

            <action-button
                v-if="isSuperAdmin"
                @click="deactivate"
                :working="deactivating"
                class="btn btn-primary">
              Deactivate
             </action-button>

          </form>
        </div>
      </div>
    </div>

    <modal v-if="adding_publisher" @close="adding_publisher = false" title="Associate Publisher">
      <form method="post">
        <div class="modal-body">
          <select-input
              :error="errors.publisher_id"
              :items="publisher_list"
              value-key="id"
              label-key="username"
              label
              v-model="associate_publisher">
            Publisher
          </select-input>
        </div>
        <div class="modal-footer">
          <action-button
              @click="addPublisher">
            Add Publisher
          </action-button>
        </div>
      </form>
    </modal>

    <modal v-if="adding_admin" @close="adding_admin = false" title="Add Admin">
      <form method="post">
        <div class="modal-body">
          <select-input
              :error="errors.admin_id"
              :items="publisher_list"
              value-key="id"
              label-key="username"
              label
              v-model="admin_id">
            User
          </select-input>
        </div>
        <div class="modal-footer">
          <action-button
              @click="addAdmin">
            Add Admin
          </action-button>
        </div>
      </form>
    </modal>
  </loader>
</template>
<script>
import { publishers as backend } from '@/api'
import TableColumn from '../../models/table-column'
import yesno_swal from '../../mixins/yesno_swal'
import moment from 'moment'

export default {

  props: {
    whiteLabelId: Number,
    isSuperAdmin: Boolean,
  },

  mixins: [
    yesno_swal
  ],

  data: () => ({
    loading: true,
    saving: false,
    deactivating: false,
    adding_publisher: false,
    adding_admin: false,
    associate_publisher: '',
    admin_id: '',
    original_pay_difference_to_id: '',
    publisher_list: [],
    publishers: [],
    admins: [],
    errors: {},
    config: {
      name: '',
      logo_icon: '',
      primary_color: '',
      secondary_color: '',
      text_color: '',
      pay_difference_to_id: '',
      title: '',
      effective_date: '',
      active: true,
      deactivation_date: null,
    },
    isDeactivationDateValid: false,

    admin_columns: [
      new TableColumn({ name: 'username', label: 'Username' })
    ],
    publisher_columns: [
      new TableColumn({
        name: 'publisher__username',
        label: 'Username',
        hide_text: true,
        component: 'table-link',
        component_payload: {
          path: '/whitelabel/detail/{id}/',
          textKey: 'publisher__username'
        }
      }),
      new TableColumn({
        name: 'impersonate',
        label: 'Actions',
        hide_text: true,
        component: 'table-link',
        component_payload: {
          path: '/impersonate/{publisher_id}',
          textKey: 'textKey'
        }
      })
    ]
  }),

  async created() {
    await backend.loadWhiteLabelSettings(this.whiteLabelId, ({data}) => {
      this.publishers = data.publishers.map(publisher => {
        publisher.textKey = 'impersonate'
        return publisher
      })
      this.admins = data.admins
      this.config = data.config
      this.config.effective_date = moment().subtract(1, 'month').startOf('month')
      this.original_pay_difference_to_id = this.config.pay_difference_to_id
      this.publisher_list = data.publisher_list
    })
    this.loading = false
  },

  methods: {
    goBack() {
      window.location.href = '/whitelabel';
    },

    deactivate() {
      this.deactivating = true;
      this.$nextTick(() => {
        if (this.$refs.deactivatedDateChild) {
          this.$refs.deactivatedDateChild.show(); // Show the date picker
        }
      });
    },

    dateSelected(value) {
      if (value) {
        this.config.deactivation_date = value;
        this.validateDeactivationDate();
      }
    },

    validateDeactivationDate() {
      if (!this.config.deactivation_date) {
        this.isDeactivationDateValid = false;
        return;
      }
      const selectedDate = moment(this.config.deactivation_date, 'YYYY-MM-DD', true);
      const today = moment().format('YYYY-MM-DD');
      this.isDeactivationDateValid = selectedDate.isSameOrAfter(today);

      if (this.isDeactivationDateValid) {
        // Start Deactivation process if deactivation date is today
        if (selectedDate.isSame(today)) {
          this.config.active = false; // Set status to inactive when valid date is selected
          this.finalizeDeactivation();
        } else {
          // For future dates, no immediate deactivation,
          this.deactivating = false; // Reset the deactivating flag
          this.config.active = true; // Keep the account active until the date arrives
        }
      } else {
        // Handle invalid date selection (before today)
        this.deactivating = false; // Ensure no deactivation is triggered
        this.config.active = true; // Keep the account active
      }
    },

    finalizeDeactivation() {
      backend.deactivateWhiteLabelSettings({
        whiteLabelId: this.whiteLabelId,
        deactivation_date: this.config.deactivation_date
      }, () => {
        // Deactivation successful
        this.deactivating = false;
        this.config.active = false; // Set the status to inactive after deactivation

        // Revoke White Label Admin access
        this.removeAllAdmins();
      }, (error) => {
        this.deactivating = false;
        this.errors = error.response.data;
      });
    },

    removeAllAdmins() {
      backend.removesWhiteLabelAdmins({
        admin_id: this.admin_id,
        whiteLabelId: this.whiteLabelId
      }, ({}) => {
        location.reload()
      }, error => this.errors = error.response.data)
    },

    saveConfig() {
      this.saving = true
      this.config.effective_date = this.config.effective_date.format('YYYY-MM-DD')
      backend.updateWhiteLabelSettings({
        whiteLabelId: this.whiteLabelId,
        config: this.config
      }, ({}) => {
        this.saving = false
      }, error => {
        this.errors = error.response.data
        this.saving = false
      })
    },

    updatePayDifferenceTo(value) {
      this.config.pay_difference_to_id = value ? Number(value) : ''
    },

    addPublisher() {
      backend.associateWhiteLabelPublisher({
        publisher_id: this.associate_publisher,
        whiteLabelId: this.whiteLabelId
      }, () => {
        location.reload()
      }, error => this.errors = error.response.data)
    },

    addAdmin() {
      backend.addWhiteLabelAdmin({
        admin_id: this.admin_id,
        whiteLabelId: this.whiteLabelId
      }, () => {
        location.reload()
      }, error => this.errors = error.response.data)
    }
  },

  computed: {
    isAnAdmin() {
      return this.isSuperAdmin || this.$root.isAnAdmin();
    }
  },
}
</script>
