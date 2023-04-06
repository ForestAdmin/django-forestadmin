## [1.4.8](https://github.com/ForestAdmin/django-forest/compare/v1.4.7...v1.4.8) (2023-04-06)


### Bug Fixes

* **stats:** users should be able to use related field in group by aggregation ([#129](https://github.com/ForestAdmin/django-forest/issues/129)) ([2699e31](https://github.com/ForestAdmin/django-forest/commit/2699e3101cef9cdc3837fc1820befeca3fc03e25))

## [1.4.7](https://github.com/ForestAdmin/django-forest/compare/v1.4.6...v1.4.7) (2023-04-05)


### Bug Fixes

* **filters:** nested aggregator weren't implemented ([#128](https://github.com/ForestAdmin/django-forest/issues/128)) ([4361849](https://github.com/ForestAdmin/django-forest/commit/4361849982530f34d30354a35644bc229bb279e4))

## [1.4.6](https://github.com/ForestAdmin/django-forest/compare/v1.4.5...v1.4.6) (2023-03-22)


### Bug Fixes

* **smart-relationship:** smart relationships are now correctly serialized ([#126](https://github.com/ForestAdmin/django-forest/issues/126)) ([7092cbb](https://github.com/ForestAdmin/django-forest/commit/7092cbb63933666b8c36a03f3871575e26f8cb0a))

## [1.4.5](https://github.com/ForestAdmin/django-forest/compare/v1.4.4...v1.4.5) (2023-02-28)

## [1.4.4](https://github.com/ForestAdmin/django-forest/compare/v1.4.3...v1.4.4) (2023-01-05)


### Bug Fixes

* **csv:** prevent error with model without id attribute ([#123](https://github.com/ForestAdmin/django-forest/issues/123)) ([66315d9](https://github.com/ForestAdmin/django-forest/commit/66315d9d2565420a659f88222a2471081f578379))

## [1.4.3](https://github.com/ForestAdmin/django-forest/compare/v1.4.2...v1.4.3) (2022-12-15)


### Bug Fixes

* **schema:** is_primary_key was missing in the jsonapi schema ([#122](https://github.com/ForestAdmin/django-forest/issues/122)) ([94ed592](https://github.com/ForestAdmin/django-forest/commit/94ed592eb51e18f1295228d0ecf0b76d4f511862))

## [1.4.2](https://github.com/ForestAdmin/django-forest/compare/v1.4.1...v1.4.2) (2022-09-15)


### Bug Fixes

* **filters:** date and dateonly fields should be cast to avoid issues in filters ([#121](https://github.com/ForestAdmin/django-forest/issues/121)) ([e5fd115](https://github.com/ForestAdmin/django-forest/commit/e5fd1151dd27b4e5652302a6a5f6b6d59d800afb))

## [1.4.1](https://github.com/ForestAdmin/django-forest/compare/v1.4.0...v1.4.1) (2022-09-14)


### Bug Fixes

* **chart:** disables the permission middleware for the chart's resources and some roles ([#120](https://github.com/ForestAdmin/django-forest/issues/120)) ([903c87a](https://github.com/ForestAdmin/django-forest/commit/903c87a9fef22ee9c85b09ad4c06d70d7074a00a))

# [1.4.0](https://github.com/ForestAdmin/django-forest/compare/v1.3.8...v1.4.0) (2022-09-14)


### Features

* **auth:** remove the APPLICATION_URL parameter ([#119](https://github.com/ForestAdmin/django-forest/issues/119)) ([e2ebd2d](https://github.com/ForestAdmin/django-forest/commit/e2ebd2d3138e02dad74bcab22b978f51d03102aa))

## [1.3.8](https://github.com/ForestAdmin/django-forest/compare/v1.3.7...v1.3.8) (2022-08-31)


### Bug Fixes

* **issue-117:** resolve issue where action name was not being respected for hooks ([#118](https://github.com/ForestAdmin/django-forest/issues/118)) ([403893a](https://github.com/ForestAdmin/django-forest/commit/403893ae82bcea3d94c3eba888b86fa60c2eacf0))

## [1.3.7](https://github.com/ForestAdmin/django-forest/compare/v1.3.6...v1.3.7) (2022-08-31)


### Bug Fixes

* **issue-115:** smart fields always calculated ([9ba8f15](https://github.com/ForestAdmin/django-forest/commit/9ba8f15d230deaf5f9082e1027543ddf1c5be0e3))

## [1.3.6](https://github.com/ForestAdmin/django-forest/compare/v1.3.5...v1.3.6) (2022-08-23)


### Bug Fixes

* **csv:** pagination should be ignored ([#111](https://github.com/ForestAdmin/django-forest/issues/111)) ([f190464](https://github.com/ForestAdmin/django-forest/commit/f19046492854e10417ac1ae0bae242178a0dc182))

## [1.3.5](https://github.com/ForestAdmin/django-forest/compare/v1.3.4...v1.3.5) (2022-08-09)


### Bug Fixes

* **field_type:** dateonly field type should not be in camel case ([#113](https://github.com/ForestAdmin/django-forest/issues/113)) ([8b17380](https://github.com/ForestAdmin/django-forest/commit/8b17380669052506865c58d7f4c802b01a583831))

## [1.3.4](https://github.com/ForestAdmin/django-forest/compare/v1.3.3...v1.3.4) (2022-08-02)


### Bug Fixes

* **csv:** prevent error with model without id attr ([#112](https://github.com/ForestAdmin/django-forest/issues/112)) ([70400e5](https://github.com/ForestAdmin/django-forest/commit/70400e5199e538937b17e0fce118d97dea70f557))

## [1.3.3](https://github.com/ForestAdmin/django-forest/compare/v1.3.2...v1.3.3) (2022-07-11)


### Bug Fixes

* **authentication:** add skew to id_token iat verification ([#109](https://github.com/ForestAdmin/django-forest/issues/109)) ([fef0774](https://github.com/ForestAdmin/django-forest/commit/fef0774b6689cfd4b4af3859aaa57da5ca57f00a))

## [1.3.2](https://github.com/ForestAdmin/django-forest/compare/v1.3.1...v1.3.2) (2022-05-18)


### Bug Fixes

* **authentication:** the jwt token expiration timestamp is based now … ([#107](https://github.com/ForestAdmin/django-forest/issues/107)) ([d8107c0](https://github.com/ForestAdmin/django-forest/commit/d8107c0aa4c88b7efc3bf104a35daf373af9cc3d))

## [1.3.1](https://github.com/ForestAdmin/django-forest/compare/v1.3.0...v1.3.1) (2022-05-13)


### Bug Fixes

* **403_error:** add some content about the reason of the 403 raising ([#106](https://github.com/ForestAdmin/django-forest/issues/106)) ([63a3ae1](https://github.com/ForestAdmin/django-forest/commit/63a3ae1d34acf4976920ece4c15e5c4c90ea964c))

# [1.3.0](https://github.com/ForestAdmin/django-forest/compare/v1.2.2...v1.3.0) (2022-05-05)


### Features

* **cors:** add the pna preflight headers to handle the last chrome versions ([#103](https://github.com/ForestAdmin/django-forest/issues/103)) ([9e458f4](https://github.com/ForestAdmin/django-forest/commit/9e458f401a76e9e81904df5bfeabdcb479c866bd))

## [1.2.2](https://github.com/ForestAdmin/django-forest/compare/v1.2.1...v1.2.2) (2022-04-19)


### Bug Fixes

* **resource:** the filter behavior must be insensitive ([#102](https://github.com/ForestAdmin/django-forest/issues/102)) ([432ed82](https://github.com/ForestAdmin/django-forest/commit/432ed82b2c4dd383aed56525dd4178233ced42bb))

## [1.2.1](https://github.com/ForestAdmin/django-forest/compare/v1.2.0...v1.2.1) (2022-04-19)


### Bug Fixes

* **resource:** the search behavior must be insensitive ([#101](https://github.com/ForestAdmin/django-forest/issues/101)) ([cc0c480](https://github.com/ForestAdmin/django-forest/commit/cc0c4805d27fb6f35e1fbc7dda1176a909c443bd))

# [1.2.0](https://github.com/ForestAdmin/django-forest/compare/v1.1.6...v1.2.0) (2022-04-01)


### Features

* **middleware:** add a middleware and some settings to deactive the count resources ([#99](https://github.com/ForestAdmin/django-forest/issues/99)) ([eb3b2e8](https://github.com/ForestAdmin/django-forest/commit/eb3b2e892c19ddb84e0f51f246e417a6b074e9a7))

## [1.1.6](https://github.com/ForestAdmin/django-forest/compare/v1.1.5...v1.1.6) (2022-03-29)


### Bug Fixes

* **jsonapi:** the value are now cast to the good type ([#98](https://github.com/ForestAdmin/django-forest/issues/98)) ([5010a02](https://github.com/ForestAdmin/django-forest/commit/5010a028ad5cb5cf5afabd36f923784cbba9c7bc))

## [1.1.5](https://github.com/ForestAdmin/django-forest/compare/v1.1.4...v1.1.5) (2022-03-29)


### Bug Fixes

* **onboarding:** won't raised error with custom field ([#97](https://github.com/ForestAdmin/django-forest/issues/97)) ([8c0fbc8](https://github.com/ForestAdmin/django-forest/commit/8c0fbc83383fb3913c8c77893f5383b522855a2e))

## [1.1.4](https://github.com/ForestAdmin/django-forest/compare/v1.1.3...v1.1.4) (2022-03-14)


### Bug Fixes

* **authentication:** add some logs in the authentication process ([#96](https://github.com/ForestAdmin/django-forest/issues/96)) ([a71c1fd](https://github.com/ForestAdmin/django-forest/commit/a71c1fd4accdada7fccb66d26a03898fc2b505e4))

## [1.1.3](https://github.com/ForestAdmin/django-forest/compare/v1.1.2...v1.1.3) (2022-03-14)


### Bug Fixes

* **authentication:** authentication won't fail without trace ([#95](https://github.com/ForestAdmin/django-forest/issues/95)) ([7e577b2](https://github.com/ForestAdmin/django-forest/commit/7e577b2fc05ffc49be8776ebc2c1216e82b9cb5c))

## [1.1.2](https://github.com/ForestAdmin/django-forest/compare/v1.1.1...v1.1.2) (2022-03-02)


### Bug Fixes

* **onboarding:** the settings 'middleware' and 'installed_apps' should be lists ([#93](https://github.com/ForestAdmin/django-forest/issues/93)) ([2570a7a](https://github.com/ForestAdmin/django-forest/commit/2570a7ad863ae839bc529e31be1948ce6fc2662f))

## [1.1.1](https://github.com/ForestAdmin/django-forest/compare/v1.1.0...v1.1.1) (2022-02-28)


### Bug Fixes

* **field:** the enum field raised an exception with Django custom field ([#92](https://github.com/ForestAdmin/django-forest/issues/92)) ([b94eb96](https://github.com/ForestAdmin/django-forest/commit/b94eb961fa0c81e0301504c7c7d1a851c0190180))

# [1.1.0](https://github.com/ForestAdmin/django-forest/compare/v1.0.19...v1.1.0) (2022-02-18)


### Features

* **django:** update the requirements.txt, the tox.py and the github actions to handle django 4 and python 3.10 ([#90](https://github.com/ForestAdmin/django-forest/issues/90)) ([661e976](https://github.com/ForestAdmin/django-forest/commit/661e97660ab01167b9a1c74ec1482f83e5983ffc))

## [1.0.19](https://github.com/ForestAdmin/django-forest/compare/v1.0.18...v1.0.19) (2022-02-11)


### Bug Fixes

* **apimap:** apimap init crashed the agent with some kinds of validators ([#89](https://github.com/ForestAdmin/django-forest/issues/89)) ([b32a5ff](https://github.com/ForestAdmin/django-forest/commit/b32a5ff21b749431f6b6e8b81e7b5ddad66c0d41))

## [1.0.18](https://github.com/ForestAdmin/django-forest/compare/v1.0.17...v1.0.18) (2022-02-11)


### Bug Fixes

* **serializer:** the jsonfield's serializing returned an error ([#88](https://github.com/ForestAdmin/django-forest/issues/88)) ([737f0c0](https://github.com/ForestAdmin/django-forest/commit/737f0c00e18855ce57b08da761d64126191f0b6b))

## [1.0.17](https://github.com/ForestAdmin/django-forest/compare/v1.0.16...v1.0.17) (2022-02-10)


### Bug Fixes

* **dashboard:** use a related field as group_by value in chart was broken ([#87](https://github.com/ForestAdmin/django-forest/issues/87)) ([2795ae6](https://github.com/ForestAdmin/django-forest/commit/2795ae6d7a68eee509a5b16879e8a080f6807f72))

## [1.0.16](https://github.com/ForestAdmin/django-forest/compare/v1.0.15...v1.0.16) (2022-02-10)


### Bug Fixes

* **jsonapiserializer:** fix and refactor the jsonapiserializer ([#83](https://github.com/ForestAdmin/django-forest/issues/83)) ([2284070](https://github.com/ForestAdmin/django-forest/commit/2284070121131aaad716d95e3cbbc9f8541e469c))

## [1.0.15](https://github.com/ForestAdmin/django-forest/compare/v1.0.14...v1.0.15) (2022-02-10)


### Bug Fixes

* **permissions:** user_id in token is a string whereas user_id lists in permissions fetch are string ([#86](https://github.com/ForestAdmin/django-forest/issues/86)) ([9852365](https://github.com/ForestAdmin/django-forest/commit/9852365e13c45c4401defd64c8bda4ba68cb63e1))

## [1.0.14](https://github.com/ForestAdmin/django-forest/compare/v1.0.13...v1.0.14) (2022-02-10)


### Bug Fixes

* **onboarding:** the env variable should be override django settings ([#85](https://github.com/ForestAdmin/django-forest/issues/85)) ([eeb8305](https://github.com/ForestAdmin/django-forest/commit/eeb8305d37aca9eeae3c254fa173c84c249d438e))

## [1.0.13](https://github.com/ForestAdmin/django-forest/compare/v1.0.12...v1.0.13) (2022-02-09)


### Bug Fixes

* **onboarding:** add an utils to init the agent ([#84](https://github.com/ForestAdmin/django-forest/issues/84)) ([9f53e17](https://github.com/ForestAdmin/django-forest/commit/9f53e1731a82f1bb9507e9cbf2e53d31e2993738))

## [1.0.12](https://github.com/ForestAdmin/django-forest/compare/v1.0.11...v1.0.12) (2022-02-03)


### Bug Fixes

* **jsonapischema:** fix issue with the primary key in jsonapi schema ([#82](https://github.com/ForestAdmin/django-forest/issues/82)) ([d54aefa](https://github.com/ForestAdmin/django-forest/commit/d54aefa077a89a8e14f7aae313a4cb10fd3759ac))

## [1.0.11](https://github.com/ForestAdmin/django-forest/compare/v1.0.10...v1.0.11) (2022-02-03)


### Bug Fixes

* **date:** fix and refactor the date uses ([#78](https://github.com/ForestAdmin/django-forest/issues/78)) ([50d0503](https://github.com/ForestAdmin/django-forest/commit/50d05034a944ee9cf9e03abffb319013fc5e00f0))

## [1.0.10](https://github.com/ForestAdmin/django-forest/compare/v1.0.9...v1.0.10) (2022-02-02)


### Bug Fixes

* **apimap:** fix the way to retrieve the related field name and the internal type ([#81](https://github.com/ForestAdmin/django-forest/issues/81)) ([505729c](https://github.com/ForestAdmin/django-forest/commit/505729c14d954d028f4da2c9f54141047ccd6c51))

## [1.0.9](https://github.com/ForestAdmin/django-forest/compare/v1.0.8...v1.0.9) (2022-02-01)


### Bug Fixes

* **cors:** allow_crential is mandatory ([#80](https://github.com/ForestAdmin/django-forest/issues/80)) ([f69193a](https://github.com/ForestAdmin/django-forest/commit/f69193abae9e68e939ed09aa6f0a241afb889b22))

## [1.0.8](https://github.com/ForestAdmin/django-forest/compare/v1.0.7...v1.0.8) (2022-01-25)


### Bug Fixes

* **onboarding:** improve the cors settings to allow more onboarding ([#77](https://github.com/ForestAdmin/django-forest/issues/77)) ([3b96749](https://github.com/ForestAdmin/django-forest/commit/3b967495040f7a01091dd62e191ed7dd6d250498))

## [1.0.7](https://github.com/ForestAdmin/django-forest/compare/v1.0.6...v1.0.7) (2022-01-20)


### Bug Fixes

* **onboarding:** avoid issues if our required packages change their dependencies ([#76](https://github.com/ForestAdmin/django-forest/issues/76)) ([5e11eb8](https://github.com/ForestAdmin/django-forest/commit/5e11eb81c93501b614880bbefe479a64a43c7e86))

## [1.0.6](https://github.com/ForestAdmin/django-forest/compare/v1.0.5...v1.0.6) (2022-01-20)


### Bug Fixes

* **onboarding:** make it possible to install the agent in more projects ([#75](https://github.com/ForestAdmin/django-forest/issues/75)) ([9c04647](https://github.com/ForestAdmin/django-forest/commit/9c04647e237c161ab94de981aeddc6452f1cf30d))

## [1.0.5](https://github.com/ForestAdmin/django-forest/compare/v1.0.4...v1.0.5) (2021-08-20)


### Bug Fixes

* fix stats permissions ([#63](https://github.com/ForestAdmin/django-forest/issues/63)) ([70ebca7](https://github.com/ForestAdmin/django-forest/commit/70ebca731710cc100f3f09f42dfc8402325fe4d0))

## [1.0.4](https://github.com/ForestAdmin/django-forest/compare/v1.0.3...v1.0.4) (2021-08-20)


### Bug Fixes

* fix get ids from request with smart action ([#62](https://github.com/ForestAdmin/django-forest/issues/62)) ([29ffbd4](https://github.com/ForestAdmin/django-forest/commit/29ffbd41d8135f584d99c10093c2c7a4ece31143))

## [1.0.3](https://github.com/ForestAdmin/django-forest/compare/v1.0.2...v1.0.3) (2021-08-13)


### Bug Fixes

* fix update one to one after new permission middleware ([#61](https://github.com/ForestAdmin/django-forest/issues/61)) ([d0c91a1](https://github.com/ForestAdmin/django-forest/commit/d0c91a1ca8dea94ad6f62bc781392b0990e540fe))

## [1.0.2](https://github.com/ForestAdmin/django-forest/compare/v1.0.1...v1.0.2) (2021-08-13)


### Bug Fixes

* correctly set version for schema ([#60](https://github.com/ForestAdmin/django-forest/issues/60)) ([f1a33e7](https://github.com/ForestAdmin/django-forest/commit/f1a33e7c33d6c911bde294d3758166e779020ed2))

## [1.0.1](https://github.com/ForestAdmin/django-forest/compare/v1.0.0...v1.0.1) (2021-08-13)


### Bug Fixes

* add missing actions package in final release + use django-forestadmin as agent name ([#58](https://github.com/ForestAdmin/django-forest/issues/58)) ([5c5f7aa](https://github.com/ForestAdmin/django-forest/commit/5c5f7aaac25e6569a9885ddb79767dfe55dd1b0e))

# 1.0.0 (2021-08-13)


### Bug Fixes

* fix setup.cfg ([#28](https://github.com/ForestAdmin/django-forest/issues/28)) ([44f8437](https://github.com/ForestAdmin/django-forest/commit/44f84374795679579caf2d6badefdbd0aed8e7eb))


### Features

* publish on pypi test repository ([#27](https://github.com/ForestAdmin/django-forest/issues/27)) ([2e1b42b](https://github.com/ForestAdmin/django-forest/commit/2e1b42bf93d60a2b96d7765fb3746026e1e04d5f))
* test resetting version to 0.0.1 ([#30](https://github.com/ForestAdmin/django-forest/issues/30)) ([d586af2](https://github.com/ForestAdmin/django-forest/commit/d586af23847a85a942cb452e92b8c6e262db2bf2))


### Reverts

* Revert "chore: fix semantic release (#18)" (#19) ([4d81ba0](https://github.com/ForestAdmin/django-forest/commit/4d81ba0a9f0fe4493733a81e9b1a22a52adc15d5)), closes [#18](https://github.com/ForestAdmin/django-forest/issues/18) [#19](https://github.com/ForestAdmin/django-forest/issues/19)
* Revert "test: test coverage debug (#14)" (#16) ([3fb5e9e](https://github.com/ForestAdmin/django-forest/commit/3fb5e9ed024cfcf69299525aaee648149c91e0c1)), closes [#14](https://github.com/ForestAdmin/django-forest/issues/14) [#16](https://github.com/ForestAdmin/django-forest/issues/16)
