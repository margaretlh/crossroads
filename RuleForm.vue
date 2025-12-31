<template>
  <div>
    <div class="row" v-if="!!params?.owner_username" >
      <div class="form-group col-md-4">
        <text-input
          disabled label="Owner" :value="params?.owner_username"
        />
      </div>
    </div>
    <div class="row" v-if="!!tpaOptions" >
      <div class="form-group col-md-8">
        <data-selector 
          required
          v-model="params.singleTpaId"
          :options="tpaOptions"
          label="TPA"
        />
      </div>
    </div>
    <div class="row">
      <div class="form-group col-md-4">
        <date-picker
          label required v-model="params.date_effective"
          :error="errors.date_effective"
        >Date effective</date-picker>
      </div>
      <div class="form-group col-md-6">
        <radio-group
          required
          v-model="params.rule_type"
          :error="errors.rule_type"
          class="form-group-radio-m0 form-group-radio-inline"
          :items="[
            {value: 1, label: 'Revenue'},
            {value: 2, label: 'Gross Profit'}
          ]"
          value-key="value"
          label-key="label"
        >Rule type</radio-group>
      </div>
    </div>
    <div class="row">
      <div class="form-group col-md-4">
        <text-input
          label="Percentage" required v-model="params.percentage"
          :error="errors.percentage"
        />
      </div>
      <div class="form-group col-md-4">
        <text-input
          label="Overhead" required v-model="params.overhead"
          :error="errors.overhead"
        />
      </div>
    </div>
    <div class="divider mb-2"/>
    <div class="is-flex">
      <div class="flex-grow">
        <action-button
          v-if="onDelete"
          class="btn-danger"
          :working="deleting"
          @click="() => {
            yesnoSwal(
              'Are you sure you want to delete this rule?',
              () => {
                deleting = true;
                onDelete(params, () => {
                  deleting = false;
                  onDeleted();
                }, () => {
                  deleting = false;
                })
              }, () => {}
            )
          }"
        >Delete</action-button>
      </div>
      <button
        v-if="onCancel"
        class="btn-default mr-1"
        @click="onCancel"
      >Cancel</button>
      <action-button
        class="btn-primary"
        :working="saving"
        @click="save"
      >Save</action-button>
    </div>
  </div>
</template>
<script>
import yesno_swal from "@/mixins/yesno_swal"
export default {
  mixins: [yesno_swal],
  props: {
    initialParams: {
      type: Object,
      default: () => ({
        date_effective: null,
        overhead: null,
        percentage: null,
        rule_type: null,
      }),
    },
    onDelete: {
      type: Function,
      default: undefined
    },
    onCancel: {
      type: Function,
      default: undefined
    },
    onSave: {
      type: Function,
      required: true
    },
    onSaved: {
      type: Function,
      required: true
    },
    onDeleted: {
      type: Function,
      default: undefined
    },
    tpaOptions: {
      type: Array,
      default: undefined
    },
  },
  data: () => ({
    params: {},
    saving: false,
    deleting: false,
    errors: {}
  }),
  methods: {
    save() {
      this.saving = true;
      this.onSave(this.params, () => {
        this.saving = false;
        this.errors = {};
        this.onSaved();
      }, error => {
        this.saving = false;
        const nonFieldErrors = error.response.data.non_field_errors || [];
        if (nonFieldErrors.length) {
          swal({
            title: 'Failed!',
            text: nonFieldErrors[0],
            type: 'error',
          });          
        }
        this.errors = error.response.data;
      })
    }
  },
  created() {
    this.params = this.initialParams;
  }
  
}
</script>