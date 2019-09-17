==================================
Adam & Paul Buildout Common Public
==================================

This is a subtree repository for synchronizing recipies across multiple public
repositories. When modifing code in this folder please take care to:

- Not create commits which mix chnages from thid folder and other parts of the
  repo.

- Keep package specific changes out of this folder.

Initial Project Setup
=====================

Create the ``bin`` and ``buildout`` directories.::

    mkdir -p bin buildout

Add in the ``buildout-common-pub`` repository.::

    git subtree add --squash --prefix buildout/common-pub git@bitbucket.org:adamandpaul/buildout-common-pub.git master

Symbolic link ``bootstrap`` and ``build`` in the bin directories.::

    cd bin
    ln -s ../buildout/common-pub/bootstrap
    ln -s ../buildout/common-pub/build
    cd ..

Create the minimum project level buildout configuration::

    touch buildout/versions.cfg

    # Copy the main template
    cp buildout/common-pub/main.cfg.in buildout/main.cfg

Edit the ``buildout/main.cfg`` as needed.


Updating buildout-common-pub
============================

Updating a subtree can be done with this command::

    git subtree pull --squash --prefix buildout/common-pub git@bitbucket.org:adamandpaul/buildout-common-pub.git master


Pushing changes back to the origin repo of this folder
======================================================

Pushing changes back to the upstream repo::

    git subtree push --prefix buildout/common-pub git@bitbucket.org:adamandpaul/buildout-common-pub.git master
