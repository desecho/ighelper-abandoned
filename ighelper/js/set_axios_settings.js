'use strict';

import {
  loadProgressBar,
} from 'axios-progress-bar';
import axios from 'axios';


function setAxiosSettings() {
  loadProgressBar();
  const headers = {
    'X-CSRFToken': vm.$cookies.get('csrftoken'),
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
  };
  axios.defaults.headers.common = headers;
}


if (window.vm) {
  setAxiosSettings();
}
