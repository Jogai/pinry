<template>
  <div class="pins">
    <section class="section">
      <div id="pins-container" class="container" v-if="blocks">
        <div
          v-masonry=""
          transition-duration="0.3s"
          item-selector=".grid-item"
          column-width=".grid-sizer"
          gutter=".gutter-sizer"
        >
          <template v-for="item in blocks">
            <div v-bind:key="item.id"
                 v-masonry-tile
                 :class="item.class"
                 class="grid pin-masonry">
              <div class="grid-sizer"></div>
              <div class="gutter-sizer"></div>
              <div class="pin-card grid-item">
                <div @mouseenter="showEditButtons(item.id)"
                     @mouseleave="hideEditButtons(item.id)"
                >
                  <transition name="fade">
                    <EditorUI
                      v-if="shouldShowEdit(item.id)"
                      :pin="item"
                      :currentUsername="editorMeta.user.meta.username"
                      :currentBoard="editorMeta.currentBoard"
                      v-on:pin-delete-succeed="reset"
                      v-on:pin-remove-from-board-succeed="reset"
                    ></EditorUI>
                  </transition>
                  <img :src="item.url"
                     @load="onPinImageLoaded(item.id)"
                     @click="openPreview(item)"
                     :alt="item.description"
                     :style="item.style"
                     class="pin-preview-image">
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
      <loadingSpinner v-bind:show="status.loading"></loadingSpinner>
    </section>
  </div>
</template>

<script>
import API from './api';
import pinHandler from './utils/PinHandler';
import PinPreview from './PinPreview.vue';
import loadingSpinner from './loadingSpinner.vue';
import scroll from './utils/scroll';
import bus from './utils/bus';
import EditorUI from './editors/PinEditorUI.vue';
import niceLinks from './utils/niceLinks';

function createImageItem(pin) {
  const image = {};
  image.url = pinHandler.escapeUrl(pin.image.thumbnail.image);
  image.id = pin.id;
  image.owner_id = pin.submitter.id;
  image.private = pin.private;
  image.description = pin.description;
  image.tags = pin.tags;
  image.author = pin.submitter.username;
  image.avatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMmQyZDJkIi8+CjxwYXRoIGQ9Ik0yNCAyNEMyNy4zMTM3IDI0IDMwIDIxLjMxMzcgMzAgMThDMzAgMTQuNjg2MyAyNy4zMTM3IDEyIDI0IDEyQzIwLjY4NjMgMTIgMTggMTQuNjg2MyAxOCAxOEMxOCAyMS4zMTM3IDIwLjY4NjMgMjQgMjQgMjRaIiBmaWxsPSIjNjY2NjY2Ii8+CjxwYXRoIGQ9Ik0yNCAyNkMyMC42ODYzIDI2IDE3LjI2MzcgMjcuMjEwNSAxNC42OTMgMjkuMDkzOEMxMi4xMjIzIDMwLjk3NyAxMC41IDMzLjQyOTMgMTAuNSAzNlY0MEgzNy41VjM2QzM3LjUgMzMuNDI5MyAzNS44Nzc3IDMwLjk3NyAzMy4zMDcgMjkuMDkzOEMzMC43MzYzIDI3LjIxMDUgMjcuMzEzNyAyNiAyNCAyNloiIGZpbGw9IiM2NjY2NjYiLz4KPC9zdmc+';
  image.large_image_url = pinHandler.escapeUrl(pin.image.image);
  image.original_image_url = pin.url;
  image.referer = pin.referer;
  image.orgianl_width = pin.image.width;
  image.style = {
    width: `${pin.image.thumbnail.width}px`,
    height: `${pin.image.thumbnail.height}px`,
  };
  image.class = {};
  return image;
}

function initialData() {
  return {
    blocks: [],
    blocksMap: {},
    status: {
      loading: false,
      hasNext: true,
      offset: 0,
    },
    editorMeta: {
      currentEditId: null,
      currentBoard: {},
      user: {
        loggedIn: false,
        meta: {},
      },
    },
  };
}

