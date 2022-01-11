<template>
  <div>
    <el-skeleton style="margin-top: 10px; width: 100%" :loading="!rule.field" animated>
      <template slot="template">
        <el-skeleton-item
          variant="image"
          style="width: 100%; height: 240px;"
        />
      </template>
    </el-skeleton>
    <chart
      v-if="rule.field && getFieldType() !== 'string'"
      ref="chart"
      :agent_ids="rule.agents"
      :collector="rule"
    />
    <el-form ref="form" :model="rule" label-position="top">
      <el-row :gutter="10">
        <el-col v-if="!rule._id" :md="8">
          <el-form-item :label="$t('Agents')">
            <el-select v-model="rule.agents" style="width: 100%" filterable multiple>
              <el-option v-for="agent in agents_choices" :key="agent._id" :label="render_asset_label(agent)" :value="agent._id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :md="8">
          <el-form-item :label="$t('Name')">
            <el-input v-model="rule.name" />
          </el-form-item>
        </el-col>
        <el-col :md="8">
          <el-form-item :label="$t('Priority')">
            <el-select v-model="rule.priority" style="width: 100%" filterable>
              <el-option :label="$t('Critical')" :value="1" />
              <el-option :label="$t('High')" :value="2" />
              <el-option :label="$t('Medium')" :value="3" />
              <el-option :label="$t('Low')" :value="4" />
              <el-option :label="$t('Info')" :value="5" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :md="24">
          <h3>{{ $t("Rule") }}:</h3>
          <table class="table" style="width: 100%; text-align: center">
            <tbody>
              <tr>
                <td>
                  <b>{{ $t("IF") }}</b>
                </td>
                <td>
                  <el-select
                    v-model="rule.measurement"
                    style="width: 100%"
                    filterable
                    :placeholder="$t('Measurement')"
                    @change="fetchFields()"
                  >
                    <el-option
                      v-for="item in measurements_choices"
                      :key="item"
                      :label="item"
                      :value="item"
                    />
                  </el-select>
                </td>
                <td>
                  <el-select
                    v-model="rule.field"
                    style="width: 100%"
                    filterable
                    :placeholder="$t('Field')"
                    @change="fieldChange()"
                  >
                    <el-option
                      v-for="(type_, field) in fields_choices"
                      :key="field"
                      :label="field"
                      :value="field"
                    >
                      <span style="float: left">{{ field }}</span>
                      <b style="float: right; color: #8492a6; font-size: 13px">
                        {{ type_ }}
                      </b>
                    </el-option>
                  </el-select>
                </td>
                <td>
                  <el-select
                    v-model="rule.operator"
                    :placeholder="$t('Operator')"
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option
                      v-for="(text, value) in operator_choices"
                      :key="value"
                      :label="text"
                      :value="value"
                    />
                  </el-select>
                </td>
                <td>
                  <el-input
                    v-model="rule.pattern"
                    :step="0.1"
                    :type="renderTypePattern()"
                    :placeholder="$t('Pattern')"
                  />
                </td>
                <td>
                  <b>{{ $t('FOR') }}</b>
                </td>
                <td>
                  <el-select
                    v-model="rule.duration"
                    :placeholder="$t('Duration')"
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option
                      v-for="duration in duration_choices"
                      :key="duration"
                      :label="$t(duration)"
                      :value="duration"
                    />
                  </el-select>
                </td>
              </tr>
            </tbody>
          </table>
        </el-col>
      </el-row>
      <el-row style="margin-top: 20px;" :gutter="10">
        <h3>{{ $t("When an alert is raised") }}:</h3>
        <el-col :md="12">
          <label>{{ $t('Send mail') }}: </label>
          <el-switch
            v-model="rule.sendMail"
          />

          <el-form-item v-if="rule.sendMail" :label="$t('Email Recipients')">
            <el-select
              v-model="rule.mailTo"
              multiple
              filterable
              allow-create
              default-first-option
              style="width: 100%"
            >
              <el-option
                v-for="email in email_addresses"
                :key="email"
                :label="email"
                :value="email"
              />
            </el-select>
          </el-form-item>

        </el-col>
        <!-- <el-col :md="12">
          <label>{{ $t('Send SMS') }}: </label>
          <el-switch
            v-model="rule.sendSMS"
          />

          <el-form-item v-if="rule.sendSMS" :label="$t('SMS Recipients')">
            <el-select
              v-model="rule.smsTo"
              multiple
              filterable
              allow-create
              default-first-option
              style="width: 100%"
            >
              <el-option
                v-for="number in phone_numbers"
                :key="number"
                :label="number"
                :value="number"
              />
            </el-select>
          </el-form-item>
        </el-col> -->
      </el-row>
    </el-form>
  </div>
</template>

