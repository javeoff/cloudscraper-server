# [1.7.0](https://github.com/javeoff/cloudscraper-server/compare/v1.6.0...v1.7.0) (2025-03-13)


### Bug Fixes

* Add explicit stdout logging and error proxy details in handle_proxy ([d8e4dd3](https://github.com/javeoff/cloudscraper-server/commit/d8e4dd387ccd7777228e2b7bbcc4684e1a1c4d0d))
* Handle BOM characters when loading proxies from file ([093b905](https://github.com/javeoff/cloudscraper-server/commit/093b905a2794484ab8c5e068c9d434de02c89813))
* Handle UTF-8 encoding and BOM characters in proxy response ([4077abb](https://github.com/javeoff/cloudscraper-server/commit/4077abbe7c67d4f1cfe5fb058484f8ff73eca341))
* Remove BOM character causing SyntaxError in server.py ([fdbd593](https://github.com/javeoff/cloudscraper-server/commit/fdbd593d8d9b6245745b38c52a88c627eee3431c))
* Update proxy loading to support login:password@IP:port format ([43d3c2e](https://github.com/javeoff/cloudscraper-server/commit/43d3c2ec5a2adcded835cc52ee79e8c23497b1ca))


### Features

* Add health monitoring and auto-restart mechanism to proxy server ([b55f114](https://github.com/javeoff/cloudscraper-server/commit/b55f1140e52b424ed44ea2da5a5c3ed0239159a2))
* Enhance request diversity and randomization for Cloudflare evasion ([4c582e3](https://github.com/javeoff/cloudscraper-server/commit/4c582e32b78abf882426e04e5382038976f379db))
* Expand browser configuration with more versions, platforms, and request headers ([a70ea97](https://github.com/javeoff/cloudscraper-server/commit/a70ea97450348a1aaefcaf0d92b40a1593bf1411))

# [1.6.0](https://github.com/javeoff/cloudscraper-server/compare/v1.5.0...v1.6.0) (2025-02-22)


### Features

* Enhance Cloudflare header randomization with dynamic Chrome versions and platforms ([09ebd39](https://github.com/javeoff/cloudscraper-server/commit/09ebd391e0666bccf61327c8ef6b5fdb5838f2b6))

# [1.5.0](https://github.com/javeoff/cloudscraper-server/compare/v1.4.0...v1.5.0) (2025-02-18)


### Features

* Enhance proxy request logging with detailed start, status, and error information ([881b14c](https://github.com/javeoff/cloudscraper-server/commit/881b14c6485d37a65591e02fd5c0a1c6ed4234c9))

# [1.4.0](https://github.com/javeoff/cloudscraper-server/compare/v1.3.0...v1.4.0) (2025-02-18)


### Features

* Add HTTP proxy support with dynamic proxy selection ([afb1007](https://github.com/javeoff/cloudscraper-server/commit/afb100778a3da29ec0777e72190070a8e946ce1c))

# [1.3.0](https://github.com/javeoff/cloudscraper-server/compare/v1.2.0...v1.3.0) (2025-02-18)


### Features

* Add automatic http:// protocol detection for proxy URLs ([08b5d36](https://github.com/javeoff/cloudscraper-server/commit/08b5d36881828ef071894eac22fbde99a042fc5a))

# [1.2.0](https://github.com/javeoff/cloudscraper-server/compare/v1.1.0...v1.2.0) (2025-02-18)


### Features

* Add fake-useragent dependency to requirements.txt ([02b02ee](https://github.com/javeoff/cloudscraper-server/commit/02b02eecb54c21e925882e52ddc0dc67f6b3b213))

# 1.0.0 (2025-02-09)


### Features

* Add Makefile with Docker container management commands ([1557166](https://github.com/GhostTypes/cloudscraper-server/commit/155716643e15ba2ab16ed84d7fbe97941444f6d8))
* **docker:** add docker-compose file to simplify application deployment and configuration ([bb79d1a](https://github.com/GhostTypes/cloudscraper-server/commit/bb79d1ad109078c9ac7198a758006161bed8717b))
* **workflows:** add Docker Publish and Release workflows for automated image building and deployment ([112a293](https://github.com/GhostTypes/cloudscraper-server/commit/112a2939eed6c8bc1a18d07f3dbd43fcaa99354a))

# [1.1.0](https://github.com/javeoff/cloudscraper-server/compare/v1.0.0...v1.1.0) (2025-02-08)


### Features

* **docker:** add docker-compose file to simplify application deployment and configuration ([bb79d1a](https://github.com/javeoff/cloudscraper-server/commit/bb79d1ad109078c9ac7198a758006161bed8717b))

# 1.0.0 (2025-02-08)


### Features

* Add Makefile with Docker container management commands ([1557166](https://github.com/javeoff/cloudscraper-server/commit/155716643e15ba2ab16ed84d7fbe97941444f6d8))
* **workflows:** add Docker Publish and Release workflows for automated image building and deployment ([112a293](https://github.com/javeoff/cloudscraper-server/commit/112a2939eed6c8bc1a18d07f3dbd43fcaa99354a))
