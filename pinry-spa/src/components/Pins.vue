<template>
  <div class="pins">
    <!-- Layout toggle button -->
    <div
      class="layout-toggle-placeholder"
      @mouseenter="showToggleOnHover"
      @mouseleave="hideToggleOnHover"
    >
      <transition name="fade">
        <div v-if="!toggleHidden" class="layout-toggle-control">
          <button
            class="layout-toggle-btn"
            :class="{ active: layoutMode === 'masonry' }"
            @click="setLayoutMode('masonry')"
            title="Masonry view"
          >
            <img src="/img/icons/mortar-icon.png" alt="Masonry" class="toggle-icon toggle-icon-img" />
          </button>
          <button
            class="layout-toggle-btn"
            :class="{ active: layoutMode === 'single' }"
            @click="setLayoutMode('single')"
            title="FFFFound view"
          >
            <svg class="toggle-icon toggle-icon-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <rect x="5" y="1" width="14" height="5" rx="1" />
              <rect x="5" y="8" width="14" height="8" rx="1" />
              <rect x="5" y="18" width="14" height="5" rx="1" />
            </svg>
          </button>
        </div>
      </transition>
    </div>

    <div
      class="inline-search-placeholder"
      @mouseenter="showToggleOnHover"
      @mouseleave="hideToggleOnHover"
    >
      <transition name="fade">
        <div v-if="!toggleHidden" class="inline-search-control">
          <i class="mdi mdi-magnify inline-search-icon" aria-hidden="true"></i>
          <input
            class="inline-search-input"
            :class="{ 'has-filter': inlineTagFilter }"
            v-model="inlineSearchQuery"
            placeholder=""
            @focus="onSearchFocus"
            @blur="onSearchBlur"
            @input="onSearchInput"
            @keyup.enter="selectInlineTag(filteredTags[0])"
            @keyup.escape="clearInlineTag"
          />
          <button
            v-if="inlineTagFilter"
            class="inline-search-clear"
            @mousedown.prevent="clearInlineTag"
          >×</button>
          <div
            v-if="inlineSearchFocused && filteredTags.length"
            class="inline-search-dropdown"
            ref="inlineSearchDropdown"
            @scroll="onInlineSearchDropdownScroll"
          >
            <div
              v-for="tag in filteredTags"
              :key="tag"
              class="inline-search-option"
              @mousedown.prevent="selectInlineTag(tag)"
            >{{ tag }}</div>
          </div>
        </div>
      </transition>
    </div>

    <section class="section">
      <!-- Masonry layout -->
      <div id="pins-container" class="container" v-if="blocks && layoutMode === 'masonry'">
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

      <!-- Single-column FFFFound layout -->
      <div class="single-column-container" v-if="blocks && layoutMode === 'single'">
        <div
          v-for="item in blocks"
          :key="item.id"
          class="single-column-item"
          :class="{ 'image-loaded': item.singleLoaded }"
        >
          <div
            @mouseenter="showEditButtons(item.id)"
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
            <img
              :src="item.large_image_url"
              @load="onSingleImageLoaded(item.id)"
              @click="openPreview(item)"
              :alt="item.description"
              class="single-column-image"
            />
          </div>
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

