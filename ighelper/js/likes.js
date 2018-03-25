'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    users: vars.users,
  },
  methods: {
    loadLikes: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Likes have been loaded'));
          vm.users = response.data.users;
        }
      }

      function fail() {
        vm.error(gettext('Error loading likes'));
      }

      axios.post(urls.loadLikes).then(success).catch(fail);
    },
  },
});
