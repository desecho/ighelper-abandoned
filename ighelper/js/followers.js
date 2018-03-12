'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    followers: vars.followers,
  },
  methods: {
    loadFollowers: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Followers have been loaded'), 'success', vars.flashOptions);
          location.reload();
        }
      }

      function fail() {
        vm.flash(gettext('Error loading followers'), 'error', vars.flashOptions);
      }

      const vm = this;
      axios.post(urls.urlLoadFollowers).then(success).catch(fail);
    },
    updateFollowers: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Followers have been updated'), 'success', vars.flashOptions);
          location.reload();
        }
      }

      function fail() {
        vm.flash(gettext('Error updating followers'), 'error', vars.flashOptions);
      }

      const vm = this;
      axios.post(urls.urlUpdateFollowers).then(success).catch(fail);
    },
    loadMedias: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Medias have been loaded'), 'success', vars.flashOptions);
        }
      }

      function fail() {
        vm.flash(gettext('Error loading medias'), 'error', vars.flashOptions);
      }

      const vm = this;
      axios.post(urls.urlLoadMedias).then(success).catch(fail);
    },
    loadLikes: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Likes have been loaded'), 'success', vars.flashOptions);
        }
      }

      function fail() {
        vm.flash(gettext('Error loading likes'), 'error', vars.flashOptions);
      }

      const vm = this;
      axios.post(urls.urlLoadLikes).then(success).catch(fail);
    },
  },
});