const TOGGLE_HIDE_DELAY_MS = 3000;
const SEARCH_ACTIVITY_HIDE_DELAY_MS = 15000;
const TAG_DROPDOWN_BATCH_SIZE = 50;

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
    layoutMode: localStorage.getItem('pinry-layout-mode') || 'masonry',
    toggleHidden: true,
    toggleFadeTimeout: null,
    togglePlaceholderHovered: false,
    inlineTagFilter: null,
    inlineSearchQuery: '',
    inlineSearchFocused: false,
    inlineSearchLastInteractionAt: 0,
    visibleTagCount: TAG_DROPDOWN_BATCH_SIZE,
    allTags: [],
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
  computed: {
    filteredTagMatches() {
      const q = this.inlineSearchQuery.toLowerCase();
      return q
        ? this.allTags.filter(t => t.toLowerCase().includes(q))
        : this.allTags;
    },
    filteredTags() {
      return this.filteredTagMatches.slice(0, this.visibleTagCount);
    },
  },
  watch: {
    pinFilters() {
      this.reset();
    },
    inlineSearchQuery() {
      this.resetVisibleTagCount();
      this.$nextTick(() => {
        if (this.$refs.inlineSearchDropdown) {
          this.$refs.inlineSearchDropdown.scrollTop = 0;
        }
      });
    },
  },
  methods: {
    resetVisibleTagCount() {
      this.visibleTagCount = TAG_DROPDOWN_BATCH_SIZE;
    },
    onInlineSearchDropdownScroll(event) {
      const { target } = event;
      if (!target) return;
      const nearBottom = target.scrollTop + target.clientHeight >= target.scrollHeight - 16;
      if (!nearBottom) return;
      if (this.visibleTagCount >= this.filteredTagMatches.length) return;
      this.visibleTagCount += TAG_DROPDOWN_BATCH_SIZE;
    },
    clearToggleFadeTimeout() {
      if (this.toggleFadeTimeout) {
        clearTimeout(this.toggleFadeTimeout);
        this.toggleFadeTimeout = null;
      }
    },
    scheduleToggleHide(delay = TOGGLE_HIDE_DELAY_MS) {
      this.clearToggleFadeTimeout();
      this.toggleFadeTimeout = setTimeout(() => {
        const recentlyUsedSearch = Date.now() - this.inlineSearchLastInteractionAt < SEARCH_ACTIVITY_HIDE_DELAY_MS;
        if (!this.togglePlaceholderHovered && !this.inlineSearchFocused && !recentlyUsedSearch) {
          this.toggleHidden = true;
          return;
        }
        this.scheduleToggleHide(delay);
      }, delay);
    },
    markInlineSearchInteraction() {
      this.inlineSearchLastInteractionAt = Date.now();
      this.toggleHidden = false;
      this.scheduleToggleHide(SEARCH_ACTIVITY_HIDE_DELAY_MS);
    },
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
    setLayoutMode(mode) {
      this.layoutMode = mode;
      localStorage.setItem('pinry-layout-mode', mode);
    },
    handleToggleScroll() {
      this.toggleHidden = false;
      this.scheduleToggleHide();
    },
    showToggleOnHover() {
      this.togglePlaceholderHovered = true;
      this.toggleHidden = false;
      this.clearToggleFadeTimeout();
    },
    hideToggleOnHover() {
      this.togglePlaceholderHovered = false;
      this.scheduleToggleHide();
    },
    onSingleImageLoaded(itemId) {
      if (this.blocksMap[itemId]) {
        this.$set(this.blocksMap[itemId], 'singleLoaded', true);
      }
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
            'open-pin': (pin) => {
              if (!previewComponent) {
                if (modal && modal.$children && modal.$children.length > 0) {
                  previewComponent = modal.$children.find(child => child.$options.name === 'PinPreview');
                }
              }
              if (previewComponent) {
                this.$set(previewComponent, 'pinItem', pin);
                this.$set(previewComponent, 'currentIndex', undefined);
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
      // Preserve inline search state across resets
      data.inlineTagFilter = this.inlineTagFilter;
      data.inlineSearchQuery = this.inlineSearchQuery;
      data.inlineSearchFocused = this.inlineSearchFocused;
      data.allTags = this.allTags;
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
      const effectiveTagFilter = this.inlineTagFilter || this.pinFilters.tagFilter;
      if (effectiveTagFilter) {
        promise = API.fetchPins(this.status.offset, effectiveTagFilter, null, null);
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
      } else if (this.pinFilters.similarToPin) {
        promise = API.Pin.fetchSimilar(this.pinFilters.similarToPin, 48);
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
    selectInlineTag(tag) {
      if (!tag) return;
      this.inlineTagFilter = tag;
      this.inlineSearchQuery = tag;
      this.inlineSearchFocused = false;
      this.reset();
      this.markInlineSearchInteraction();
    },
    clearInlineTag() {
      this.inlineTagFilter = null;
      this.inlineSearchQuery = '';
      this.inlineSearchFocused = false;
      this.reset();
      this.markInlineSearchInteraction();
    },
    onSearchFocus() {
      this.inlineSearchFocused = true;
      this.resetVisibleTagCount();
      this.markInlineSearchInteraction();
    },
    onSearchBlur() {
      this.inlineSearchFocused = false;
      this.markInlineSearchInteraction();
    },
    onSearchInput() {
      this.markInlineSearchInteraction();
    },
    niceLinks,
  },
  created() {
    bus.bus.$on(bus.events.refreshPin, this.reset);
    this.registerScrollEvent();
    this.initialize();
    API.Tag.fetchList().then((resp) => {
      this.allTags = resp.data.map(t => t.name).sort();
    });
    window.addEventListener('scroll', this.handleToggleScroll);
    // Show toggle briefly on load, then hide after 3s
    this.toggleHidden = false;
    this.scheduleToggleHide();
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleToggleScroll);
    this.clearToggleFadeTimeout();
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

/* Layout toggle button */
.layout-toggle-placeholder {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 76px;
  height: 32px;
  z-index: 20;
  cursor: pointer;
}

.layout-toggle-control {
  display: flex;
  background-color: #000002;
  border-radius: 999px;
  overflow: hidden;
}

.layout-toggle-btn {
  height: 32px;
  border: none;
  background: transparent;
  padding: 0 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;

  &.active {
    background-color: rgba(255, 66, 255, 0.15);
  }
}

.toggle-icon {
  width: 16px;
  height: 16px;
}

.toggle-icon-svg {
  fill: #ffffff;

  .active & {
    fill: #ff42ff;
  }
}

.toggle-icon-img {
  /* White by default */
  filter: brightness(0) invert(1);

  .active & {
    /* Hot pink #ff42ff */
    filter: brightness(0) saturate(100%) invert(42%) sepia(99%) saturate(3000%) hue-rotate(280deg) brightness(105%) contrast(105%);
  }
}

/* Single-column FFFFound layout */
.single-column-container {
  max-width: $pin-single-column-width;
  margin: 0 auto;
  padding: 0 15px;
}

.single-column-item {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  opacity: 0;
  transition: opacity 0.3s;
  position: relative;

  &.image-loaded {
    opacity: 1;
  }
}

.single-column-image {
  width: 100%;
  display: block;
  border-radius: 8px;
  cursor: zoom-in;
  background-color: #2d2d2d;
}

/* Inline tag search */
.inline-search-placeholder {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  height: 32px;
  width: min(500px, calc(100vw - 220px));
  z-index: 20;

  @media (max-width: 419px) { display: none; }
}

.inline-search-control {
  position: relative;
  display: flex;
  align-items: center;
  background-color: #000002;
  border-radius: 999px;
  height: 32px;
  padding: 0 14px;
}

.inline-search-icon {
  font-size: 18px;
  line-height: 1;
  color: #ff42ff;
  flex-shrink: 0;
  margin-right: 8px;
}

.inline-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 13px;
  font-family: 'Open Sans', sans-serif;
  height: 100%;
  min-width: 0;

  &::placeholder { color: #888; }
  &.has-filter { color: #ff42ff; }
}

.inline-search-clear {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 0 0 6px;
  &:hover { color: #ff42ff; }
}

.inline-search-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background-color: #000002;
  border-radius: 12px;
  overflow: hidden;
  max-height: 260px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
}

.inline-search-option {
  padding: 7px 14px;
  font-size: 13px;
  color: #e0e0e0;
  cursor: pointer;
  font-family: 'Open Sans', sans-serif;

  &:hover {
    background-color: rgba(255, 66, 255, 0.15);
    color: #ff42ff;
  }
}

</style>

<style lang="scss">
.pin-preview-at-home {
  .animation-content {
    display: flex;
    flex-direction: column;
    height: 90vh;
    max-height: 90vh;
    overflow: hidden;
  }
}
</style>
