<template>
  <div class="pin-create-modal">
    <div class="modal-card">
      <!-- Header with title and private checkbox -->
      <header class="modal-card-head">
        <p class="modal-card-title">{{ $t(editorMeta.title) }}</p>
        <b-checkbox v-model="pinModel.form.private.value">
          {{ $t("isPrivateCheckbox") }}
        </b-checkbox>
      </header>

      <section class="modal-card-body">
        <!-- Upload Zone -->
        <FileUpload
          :previewImageURL="pinModel.form.url.value"
          v-on:imageUploadSucceed="onUploadDone"
          v-on:imageUploadProcessing="onUploadProcessing"
        ></FileUpload>

        <!-- Form Fields -->
        <div class="form-fields">
          <b-field :label="$t('imageUrlLabel')"
                   v-show="!disableUrlField && !isEdit"
                   :type="pinModel.form.url.type"
                   :message="pinModel.form.url.error"
                   horizontal>
            <b-input
              type="text"
              v-model="pinModel.form.url.value"
              :placeholder="$t('pinCreateModalImageURLPlaceholder')"
              maxlength="2048"
            ></b-input>
          </b-field>

          <b-field :label="$t('imageSourceLabel')"
                   :type="pinModel.form.referer.type"
                   :message="pinModel.form.referer.error"
                   horizontal>
            <b-input
              type="text"
              v-model="pinModel.form.referer.value"
              :placeholder="$t('pinCreateModalImageSourcePlaceholder')"
              maxlength="2048"
            ></b-input>
          </b-field>

          <b-field :label="$t('tagsLabel')" horizontal>
            <b-taginput
                v-model="pinModel.form.tags.value"
                :data="editorMeta.filteredTagOptions"
                autocomplete
                ellipsis
                icon="label"
                :allow-new="true"
                :placeholder="$t('pinCreateModalImageTagsPlaceholder')"
                @typing="getFilteredTags">
              <template slot-scope="props">
                <strong>{{ props.option }}</strong>
              </template>
              <template slot="empty">
                {{ $t("pinCreateModalEmptySlot") }}
              </template>
            </b-taginput>
          </b-field>

          <b-field :label="$t('descriptionLabel')"
                   :type="pinModel.form.description.type"
                   :message="pinModel.form.description.error"
                   horizontal>
            <b-input
              type="text"
              v-model="pinModel.form.description.value"
              :placeholder="$t('pinCreateModalImageDescriptionPlaceholder')"
              maxlength="1024"
            ></b-input>
          </b-field>

          <b-field :label="$t('selectBoardLabel')" v-if="!isEdit" horizontal>
            <b-taginput
                v-model="selectedBoardNames"
                :data="filteredBoardNames"
                autocomplete
                ellipsis
                :allow-new="true"
                :placeholder="$t('filterSelectSelectBoardPlaceholder')"
                @typing="getFilteredBoards">
              <template slot-scope="props">
                <span>{{ props.option }}</span>
              </template>
              <template slot="empty">
                {{ $t("pinCreateModalEmptySlot") }}
              </template>
            </b-taginput>
          </b-field>
        </div>
      </section>

      <footer class="modal-card-foot">
        <button
          v-if="!isEdit"
          @click="createPin"
          class="button is-primary">{{ $t("pinCreateModalCreatePinButton") }}
        </button>
        <button
          v-if="isEdit"
          @click="savePin"
          class="button is-primary">{{ $t("pinCreateModalSaveChangesButton") }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script>
import API from '../api';
import FileUpload from './FileUpload.vue';
import bus from '../utils/bus';
import ModelForm from '../utils/ModelForm';
import Loading from '../utils/Loading';
import AutoComplete from '../utils/AutoComplete';
import niceLinks from '../utils/niceLinks';


function isURLBlank(url) {
  return url !== null && url === '';
}

const fields = ['url', 'referer', 'description', 'tags', 'private'];

export default {
  name: 'PinCreateModal',
  props: {
    fromUrl: {
      type: Object,
      default: null,
    },
    username: {
      type: String,
      default: null,
    },
    isEdit: {
      type: Boolean,
      default: false,
    },
    existedPin: {
      type: Object,
      default: null,
    },
  },
  components: {
    FileUpload,
  },
  data() {
    const pinModel = ModelForm.fromFields(fields);
    pinModel.form.tags.value = [];
    return {
      disableUrlField: false,
      pinModel,
      formUpload: {
        imageId: null,
      },
      boardOptions: [],
      tagOptions: [],
      selectedBoardNames: [],
      filteredBoardNames: [],
      editorMeta: {
        title: 'NewPinTitle',
        filteredTagOptions: [],
      },
    };
  },
  computed: {
    boardIds() {
      const ids = [];
      this.selectedBoardNames.forEach((name) => {
        const board = this.boardOptions.find(b => b.name === name);
        if (board) {
          ids.push(board.value);
        }
      });
      return ids;
    },
  },
  created() {
    this.fetchBoardList();
    this.fetchTagList();
    if (this.isEdit) {
      this.editorMeta.title = 'EditPinTitle';
      this.pinModel.form.url.value = this.existedPin.url;
      this.pinModel.form.referer.value = this.existedPin.referer;
      this.pinModel.form.description.value = this.existedPin.description;
      this.pinModel.form.tags.value = this.existedPin.tags;
      this.pinModel.form.private.value = this.existedPin.private;
    } else {
      this.pinModel.form.private.value = false;
    }
    if (this.fromUrl) {
      this.pinModel.form.url.value = this.fromUrl.url;
      this.pinModel.form.referer.value = this.fromUrl.referer;
      this.pinModel.form.description.value = this.fromUrl.description;
    }
  },
  methods: {
    fetchTagList() {
      API.Tag.fetchList().then(
        (resp) => {
          this.tagOptions = resp.data;
        },
      );
    },
    getFilteredTags(text) {
      const filteredTagOptions = [];
      AutoComplete.getFilteredOptions(
        this.tagOptions,
        text,
      ).forEach(
        (option) => {
          filteredTagOptions.push(option.name);
        },
      );
      this.editorMeta.filteredTagOptions = filteredTagOptions;
    },
    getFilteredBoards(text) {
      this.filteredBoardNames = this.boardOptions
        .filter(b => b.name.toLowerCase().includes(text.toLowerCase()))
        .map(b => b.name);
    },
    fetchBoardList() {
      API.Board.fetchFullList(this.username).then(
        (resp) => {
          const boardOptions = [];
          resp.data.forEach(
            (board) => {
              const boardOption = { name: board.name, value: board.id };
              boardOptions.push(boardOption);
            },
          );
          this.boardOptions = boardOptions;
          this.filteredBoardNames = boardOptions.map(b => b.name);
        },
        () => {
          console.log('Error occurs while fetch board full list');
        },
      );
    },
    onUploadProcessing() {
      this.disableUrlField = true;
    },
    onUploadDone(imageId) {
      this.formUpload.imageId = imageId;
    },
    savePin() {
      const self = this;
      const data = this.pinModel.asDataByFields(
        ['referer', 'description', 'tags', 'private'],
      );
      const promise = API.Pin.updateById(this.existedPin.id, data);
      promise.then(
        (resp) => {
          bus.bus.$emit(bus.events.refreshPin);
          self.$emit('pinUpdated', resp);
          self.$parent.close();
        },
      );
    },
    createPin() {
      const loading = Loading.open(this);
      const self = this;
      let promise;
      if (isURLBlank(this.pinModel.form.url.value) && this.formUpload.imageId === null) {
        return;
      }
      if (this.formUpload.imageId === null) {
        const data = this.pinModel.asDataByFields(fields);
        promise = API.Pin.createFromURL(data);
      } else {
        const data = this.pinModel.asDataByFields(
          ['referer', 'description', 'tags', 'private'],
        );
        data.image_by_id = this.formUpload.imageId;
        promise = API.Pin.createFromUploaded(data);
      }
      promise.then(
        (resp) => {
          const promises = [];
          function done() {
            self.$emit('pinCreated', resp);
            self.$parent.close();
            loading.close();
          }
          bus.bus.$emit(bus.events.refreshPin);
          if (self.boardIds && self.boardIds.length > 0) {
            self.boardIds.forEach(
              (boardId) => {
                promises.push(API.Board.addToBoard(boardId, [resp.data.id]));
              },
            );
          }
          if (promises.length > 0) {
            Promise.all(promises).then(done);
          } else {
            done();
          }
        },
      ).catch((error) => {
        console.log('Cannot create pin:', error);
        loading.close();
      });
    },
    niceLinks,
  },
};
</script>

<style lang="scss" scoped>
.pin-create-modal {
  .modal-card {
    width: 560px;
    max-width: 95vw;
  }

  .modal-card-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: none;
    padding: 60px 30px 20px;
    background-color: #2d2d2d !important;
  }

  .modal-card-body {
    padding: 0 30px 30px;
  }

  // Full width file upload with 10px margin from modal edges
  ::v-deep .image-upload {
    margin: 0 -8px;
    padding: 0 12px;

    .upload {
      position: static;
      display: block;
    }
  }

  .form-fields {
    margin-top: 1.5rem;
    padding: 0 50px;
  }

  // Wider label column
  ::v-deep .field.is-horizontal .field-label {
    flex-basis: 120px;
    flex-grow: 0;
    flex-shrink: 0;
    text-align: right;
    margin-right: 1rem;
  }

  // Rounded form inputs with lighter border
  ::v-deep .input,
  ::v-deep .taginput .taginput-container {
    border-radius: 9999px;
    border-color: #555 !important;

    &::placeholder {
      color: #777 !important;
    }
  }

  ::v-deep .taginput .taginput-container input::placeholder {
    color: #777 !important;
  }

  // Hot pink rounded button
  .modal-card-foot .button.is-primary {
    background-color: #ff42ff !important;
    border-color: #ff42ff !important;
    border-radius: 9999px;
    padding-left: 2em;
    padding-right: 2em;
  }

  .modal-card-foot {
    justify-content: flex-end;
    border-top: none;
    padding: 0 30px 30px;
    background-color: #2d2d2d !important;
  }
}
</style>