export default {
  name: 'pins',
  components: {
    loadingSpinner,
    EditorUI,
  },
  data() {
    return initialData();
  },
  props: {
    pinFilters: {
      type: Object,
      default() {
        return {
          tagFilter: null,
          userFilter: null,
          boardFilter: null,
        };
      },
    },
  },
  watch: {
    pinFilters() {
      this.reset();
    },
  },
  methods: {
    shouldShowEdit(id) {
      if (!this.editorMeta.user.loggedIn) {
        return false;
      }
      return this.editorMeta.currentEditId === id;
    },
    showEditButtons(id) {
      this.editorMeta.currentEditId = id;
    },
    hideEditButtons() {
      this.editorMeta.currentEditId = null;
    },
    onPinImageLoaded(itemId) {
      this.blocksMap[itemId].class = {
        'image-loaded': true,
      };
      this.blocksMap[itemId].style.height = 'auto';
    },
    registerScrollEvent() {
      const self = this;
      scroll.bindScroll2Bottom(
        () => {
          if (self.status.loading || !self.status.hasNext) {
            return;
          }
          self.fetchMore();
        },
      );
    },
    buildBlocks(results) {
      const blocks = [];
      results.forEach(
        (pin) => {
          const item = createImageItem(pin);
          blocks.push(
            item,
          );
        },
      );
      return blocks;
    },
    openPreview(pinItem) {
      const currentIndex = this.blocks.findIndex(pin => pin.id === pinItem.id);
      let previewComponent = null;

      const modal = this.$buefy.modal.open(
        {
          parent: this,
          component: PinPreview,
          props: {
            pinItem,
            allPins: this.blocks,
            currentIndex,
          },
          scroll: 'keep',
          customClass: 'pin-preview-at-home',
          events: {
            'navigate-pin': (newIndex) => {
              if (newIndex >= 0 && newIndex < this.blocks.length) {
                // Find component instance if not already found
                if (!previewComponent) {
                  // Try to find the PinPreview component in modal's children
                  if (modal && modal.$children && modal.$children.length > 0) {
                    previewComponent = modal.$children.find(child => child.$options.name === 'PinPreview');
                  }
                }

                // Update props
                if (previewComponent) {
                  // Use Vue.set to ensure reactivity
                  this.$set(previewComponent, 'pinItem', this.blocks[newIndex]);
                  this.$set(previewComponent, 'currentIndex', newIndex);
                } else if (modal && modal.propsData) {
                  // Fallback to propsData
                  this.$set(modal.propsData, 'pinItem', this.blocks[newIndex]);
                  this.$set(modal.propsData, 'currentIndex', newIndex);
                }
              }
            },
          },
        },
      );

      // Try to get component reference after modal mounts
      this.$nextTick(() => {
        if (modal && modal.$children && modal.$children.length > 0) {
          previewComponent = modal.$children.find(child => child.$options.name === 'PinPreview');
        }
      });
    },
    shouldFetchMore(created) {
      if (!created) {
        if (this.status.loading) {
          return false;
        }
        if (!this.status.hasNext) {
          return false;
        }
      }
      return true;
    },
    initialize() {
      this.initializeMeta();
      this.fetchMore(true);
    },
    initializeMeta() {
      const self = this;
      API.User.fetchUserInfo().then(
        (user) => {
          if (user === null) {
            self.editorMeta.user.loggedIn = false;
            self.editorMeta.user.meta = {};
          } else {
            self.editorMeta.user.meta = user;
            self.editorMeta.user.loggedIn = true;
          }
        },
      );
    },
    reset() {
      const data = initialData();
      Object.entries(data).forEach(
        (kv) => {
          const [key, value] = kv;
          this[key] = value;
        },
      );
      this.initialize();
    },
    fetchMore(created) {
      if (!this.shouldFetchMore(created)) {
        return;
      }
      this.status.loading = true;
      let promise;
      if (this.pinFilters.tagFilter) {
        promise = API.fetchPins(this.status.offset, this.pinFilters.tagFilter, null, null);
      } else if (this.pinFilters.userFilter) {
        promise = API.fetchPins(this.status.offset, null, this.pinFilters.userFilter, null);
      } else if (this.pinFilters.boardFilter) {
        const prevPromise = API.Board.get(this.pinFilters.boardFilter);
        promise = prevPromise.then(
          (resp) => {
            this.editorMeta.currentBoard = resp.data;
            return API.fetchPins(this.status.offset, null, null, this.pinFilters.boardFilter);
          },
        );
      } else if (this.pinFilters.idFilter) {
        promise = API.fetchPin(this.pinFilters.idFilter);
      } else {
        promise = API.fetchPins(this.status.offset);
      }
      promise.then(
        (resp) => {
          const { results, next } = resp.data;
          let newBlocks = this.buildBlocks(results);
          newBlocks.forEach(
            (item) => { this.blocksMap[item.id] = item; },
          );
          newBlocks = this.blocks.concat(newBlocks);
          this.blocks = newBlocks;
          this.status.offset = newBlocks.length;
          this.status.hasNext = !(next === null);
          this.status.loading = false;
        },
        () => { this.status.loading = false; },
      );
    },
    niceLinks,
  },
  created() {
    bus.bus.$on(bus.events.refreshPin, this.reset);
    this.registerScrollEvent();
    this.initialize();
  },
};
</script>

<style lang="scss" scoped>
/* grid */
@import 'utils/pin';

.grid-sizer,
.grid-item { width: $pin-preview-width; }
.grid-item {
  margin-bottom: 15px;
}
.gutter-sizer {
  width: 15px;
}

/* pin-image transition */
.pin-masonry.image-loaded{
  opacity: 1;
  transition: opacity .3s;
}
.pin-masonry {
  opacity: 0;
}

/* card */
$pin-footer-position-fix: -6px;
$avatar-width: 30px;
$avatar-height: 30px;
@import './utils/fonts';
@import './utils/loader.scss';

.pin-card {
  border-radius: 8px;
  overflow: hidden;

  .pin-preview-image {
    cursor: zoom-in;
    border-radius: 8px;
  }
  > img {
    min-width: $pin-preview-width;
    background-color: #2d2d2d;
    border-radius: 8px;
    @include loader('../assets/loader.gif');
  }
}

@import 'utils/grid-layout';
@include screen-grid-layout("#pins-container");

/* Fade transition for editor buttons */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

</style>
