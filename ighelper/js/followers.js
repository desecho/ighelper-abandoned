'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    followers: vars.followers,
    hideApproved: false,
    hideFollowed: false,
  },
  methods: {
    isApproved: function(follower) {
      return follower.followed || follower.approved;
    },
    loadFollowers: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Followers have been loaded'), 'success', vars.flashOptions);
          vm.followers = response.data.followers;
        }
      }

      function fail() {
        vm.flash(gettext('Error loading followers'), 'error', vars.flashOptions);
      }

      axios.post(urls.loadFollowers).then(success).catch(fail);
    },
    updateUsersIAmFollowing: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Users you are following have updated'), 'success', vars.flashOptions);
        }
        vm.followers = response.data.followers;
      }

      function fail() {
        vm.flash(gettext('Error updating users you are following'), 'error', vars.flashOptions);
      }

      axios.post(urls.updateUsersIAmFollowing).then(success).catch(fail);
    },
    setApprovedStatus: function(follower) {
      function success() {
        follower.approved = true;
      }

      function fail() {
        vm.flash(gettext('Error setting approved status'), 'error', vars.flashOptions);
        element.prop('checked', !status);
      }

      const id = follower.id;
      const element = $('#follower' + id);
      const status = element.prop('checked');
      const url = `${urls.followers}${id}/set-approved-status/`;
      axios.put(url, $.param({
        status: status,
      })).then(success).catch(fail);
    },
  },
});
