'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    users: vars.users,
  },
  methods: {
    loadLikes: function(onlyForNewMedias = false) {
      function success(response) {
        if (response.data.status === 'success') {
          vm.success(gettext('Likes have been loaded'));
          vm.users = response.data.users;
        }
      }

      function fail() {
        vm.error(gettext('Error loading likes'));
      }

      axios.post(urls.loadLikes, $.param({
        'onlyForNewMedias': JSON.stringify(onlyForNewMedias),
      })).then(success).catch(fail);
    },
  },
});
