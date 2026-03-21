<template>
  <div class="search-panel">
    <div class="floating-search-shell">
      <div class="floating-search-bar">
        <i class="mdi mdi-magnify search-icon" aria-hidden="true"></i>
        <b-select v-model="filterType" class="search-type-select">
          <option value="Tag">{{ $t("SearchPanelTagOption") }}</option>
          <option value="Board">{{ $t("SearchPanelBoardOption") }}</option>
        </b-select>
        <b-autocomplete
          v-if="filterType === 'Tag'"
          ref="tagAutocomplete"
          class="search-input"
          v-model="name"
          :data="filteredDataArray"
          :keep-first="true"
          :open-on-focus="true"
          placeholder=""
          @select="option => selected = option">
          <template slot="empty">{{ $t("noResultsFound") }}</template>
        </b-autocomplete>
        <template v-else>
          <b-input
            class="search-input"
            type="search"
            v-model="boardText"
            placeholder=""
            @keyup.enter.native="searchBoard"
          >
          </b-input>
          <button class="board-search-button" type="button" @click="searchBoard">
            {{ $t("searchButton") }}
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'FilterSelector',
  data() {
    return {
      filterType: 'Tag',
      selectedOption: [],
      options: {
        Tag: [],
      },
      name: '',
      boardText: '',
      selected: null,
    };
  },
  methods: {
    selectOption(filterName) {
      this.name = '';
      this.boardText = '';
      if (filterName === 'Tag') {
        this.selectedOption = this.options.Tag;
      }
    },
    searchBoard() {
      if (this.boardText === '') {
        return;
      }
      this.$emit(
        'selected',
        { filterType: this.filterType, selected: this.boardText },
      );
    },
  },
  watch: {
    filterType(newVal) {
      this.selectOption(newVal);
    },
    name(newVal) {
      if (newVal === '' && this.$refs.tagAutocomplete) {
        this.$refs.tagAutocomplete.isActive = true;
      }
    },
    selected(newVal) {
      this.$emit(
        'selected',
        { filterType: this.filterType, selected: newVal },
      );
    },
  },
  computed: {
    filteredDataArray() {
      return this.selectedOption.filter(
        (option) => {
          const ret = option
            .toString()
            .toLowerCase()
            .indexOf(this.name.toLowerCase()) >= 0;
          return ret;
        },
      );
    },
  },
  created() {
    api.Tag.fetchList().then(
      (resp) => {
        const options = [];
        resp.data.forEach(
          (tag) => {
            options.push(tag.name);
          },
        );
        this.options.Tag = options;
        if (this.filterType === 'Tag') {
          this.selectedOption = options;
        }
      },
    );
  },
};
</script>

<style scoped="scoped" lang="scss">
.search-panel {
  height: 56px;
}

.floating-search-shell {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: min(760px, calc(100vw - 230px));
  z-index: 24;
}

.floating-search-bar {
  display: flex;
  align-items: center;
  height: 34px;
  padding: 0 6px;
  border-radius: 999px;
  background-color: #000002;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-family: 'Open Sans', sans-serif;
}

.search-icon {
  margin-right: 4px;
  color: #ff42ff;
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.search-type-select {
  width: 72px;
  margin-right: 0;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.search-type-select ::v-deep .select {
  display: flex;
  align-items: center;
  height: 28px;
}

.search-type-select ::v-deep .select select {
  height: 28px !important;
  line-height: 28px !important;
}

.search-input {
  flex: 1;
  min-width: 0;
  font-family: 'Open Sans', sans-serif;
}

.board-search-button {
  margin-left: 4px;
  height: 24px;
  border: none;
  border-radius: 999px;
  padding: 0 10px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'Open Sans', sans-serif;
  cursor: pointer;
  color: #ff42ff;
  background: rgba(255, 66, 255, 0.12);
}

.board-search-button:hover {
  background: rgba(255, 66, 255, 0.2);
}

.search-panel ::v-deep .select select,
.search-panel ::v-deep .input {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #f0f0f0;
  font-family: 'Open Sans', sans-serif;
  height: 28px !important;
  line-height: 28px !important;
  min-height: 28px !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  padding-left: 4px !important;
  padding-right: 4px !important;
}

.search-panel ::v-deep .select select {
  font-size: 13px;
  color: #ff42ff;
  padding-right: 4px !important;
  padding-left: 4px !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  line-height: 28px !important;
}

.search-panel ::v-deep .control,
.search-panel ::v-deep .field {
  margin-bottom: 0 !important;
}

.search-panel ::v-deep .autocomplete {
  width: 100%;
}

.search-panel ::v-deep .select:not(.is-multiple):not(.is-loading)::after {
  display: none;
}

.search-panel ::v-deep .autocomplete .dropdown-menu {
  margin-top: 4px;
}

.search-panel ::v-deep .autocomplete .dropdown-content {
  background: #000002;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  max-height: 320px;
  font-family: 'Open Sans', sans-serif;
}

.search-panel ::v-deep .autocomplete .dropdown-item {
  color: #e6e6e6;
}

.search-panel ::v-deep .autocomplete .dropdown-item.is-hovered,
.search-panel ::v-deep .autocomplete .dropdown-item:hover {
  background: rgba(255, 66, 255, 0.15);
  color: #ff42ff;
}

@media (max-width: 960px) {
  .floating-search-shell {
    width: min(760px, calc(100vw - 110px));
  }
}

@media (max-width: 640px) {
  .search-panel {
    height: 52px;
  }

  .floating-search-shell {
    top: 16px;
    width: calc(100vw - 28px);
  }

  .floating-search-bar {
    height: 32px;
    padding: 0 4px;
  }

  .search-type-select {
    width: 92px;
  }

  .board-search-button {
    padding: 0 10px;
  }
}
</style>
