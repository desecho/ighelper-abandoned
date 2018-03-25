'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    followed: vars.followed,
  },
  methods: {
    loadFollowed: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Users you are following have been loaded'));
        }
        vm.followed = response.data.followed;
      }

      function fail() {
        vm.error(gettext('Error loading users you are following'));
      }

      axios.post(urls.loadFollowed).then(success).catch(fail);
    },
    unfollow: function(user) {
      function success() {
        vm.followed = vm.followed.filter((u) => u.id != id);
      }

      function fail() {
        vm.error(gettext('Error unfollowing user'));
      }

      const id = user.id;
      const url = `${urls.followed}${id}/unfollow/`;
      axios.post(url).then(success).catch(fail);
    },
    setConfirmedStatus: function(user) {
      function success() {
        user.confirmed = status;
      }

      function fail() {
        vm.error(gettext('Error'));
        element.prop('checked', !status);
      }

      const id = user.id;
      const element = $('#user-confirmed' + id);
      const status = element.prop('checked');
      const url = `${urls.followed}${id}/set-confirmed-status/`;
      axios.put(url, $.param({
        status: status,
      })).then(success).catch(fail);
    },
  },
});
