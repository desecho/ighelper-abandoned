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
      const vm = this;
      axios.post(urls.urlSavePreferences, $.param({
        language: vm.language,
      })).then(function() {
        location.reload();
      }).catch(function() {
        vm.flash(gettext('Error saving settings'), 'error', vars.flashOptions);
      });
    },
  },
});
