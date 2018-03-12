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
  },
});
