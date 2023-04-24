# web GUI for managing docker compose project dev

generate graph for docker-compose

______________________________________________________________________

## Table Of Content

<!--TOC-->

- [web GUI for managing docker compose project dev](#web-gui-for-managing-docker-compose-project-dev)
  - [Table Of Content](#table-of-content)
  - [TO FIX](#to-fix)
  - [TODO](#todo)
    - [WEbUI](#webui)
  - [Makefile](#makefile)

<!--TOC-->

## TO FIX

## TODO

### WEbUI

- manage project dynamicly from graph
- create/update service from GUI
- export docker compose
  - global
  - splitted by service
  - dev and prod
- launch makefile rules
- add cli/web GUI for services management functionalities from composes files
  - build selected services
  - generate graphs
  - interact with graphs
  - run selected services
  - remove selected services
  - logs access selected services
  - up selected services
  - stats selected services
  - add notification on docker container state modification on project
- add web IDE
- add project overview
- add browser and desktop notificatilons
- add companion IA companion to debug
- possibility to deploy in registries
- git management
- ci-support and management
- make docker desktop extenssion

## Makefile

<!-- START makefile-doc -->

```
$ make help
make[1]: Entering directory '/mnt/d/drive/dev/repos/-perso-/docker-overview-webui'
Hello to the `docker-overview-webui` Makefile
 	make [target] [args]


| Rule                                               | Help                                                         | Usage                                              | dependencies                                                 | Service              |
+====                                                +====                                                          +====                                                +====                                                          +====                  +
| help                                               | display help                                                 |                                                    |                                                              |                      |
| docker-build                                       | build image                                                  |                                                    |                                                              |                      |
| docker-connect-dev                                 | connect-to-dev-server                                        |                                                    |                                                              |                      |
| docker-stop                                        | stop services                                                |                                                    |                                                              |                      |
| docker-up                                          | up service                                                   |                                                    |                                                              |                      |
| docker-up-detach                                   | up service and detach                                        |                                                    |                                                              |                      |
| node-upgradable-package                            | check outdated packages                                      |                                                    |                                                              |                      |
| node-dev-upgradable-package                        | check outdated packages on dev                               |                                                    |                                                              |                      |
| app-build                                          | build application                                            |                                                    |  app-install-deps                                            |                      |
| app-install-deps                                   | install proect dependencies locally                          |                                                    |                                                              |                      |
| app-dev                                            | launch as dev                                                |                                                    |  app-install-deps                                            |                      |
| ci-run-local                                       | run ci pipeline locally                                      |                                                    |                                                              |                      |
| pre-commit                                         | run localy precommit                                         |                                                    |                                                              |                      |
make[1]: Leaving directory '/mnt/d/drive/dev/repos/-perso-/docker-overview-webui'
```

<!-- END makefile-doc -->
