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
          vm.success(gettext('Followers have been loaded'));
          vm.followers = response.data.followers;
        }
      }

      function fail() {
        vm.error(gettext('Error loading followers'));
      }

      axios.post(urls.loadFollowers).then(success).catch(fail);
    },
    loadUsersIAmFollowing: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Users you are following have updated'));
        }
        vm.followers = response.data.followers;
      }

      function fail() {
        vm.error(gettext('Error updating users you are following'));
      }

      axios.post(urls.loadUsersIAmFollowing).then(success).catch(fail);
    },
    setApprovedStatus: function(follower) {
      function success() {
        follower.approved = status;
      }

      function fail() {
        vm.error(gettext('Error setting approved status'));
        element.prop('checked', !status);
      }

      const id = follower.id;
      const element = $('#follower-approved' + id);
      const status = element.prop('checked');
      const url = `${urls.followers}${id}/set-approved-status/`;
      axios.put(url, $.param({
        status: status,
      })).then(success).catch(fail);
    },
    setFollowedStatus: function(follower) {
      function success() {
        follower.followed = status;
      }

      function fail() {
        vm.error(gettext('Error'));
        element.prop('checked', !status);
      }

      const id = follower.id;
      const element = $('#follower-followed' + id);
      const status = element.prop('checked');
      const url = `${urls.followers}${id}/set-followed-status/`;
      axios.put(url, $.param({
        status: status,
      })).then(success).catch(fail);
    },
    block: function(follower) {
      function success() {
        vm.followers = vm.followers.filter((m) => m.id != id);
      }

      function fail() {
        vm.error(gettext('Error blocking follower'));
      }

      const id = follower.id;
      const url = `${urls.followers}${id}/block/`;
      axios.delete(url).then(success).catch(fail);
    },
  },
});
