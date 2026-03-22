<template>
  <div class="profile-container">
    <div class="profile-token-card">
      <header class="token-card-head">
        <p class="token-card-title">{{ $t("tokenUserProfileCardTitle") }}</p>
      </header>
      <div class="token-card-body">
        <p class="token-desc">{{ $t("tokenUserProfileCardContent") }}</p>
        <pre class="token-value">{{ token }}</pre>
        <p class="token-note">
          {{ $t("pleaseReadTokenUserProfileCardContent") }}
          <a target="_blank" href="https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication">
            {{ $t("drfApiDocumentationLink") }}
          </a>
          {{ $t("forMoreDetailsParagraph") }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'profile',
  props: ['token'],
  data() {
    return {};
  },
};
</script>

<style scoped lang="scss">
@font-face {
  font-family: 'Rubik';
  src: url('../../assets/Rubik/static/Rubik-Regular.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

.profile-container {
  margin-top: 1.5rem;
  margin-left: auto;
  margin-right: auto;
}

@import '../utils/grid-layout';
@include screen-grid-layout(".profile-container");

.profile-token-card {
  background-color: #2d2d2d;
  border-radius: 8px;
  overflow: hidden;
}

.token-card-head {
  padding: 1.5rem 1.75rem 1rem;
  border-bottom: 1px solid #404040;
}

.token-card-title {
  font-family: 'Rubik', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.token-card-body {
  padding: 1.25rem 1.75rem 1.75rem;
}

.token-desc {
  color: #e0e0e0;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.token-value {
  background-color: #1a1a1a;
  color: #ff42ff;
  border: 1px solid #404040;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  word-break: break-all;
  white-space: pre-wrap;
  margin-bottom: 1rem;
  font-family: monospace;
}

.token-note {
  color: #888888;
  font-size: 0.8rem;
  margin: 0;

  a {
    color: #4a9eff !important;
    &:hover { color: #6bb3ff !important; }
  }
}
</style>
