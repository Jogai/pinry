<template>
  <div class="pins-for-tag">
    <PHeader></PHeader>
    <SearchPanel v-on:selected="doSearch"></SearchPanel>
    <Pins v-if="pinFilters" :pin-filters="pinFilters"></Pins>
    <Boards v-if="boardFilters" :filters="boardFilters"></Boards>
  </div>
</template>

<script>
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';
import Boards from '../components/Boards.vue';
import SearchPanel from '../components/search/SearchPanel.vue';

export default {
  name: 'Search',
  data() {
    return {
      pinFilters: {},
      boardFilters: null,
    };
  },
  components: {
    PHeader,
    Pins,
    Boards,
    SearchPanel,
  },
  watch: {
    $route(to) {
      this.applyQueryParams(to.query);
    },
  },
  created() {
    this.applyQueryParams(this.$route.query);
  },
  methods: {
    applyQueryParams(query) {
      if (query.tags) {
        this.pinFilters = { tagFilter: query.tags };
        this.boardFilters = null;
      }
    },
    doSearch(args) {
      this.pinFilters = null;
      this.boardFilters = null;
      if (args.filterType === 'Tag') {
        this.pinFilters = { tagFilter: args.selected };
      } else if (args.filterType === 'Board') {
        this.boardFilters = { boardNameContains: args.selected };
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
