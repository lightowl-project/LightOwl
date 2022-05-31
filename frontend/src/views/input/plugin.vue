<template>
  <el-form label-position="right" label-width="30%" :model="form">
    <div v-if="is_loaded">
      <el-row>
        <el-col class="ml-auto" :md="20">
          <el-alert
            :title="$t('Description')"
            type="info"
            effect="dark"
            :closable="false"
            show-icon
          >
            <p v-html="mapping.description" />

          </el-alert>
          <p style="font-size: 15px">
            <a :href="mapping.url" target="_blank">
              <i class="fa fa-info-circle" />&nbsp;&nbsp;{{ $t("Open Telegraf documentation") }}
            </a>
          </p>
        </el-col>
      </el-row>
      <el-row class="mt-2">
        <el-form-item v-if="!edit" :label="$t('Advanced')">
          <el-switch v-model="advanced" />
        </el-form-item>
        <div v-for="(attrs, name) in mapping.properties" :key="name">
          <el-form-item
            v-if="!attrs.advanced || (attrs.advanced && advanced)"
            :label="attrs.title"
            :error="errors[name]"
            :required="mapping.required.indexOf(name) !== -1"
            :show-message="errors[name] !== ''"
          >
            <div v-if="attrs.type === 'array'">
              <div>
                <el-tag
                  v-for="tag in form[name]"
                  :key="tag"
                  closable
                  type="info"
                  size="small"
                  :disable-transitions="false"
                  @close="handleTagClose(tag, name)"
                >
                  {{ tag }}
                </el-tag>
                <el-input
                  v-if="tags[name].visible"
                  v-model="tags[name].value"
                  class="input-new-tag"
                  style="width: 50%"
                  size="mini"
                  @keyup.enter.native.prevent="handleTagInput(name)"
                  @blur="handleTagInput(name)"
                />
                <el-button
                  v-else
                  plain
                  type="primary"
                  size="mini"
                  @click="showTagsInput(name)"
                >
                  <i class="fa fa-plus" />
                </el-button>
              </div>
              <small v-html="attrs.description" />
            </div>
            <div v-else-if="attrs.type === 'number'">
              <el-input-number
                v-model="form[name]"
                controls-position="right"
                :min="1.0"
                :precision="1"
                :step="0.1"
                size="mini"
              /><br>
              <small v-html="attrs.description" />
            </div>
            <div v-else-if="attrs.type === 'integer'">
              <el-input-number
                v-model="form[name]"
                controls-position="right"
                size="mini"
              /><br>
              <small v-html="attrs.description" />
            </div>
            <div v-else-if="attrs.type === 'boolean'">
              <el-switch v-model="form[name]" /><br>
              <small v-html="attrs.description" />
            </div>
            <div v-else-if="attrs.allOf">
              <div>
                <el-select v-model="form[name]" size="mini" style="width: 50%">
                  <el-option
                    v-for="val in getDefinitions(name)"
                    :key="val"
                    :value="val"
                  >{{ val }}</el-option>
                </el-select>
              </div>
              <small v-html="attrs.description" />
            </div>
            <div v-else>
              <el-input
                v-model="form[name]"
                size="small"
                :type="attrs.input_type === 'password' ? 'password' : 'text'"
                style="width: 50%"
              /><br>
              <small v-html="attrs.description" />
            </div>
          </el-form-item>
        </div>
      </el-row>
      <el-row class="text-center mt-2">
        <el-button v-if="!edit" type="warning" plain @click="$emit('back')">
          {{ $t("Back") }}
        </el-button>
        <el-button type="primary" @click="submitForm()">
          {{ $t("Save") }}
        </el-button>
      </el-row>
    </div>
  </el-form>
</template>

<script>
import request from "@/utils/request"

export default {
  props: {
    edit: {
      type: Boolean,
      default: false
    },
    pluginName: {
      type: String,
      required: true
    },
    pluginConfig: {
      type: Object,
      required: true
    }
  },

  data: () => {
    return {
      is_loaded: false,
      advanced: false,
      mapping: {},
      errors: {},
      form: {},
      tags: {}
    }
  },

  mounted() {
    this.advanced = this.edit
    const params = { plugin_name: this.pluginName }
    request
      .get("/api/v1/inputs/schema/", { params: params })
      .then((response) => {
        const form = {}
        const tags = {}
        for (const [key, values] of Object.entries(response.data.properties)) {
          let default_value = values.default
          if (this.pluginConfig[key]) {
            default_value = this.pluginConfig[key]
          }

          if (values.type === "number") {
            if (!default_value) default_value = 0
          } else if (values.type === "array") {
            if (!default_value) default_value = []

            tags[key] = {
              visible: false,
              value: ""
            }
          } else if (values.type === "boolean") {
            default_value = default_value === true
          } else {
            if (!default_value) default_value = ""
          }

          form[key] = default_value
        }

        this.tags = tags
        this.mapping = response.data
        if (!this.mapping.required) this.mapping.required = []

        this.$nextTick(() => {
          this.is_loaded = true
          this.$forceUpdate()
          this.form = form
        })
      })
  },

  methods: {
    getDefinitions(key) {
      let ref = this.mapping.properties[key].allOf[0].$ref
      ref = ref.replace("#/definitions/", "")
      return this.mapping.definitions[ref].enum
    },

    showTagsInput(key) {
      this.tags[key].visible = true
      this.$forceUpdate()
    },

    handleTagClose(tag, key) {
      this.form[key].splice(this.form[key].indexOf(tag), 1)
      this.$forceUpdate()
    },

    handleTagInput(key) {
      const value = this.tags[key].value
      if (value) this.form[key].push(value)
      this.tags[key].visible = false
      this.tags[key].value = ""
      this.$forceUpdate()
    },

    submitForm() {
      let error = false
      for (const [key, values] of Object.entries(this.mapping.properties)) {
        const form_value = this.form[key]
        const value_type = values.type

        if (this.mapping.required.indexOf(key) === -1) continue

        switch (value_type) {
          case "array":
            if (!form_value.length) {
              error = true
              this.errors[key] = this.$t("Please set at least one tag")
            }
            break
        }
      }

      this.$forceUpdate()
      if (error) return

      // Now validate config against schema
      const form = {
        plugin_name: this.pluginName,
        config: this.form
      }

      request
        .post("/api/v1/inputs/config/generate", form)
        .then((response) => {
          this.$emit("finish", this.form)
        })
        .catch((err) => {
          if (err.response.status === 400) {
            const errors = {}
            for (const [key, error] of Object.entries(
              err.response.data.detail
            )) {
              errors[key] = error
            }

            this.errors = errors
          }
        })
    }
  }
}
</script>
