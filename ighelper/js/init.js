'use strict';

import Vue from 'vue';
import VueFlashMessage from 'vue-flash-message';
import VueCookie from 'vue-cookies';


window.vars = {};
window.urls = {};

Vue.options.delimiters = ['[[', ']]'];
Vue.use(VueFlashMessage, {
  createShortcuts: true,
  messageOptions: {
    timeout: 1500,
    important: true,
  },
});
Vue.use(VueCookie);

new Vue({
  el: '#menu',
  methods: {
    changeLanguage: function() {
      document.getElementById('language-form').submit();
    },
  },
});
