'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    language: vars.language,
  },
  methods: {
    savePreferences: function() {
      axios.post(urls.savePreferences, $.param({
        language: vm.language,
      })).then(function() {
        location.reload();
      }).catch(function() {
        vm.error(gettext('Error saving settings'));
      });
    },
  },
});
