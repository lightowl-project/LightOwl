<template>
  <div>
    <el-table
      ref="lightOwlTable"
      v-loading="loading"
      size="mini"
      stripe
      :data="tableData"
      :row-key="rowKey"
      style="width: 100%"
      highlight-current-row
      :default-sort="defaultSort"
      :empty-text="$t('No data found')"
      header-row-class-name="thead-light"
      @selection-change="handleSelectionChange"
      @row-click="rowClick"
      @sort-change="sortChange"
    >
      <slot name="columns" />
    </el-table>
    <div
      slot="footer"
      class="
        col-12
        d-flex
        justify-content-center justify-content-sm-between
        flex-wrap
        pl-1
        pb-1
      "
    >
      <p class="card-category m-0 pagination-info" style="float: left">
        {{ $t("Showing") }} {{ pagination.from + 1 }} {{ $t("to") }}
        {{ pagination.to }} {{ $t("of") }} {{ pagination.total }}
        {{ $t("entries") }}

        <span v-if="selectedRows.length">
          &nbsp; &nbsp; {{ selectedRows.length }} {{ $t("rows selected") }}
        </span>
      </p>
      <base-pagination
        style="float: right"
        class="pagination-no-border mt-3 pr-1 mt-1"
        :current="pagination.currentPage"
        :per-page="pagination.perPage"
        :total="pagination.total"
        @change="paginationChanged($event)"
      />
    </div>
  </div>
</template>

<script>
import { Table, TableColumn, Select, Option } from "element-ui"
import BasePagination from "./BasePagination.vue"
import request from "@/utils/request"

export default {
  name: "LightOwlTable",
  components: {
    [Table.name]: Table,
    [Select.name]: Select,
    [Option.name]: Option,
    "base-pagination": BasePagination,
    [TableColumn.name]: TableColumn
  },

  props: {
    defaultSort: {
      type: Object,
      required: true
    },
    uri: {
      type: String,
      required: true
    },
    perPage: {
      type: Number,
      default: 10
    },
    customParams: {
      type: Object,
      default: () => ({})
    },
    search: {
      type: String,
      default: ""
    },

    rowKey: {
      type: String,
      default: "_id"
    }
  },

  data: (vm) => ({
    expandRowKeys: [],
    selectedRows: [],
    loading: false,
    sort: {},
    pagination: {
      perPage: vm.perPage,
      from: 0,
      to: 10,
      page: 1,
      total: 0,
      perPageOptions: [
        { label: 10, value: 10 },
        { label: 20, value: 20 },
        { label: 30, value: 30 },
        { label: 50, value: 50 },
        { label: 100, value: 100 }
      ]
    },
    tableData: []
  }),

  watch: {
    "pagination.perPage"() {
      this.pagination.page = 1
      this.getData()
    },

    customParams() {
      this.getData()
    }
  },

  beforeMount() {
    this.sort = this.defaultSort
  },

  mounted() {
    this.getData()
  },

  methods: {
    triggerLoading() {
      this.loading = !this.loading
    },

    getData() {
      this.tableData = []
      let params = {
        sort: `${this.sort.prop}|${this.sort.order}`,
        page: this.pagination.page,
        per_page: this.pagination.perPage,
        search: this.search
      }

      params = Object.assign({}, params, this.customParams)

      this.loading = true

      request.get(this.uri, { params: params }).then((response) => {
        this.loading = false
        this.tableData = response.data.data
        this.pagination.from = response.data.from
        this.pagination.page = response.data.current_page
        this.pagination.total = response.data.total
        this.pagination.to = response.data.to
      })
    },
    paginationChanged(page) {
      this.pagination.page = page
      this.getData()
    },

    rowClick(row, column) {
      this.$emit("rowClicked", row, column)
    },

    handleSelectionChange(rows) {
      this.$emit("selectionChange", rows)
    },

    sortChange(sort) {
      this.sort = {
        prop: sort.prop,
        order: sort.order
      }
      this.getData()
    },

    toggleRowExpansion(row) {
      this.$refs.lightOwlTable.toggleRowExpansion(row)
    }
  }
}
</script>

<style>
.el-table th {
  padding: 0 !important;
}

.el-table tbody td {
  padding: 5px 0 !important;
}

.el-table .el-button {
  padding: 5px 10px !important;
  font-size: 12px;
}
.card-category {
  margin-bottom: 0px !important;
  line-height: 52px;
}

.pagination {
  margin-bottom: 0px !important;
  margin-top: 10px;
}

.pagination-info {
  font-size: 13px;
  line-height: 35px;
}

.pagination-no-border {
  margin-top: 5px !important;
}
</style>
