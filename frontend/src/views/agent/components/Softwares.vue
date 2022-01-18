<template>
  <div style="padding: 0 5px;">
    <el-table
      :data="agent.softwares.filter(data => !searchSoftware || data.name.toLowerCase().includes(searchSoftware.toLowerCase()))"
      style="width: 100%"
    >
      <el-table-column
        sortable
        prop="name"
        :label="$t('Name')"
      />
      <el-table-column
        sortable
        prop="version"
        :label="$t('Version')"
      />
      <el-table-column
        sortable
        prop="vendor"
        :label="$t('Vendor')"
      />
      <el-table-column>
        <template slot="header" slot-scope="scope">
          <el-input
            v-model="searchSoftware"
            size="mini"
            type="text"
            :placeholder="$t('Search')"
            prefix-icon="el-icon-search"
          />
        </template>
        <template />
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  props: {
    agent: {
      type: Object,
      required: true
    }
  },

  data: () => ({
    searchSoftware: ""
  })
}
</script>

