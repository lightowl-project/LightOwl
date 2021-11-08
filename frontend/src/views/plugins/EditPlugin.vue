<template>
  <div class="app-container">
    <el-row :gutter="20" justify="center">
      <el-form @submit.prevent="savePlugin">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span v-if="!form.id">{{ $t("Create Plugin") }}</span>
            <span v-else>{{ $t("Edit Plugin") }}</span>
            <el-button
              type="primary"
              :loading="is_loading"
              style="float: right"
              size="mini"
              @click.native.prevent="savePlugin"
            >
              <span>{{ $t("Save Changes") }}</span>
            </el-button>
          </div>
          <el-col :md="12">
            <el-row>
              <el-col :md="6">
                <el-form-item class="mb-0" :label="$t('Plugin name')">
                  <el-input v-model="form.name" />
                </el-form-item>
              </el-col>
              <el-col :md="6">
                <el-form-item class="mb-0" :label="$t('Plugin type')">
                  <el-select v-model="form.plugin_type" style="width: 100%">
                    <el-option
                      v-for="item in pluginTypeChoices"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <AceEditor
              v-model="form.config_file"
              lang="ini"
              theme="monokai"
              width="100%"
              height="700px"
              :options="{
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                fontSize: 14,
                highlightActiveLine: true,
                enableSnippets: true,
                showLineNumbers: true,
                tabSize: 2,
                showPrintMargin: false,
                showGutter: true,
              }"
              @init="editorInit"
            />
          </el-col>
          <el-col :md="12">
            <el-table
              stripe
              border
              size="mini"
              highlight-current-row
              :data="form.config"
              style="width: 100%"
              :default-sort="{
                prop: 'key',
                order: 'descending',
              }"
            >
              <el-table-column prop="key" :label="$t('Name')" :width="150" />
              <el-table-column prop="type" :label="$t('Type')" :width="180">
                <div slot-scope="{ $index, row }" class="d-flex">
                  <el-select v-model="row.type" style="width: 100%">
                    <el-option
                      v-for="item in availableType"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </div>
              </el-table-column>

              <el-table-column
                prop="default_value"
                :label="$t('Default Value')"
                :width="300"
              >
                <div slot-scope="{ $index, row }" class="d-flex">
                  <el-input
                    v-if="['str', 'int', 'float'].indexOf(row.type) !== -1"
                    v-model="row.default_value"
                    :type="renderType(row)"
                    :step="renderStep(row)"
                  />
                  <span v-else-if="row.type === 'bool'">
                    <el-switch v-model="row.default_value" />
                  </span>
                  <span v-else-if="row.type === 'list'">
                    <vue-tags-input
                      v-model="row.default_value"
                      :tags="tags"
                      placeholder=""
                      @tags-changed="(newTags) => (tags = newTags)"
                    />
                  </span>
                </div>
              </el-table-column>
              <el-table-column prop="description" :label="$t('Description')">
                <div slot-scope="{ $index, row }" class="d-flex">
                  <el-input v-model="row.description" type="textarea" />
                </div>
              </el-table-column>
            </el-table>
          </el-col>
        </el-card>
      </el-form>
    </el-row>
  </div>
</template>

<script>
import VueTagsInput from "@johmun/vue-tags-input"
import AceEditor from "vuejs-ace-editor"
import request from "@/utils/request"

export default {
  components: { AceEditor, VueTagsInput },
  data: (vm) => ({
    is_loading: false,
    form: {
      id: null,
      name: "",
      plugin_type: "input",
      config_file: "",
      config: []
    },
    tags: [],
    pluginTypeChoices: [
      {
        value: "input",
        label: vm.$t("Input")
      },
      {
        value: "output",
        label: vm.$t("Output")
      }
    ],
    availableType: [
      {
        value: "int",
        label: vm.$t("Integer")
      },
      {
        value: "float",
        label: vm.$t("Float")
      },
      {
        value: "str",
        label: vm.$t("String")
      },
      {
        value: "bool",
        label: vm.$t("Boolean")
      },
      {
        value: "list",
        label: vm.$t("List")
      }
    ]
  }),

  watch: {
    "form.config_file"(val) {
      const regexp = /{{([\s*a-zA-Z_\s*]*)}}/g

      const existing_variables = []
      for (const field of this.form.config) {
        existing_variables.push(field.key)
      }

      const new_variables = []
      const total_variables = []
      for (let variable of [...val.matchAll(regexp)]) {
        variable = variable[1].trim()
        if (!variable) continue
        total_variables.push(variable)
        if (existing_variables.indexOf(variable) === -1) {
          new_variables.push(variable)
        }
      }

      const new_fields = []
      for (const variable of new_variables) {
        new_fields.push({
          key: variable,
          type: "str",
          description: "",
          defaultValue: ""
        })
      }

      for (const field of this.form.config) {
        if (total_variables.indexOf(field.key) !== -1) new_fields.push(field)
      }

      this.form.config = new_fields
    }
  },

  mounted() {
    if (this.$route.params.id) {
      this.form.id = this.$route.params.id
      request.get(`/api/v1/plugins/${this.form.id}`).then((response) => {
        this.form = {
          id: response.data._id,
          name: response.data.name,
          plugin_type: response.data.plugin_type,
          config_file: response.data.config_file,
          config: response.data.config
        }
      })
    }
  },

  methods: {
    editorInit: function() {
      require("brace/ext/language_tools") // language extension prerequsite...
      require("brace/mode/ini")
      require("brace/theme/monokai")
    },

    renderType(data) {
      const mapping = {
        int: "number",
        float: "number",
        str: "text"
      }

      return mapping[data.type]
    },

    renderStep(data) {
      return data.type === "float" ? 0.1 : 1
    },

    savePlugin() {
      this.is_loading = true

      if (this.form.id) {
        request.put(`/api/v1/plugins/${this.form.id}`, this.form).then(() => {
          this.is_loading = false
          this.$message({
            type: "success",
            message: this.$t("Plugin successfully updated"),
            showClose: true
          })

          this.$router.push("/plugins")
        })
      } else {
        request.post("/api/v1/plugins/", this.form).then(() => {
          this.is_loading = false
          this.$message({
            type: "success",
            message: this.$t("Plugin successfully created"),
            showClose: true
          })

          this.$router.push("/plugins")
        })
      }
    }
  }
}
</script>
