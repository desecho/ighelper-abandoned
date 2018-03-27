'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    medias: vars.medias,
    showIssuesColumns: true,
    showOnlyIssues: false,
  },
  methods: {
    load: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Medias have been loaded'));
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.error(gettext('Error loading medias'));
      }

      axios.post(urls.loadMedias).then(success).catch(fail);
    },
    removeMedia: function(id) {
      vm.medias = vm.medias.filter((m) => m.id != id);
    },
    updateMedias: function(media) {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Medias have been updated'));
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.error(gettext('Error updating medias'));
      }

      axios.post(urls.updateMedias).then(success).catch(fail);
    },
    updateMedia: function(media) {
      function success(response) {
        if (response.data.status === 'success') {
          const updatedMedia = response.data.media;
          media.noLocation = updatedMedia.noLocation;
          media.noCaption = updatedMedia.noCaption;
          media.noTags = updatedMedia.noTags;
          media.likes = updatedMedia.likes;
          media.views = updatedMedia.views;
          media.caption = updatedMedia.caption;
          media.image = updatedMedia.image;
          media.imageSmall = updatedMedia.imageSmall;
          media.location = updatedMedia.location;
        } else {
          vm.removeMedia(media.id);
          vm.showRemovedMediaMessage();
        }
      }

      function fail() {
        vm.error(gettext('Error updating media'));
      }

      const url = `${urls.medias}${media.id}/`;
      axios.put(url).then(success).catch(fail);
    },
    del: function(media) {
      function success(response) {
        vm.removeMedia(media.id);
      }

      function fail() {
        vm.error(gettext('Error deleting media'));
      }

      const url = `${urls.medias}${media.id}/`;
      axios.delete(url).then(success).catch(fail);
    },
    hasIssue: function(media) {
      return media.noCaption || media.noTags || media.noLocation;
    },
    showRemovedMediaMessage: function() {
      vm.info(gettext('Media has been removed because it no longer exists on Instagram'));
    },
    loadViews: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Views have been loaded'));
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.error(gettext('Error loading views'));
      }

      axios.post(urls.loadViews).then(success).catch(fail);
    },
    editCaption: function(media) {
      function success(response) {
        if (response.data.status === 'success') {
          media.caption = caption;
        } else {
          vm.removeMedia(media.id);
          vm.showRemovedMediaMessage();
        }
      }

      function fail() {
        vm.error(gettext('Error editing caption'));
      }

      let caption = prompt(gettext('Caption'), media.caption);
      if (caption != null) {
        caption = $.trim(caption);
        if (caption == media.caption) {
          return;
        }
        const url = `${urls.medias}${media.id}/caption/`;
        axios.put(url, $.param({
          caption: caption,
        })).then(success).catch(fail);
      }
    },
  },
});