<script>
import request from "@/utils/request"
import Chart from "@/components/Chart.vue"
import renderMixin from "@/mixins/renderMixin.js"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  mixins: [renderMixin],
  components: { Chart },
  props: {
    agent_id: {
      type: String,
      default: ""
    },
    rule_id: {
      type: String,
      default: null
    }
  },

  data: () => ({
    agents_choices: [],
    measurements_choices: [],
    operator_choices: [],
    duration_choices: ["oneshot", "1m", "5m", "10m", "1h", "2h", "6h"],
    fields_choices: [],
    email_addresses: [],
    phone_numbers: [],
    rule: {
      enabled: true,
      priority: 3,
      name: "",
      agents: [],
      description: "",
      remediation: "",
      measurement: "",
      field: "",
      operator: "",
      pattern: "",
      duration: "oneshot",
      sendMail: true,
      mailTo: [],
      sendSMS: false,
      smsTo: []
    }
  }),

  watch: {
    "rule.field"() {
      if (this.getFieldType() !== "string" && this.rule.field) {
        if (this.$refs.chart) this.$refs.chart.fetchData()
      }
    },

    "rule.measurement"() {
      this.fields_choices = []
      this.rule.field = ""
    },

    "rule.agents"() {
      this.fetch_measurements()
    }
  },

  beforeMount() {
    this.fetch_emails_phones()
    this.fetch_agents()

    if (this.rule_id) {
      request.get(`/api/v1/rules/${this.rule_id}`).then((response) => {
        this.rule = response.data
        // this.rule.agents = response.data.agents
        this.fetch_measurements()
        this.fetchFields(this.rule.field)
      })
    }
  },

  methods: {
    fetch_emails_phones() {
      request.get("/api/v1/rules/data/mailsms").then((response) => {
        this.email_addresses = response.data.emails
        this.phone_numbers = response.data.phones
      })
    },

    async fetch_agents() {
      const response = await request.get("/api/v1/agents/", { params: { all: true }})
      this.agents_choices = response.data
    },

    async fetch_measurements() {
      this.measurements_choices = []
      const tmp_measurements = {}
      for (const i in this.rule.agents) {
        const agent_id = this.rule.agents[i]
        const response = await request.get(`/api/v1/inputs/measurements/${agent_id}`)

        for (const measurement of response.data) {
          if (tmp_measurements[measurement]) {
            tmp_measurements[measurement] += 1
          } else {
            tmp_measurements[measurement] = 1
          }
        }
      }

      let tmp = Object.keys(tmp_measurements)
      if (this.rule.agents.length > 1) {
        tmp = []
        for (const [measurement, number] of Object.entries(tmp_measurements)) {
          if (number === this.rule.agents.length) {
            tmp.push(measurement)
          }
        }
      }

      this.measurements_choices = tmp
    },

    checkEmails() {
      if (!this.rule.mailTo.length) {
        this.$message({
          type: "error",
          message: this.$t("Fill at least one email address")
        })

        return false
      }

      const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

      for (const email of this.rule.mailTo) {
        const res = re.test(String(email).toLowerCase())
        if (!res) {
          this.$message({
            type: "error",
            message: `${email} ${this.$t("is not a valid email address")}`
          })
          return false
        }
      }

      return true
    },

    checkPhoneNumbers() {
      if (!this.rule.smsTo.length) {
        this.$message({
          type: "error",
          message: this.$t("Fill at least one phone number")
        })

        return false
      }

      const re = /^[\+]?([0-9][\s]?|[0-9]?)([(][0-9]{3}[)][\s]?|[0-9]{3}[-\s\.]?)[0-9]{3}[-\s\.]?[0-9]{4,6}$/im

      for (const phone of this.rule.smsTo) {
        const res = re.test(String(phone).toLowerCase())
        if (!res) {
          this.$message({
            type: "error",
            message: `${phone} ${this.$t("is not a valid phone number")}`
          })
          return false
        }
      }

      return true
    },

    fetchFields(field) {
      this.rule.field = ""
      request
        .get("/api/v1/inputs/mapping/", {
          params: { measurement: this.rule.measurement }
        })
        .then((response) => {
          this.fields_choices = response.data

          if (field) {
            this.rule.field = field
          }

          this.constructOperator()
        })
    },

    constructOperator() {
      const field_type = this.getFieldType()

      const options = {
        eq: this.$t("eq"),
        neq: this.$t("neq")
      }

      if (field_type === "string") {
        options["contains"] = this.$t("contains")
        options["notcontains"] = this.$t("notcontains")
        options["startsWith"] = this.$t("startsWith")
        options["endsWith"] = this.$t("endsWith")
      } else if (["integer", "float"].indexOf(field_type) > -1) {
        options["lt"] = this.$t("lt")
        options["lte"] = this.$t("lte")
        options["gt"] = this.$t("gt")
        options["gte"] = this.$t("gte")
      }

      this.operator_choices = options
    },

    fieldChange() {
      this.rule.pattern = null
      this.constructOperator()
    },

    getFieldType() {
      return this.fields_choices[this.rule.field]
    },

    renderTypePattern() {
      const field_type = this.getFieldType()

      const mapping = {
        string: "text",
        float: "number",
        integer: "number"
      }

      return mapping[field_type]
    },

    saveRule() {
      const data = Object.assign({}, this.rule)

      if (!data.name || !data.priority || !data.measurement || !data.field || !data.operator || !data.pattern) {
        this.$message({
          type: "error",
          message: this.$t("Invalid rule")
        })
        return
      }

      if (this.rule.sendMail) {
        if (!this.checkEmails()) { return false }
      }

      if (this.rule.sendSMS) {
        if (!this.checkPhoneNumbers()) { return false }
      }

      if (!this.rule_id) {
        request.post("/api/v1/rules/", data).then((response) => {
          this.$emit("save")
          this.$message({
            type: "success",
            message: this.$t("Rule successfully created"),
            showClose: true
          })
        })
      } else {
        request.put(`/api/v1/rules/${this.rule_id}`, data).then((response) => {
          this.$emit("save")
          this.$message({
            type: "success",
            message: this.$t("Rule successfully updated"),
            showClose: true
          })
        })
      }
    }
  }
})
</script>
