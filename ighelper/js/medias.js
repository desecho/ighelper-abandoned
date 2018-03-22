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
          vm.flash(gettext('Medias have been loaded'), 'success', vars.flashOptions);
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.flash(gettext('Error loading medias'), 'error', vars.flashOptions);
      }

      axios.post(urls.loadMedias).then(success).catch(fail);
    },
    removeMedia: function(id) {
      vm.medias = vm.medias.filter((m) => m.id != id);
    },
    update: function(media) {
      function success(response) {
        if (response.data.status === 'success') {
          const updatedMedia = response.data.media;
          media.noLocation = updatedMedia.noLocation;
          media.noCaption = updatedMedia.noCaption;
          media.noTags = updatedMedia.noTags;
          media.likes = updatedMedia.likes;
          media.views = updatedMedia.views;
          media.caption = updatedMedia.caption;
        } else {
          vm.removeMedia(media.id);
          vm.showRemovedMediaMessage();
        }
      }

      function fail() {
        vm.flash(gettext('Error updating media'), 'error', vars.flashOptions);
      }

      const url = `${urls.medias}${media.id}/`;
      axios.put(url).then(success).catch(fail);
    },
    del: function(media) {
      function success(response) {
        vm.removeMedia(media.id);
      }

      function fail() {
        vm.flash(gettext('Error deleting media'), 'error', vars.flashOptions);
      }

      const url = `${urls.medias}${media.id}/`;
      axios.delete(url).then(success).catch(fail);
    },
    hasIssue: function(media) {
      return media.noCaption || media.noTags || media.noLocation;
    },
    showRemovedMediaMessage: function() {
      vm.flash(gettext('Media has been removed because it no longer exists on Instagram'), 'info', vars.flashOptions);
    },
    loadLikes: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Likes have been loaded'), 'success', vars.flashOptions);
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.flash(gettext('Error loading likes'), 'error', vars.flashOptions);
      }

      axios.post(urls.loadLikes).then(success).catch(fail);
    },
    loadViews: function(){
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Views have been loaded'), 'success', vars.flashOptions);
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.flash(gettext('Error loading views'), 'error', vars.flashOptions);
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
        vm.flash(gettext('Error editing caption'), 'error', vars.flashOptions);
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
