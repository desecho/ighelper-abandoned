InstagramHelper
==========================================================

|Build Status| |Requirements Status| |Codecov|

The web application on Django_ 2, Vue.js_ 2, Bootstrap_ 4. It allows you to manage your followers. It also allows you to get statistics.

Features:

- See how many photos & videos your followers liked
- Mark followers as approved
- Get total number of:
    - photos
    - videos
    - followers
    - likes

Installation instructions
----------------------------

1. Use ansible-playbook-server_ to deploy.
2. Do git clone.

Development
--------------

| Use ``clean.sh`` to automatically prettify your code.
| Use ``tox`` for testing and linting.

.. |Requirements Status| image:: https://requires.io/github/desecho/ighelper/requirements.svg?branch=master
   :target: https://requires.io/github/desecho/ighelper/requirements/?branch=master

.. |Codecov| image:: https://codecov.io/gh/desecho/ighelper/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/desecho/ighelper

.. |Build Status| image:: https://travis-ci.org/desecho/ighelper.svg?branch=master
   :target: https://travis-ci.org/desecho/ighelper

.. _ansible-playbook-server: https://github.com/desecho/ansible-playbook-server
.. _Vue.js: https://vuejs.org/
.. _Bootstrap: https://getbootstrap.com/
.. _Django: https://www.djangoproject.com/
