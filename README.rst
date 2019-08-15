====================================
Adam & Paul Buildout Recipies Public
====================================

This is a subtree repository for synchronizing recipies across multiple public
repositories. When modifing code in this folder please take care to:

- Not create commits which mix chnages from thid folder and other parts of the
  repo.

- Keep package specific changes out of this folder.

Adding/Updating Repo a Project
==============================

This repository can be added as a subtree using the subtree git plugin
with the following command::

    git subtree add --squash --prefix buildout/common git@bitbucket.org:adamandpaul/buildout-recipies-pub.git master

Updating a subtree can be done with this command::

    git subtree pull --squash --prefix buildout/common git@bitbucket.org:adamandpaul/buildout-recipies-pub.git master

Pushing changes back to the origin repo of this folder
======================================================

Pushing changes back to the upstream repo::

    git subtree push --prefix buildout/common git@bitbucket.org:adamandpaul/buildout-recipies-pub.git master
